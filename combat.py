# combat.py
import random
from typing import Dict
from constants import WeaponType, WEAPON_TRIANGLE
from skills import SkillTriggerType, SkillEffectType

class CombatSystem:
    @staticmethod
    def calculate_hit_chance(attacker, defender, game_map) -> int:
        hit_rate = attacker.get_hit_rate()
        avoid = defender.get_avoid()
        terrain_dodge = game_map.get_terrain_dodge(defender.x, defender.y)
        
        # 武器相性ボーナス
        weapon_bonus = 0
        if attacker.equipped_weapon and defender.equipped_weapon:
            attacker_type = attacker.equipped_weapon.weapon_type
            defender_type = defender.equipped_weapon.weapon_type
            
            if attacker_type in WEAPON_TRIANGLE and defender_type in WEAPON_TRIANGLE[attacker_type]:
                weapon_bonus = WEAPON_TRIANGLE[attacker_type][defender_type] * 15
        
        # スキルによる命中修正
        hit_modifier = 0
        for skill in attacker.active_skills:
            if skill.effect_type == SkillEffectType.HIT_BOOST:
                hit_modifier += skill.effect_value
        
        # 特殊なスキル効果（例: 斧殺し）
        for skill in attacker.active_skills:
            if skill.effect_type == SkillEffectType.SPECIAL_ATTACK:
                if isinstance(skill.effect_value, dict):
                    condition = skill.effect_value.get("condition", "")
                    if "opponent_weapon_type" in condition and defender.equipped_weapon:
                        # 条件を評価
                        weapon_condition = f"WeaponType.{defender.equipped_weapon.weapon_type.name}"
                        if weapon_condition in condition:
                            hit_modifier += skill.effect_value.get("hit_bonus", 0)
        
        # 防御側のスキルによる回避修正
        avoid_modifier = 0
        for skill in defender.active_skills:
            if skill.effect_type == SkillEffectType.AVOID_BOOST:
                avoid_modifier += skill.effect_value
        
        hit_chance = hit_rate + weapon_bonus + hit_modifier - avoid - terrain_dodge - avoid_modifier
        return max(0, min(100, hit_chance))
    
    @staticmethod
    def calculate_damage(attacker, defender, game_map) -> int:
        attack_power = attacker.get_attack_power()
        is_magic = attacker.equipped_weapon and attacker.equipped_weapon.weapon_type == WeaponType.MAGIC
        
        defense_stat = defender.resistance if is_magic else defender.defense
        terrain_defense = game_map.get_terrain_defense(defender.x, defender.y)
        
        # 武器相性ボーナス
        weapon_bonus = 0
        if attacker.equipped_weapon and defender.equipped_weapon:
            attacker_type = attacker.equipped_weapon.weapon_type
            defender_type = defender.equipped_weapon.weapon_type
            
            if attacker_type in WEAPON_TRIANGLE and defender_type in WEAPON_TRIANGLE[attacker_type]:
                weapon_bonus = WEAPON_TRIANGLE[attacker_type][defender_type] * 1
        
        # スキルによるダメージ修正
        damage_modifier = 0
        for skill in attacker.active_skills:
            if skill.effect_type == SkillEffectType.DAMAGE_BOOST:
                damage_modifier += skill.effect_value
        
        # 防御側のスキルによるダメージ減少
        damage_reduction = 0
        for skill in defender.active_skills:
            if skill.effect_type == SkillEffectType.DAMAGE_REDUCE:
                if isinstance(skill.effect_value, float):
                    # 割合によるダメージ減少
                    damage_reduction += int((attack_power - defense_stat) * skill.effect_value)
                else:
                    # 固定値によるダメージ減少
                    damage_reduction += skill.effect_value
        
        # 特殊なスキル効果（例: 月光）
        for skill in attacker.active_skills:
            if skill.effect_type == SkillEffectType.SPECIAL_ATTACK:
                if isinstance(skill.effect_value, dict) and "defense_pierce" in skill.effect_value:
                    pierce_amount = int(defense_stat * skill.effect_value["defense_pierce"])
                    damage_modifier += pierce_amount
        
        damage = attack_power + weapon_bonus + damage_modifier - defense_stat - terrain_defense - damage_reduction
        return max(0, damage)
    
    @staticmethod
    def calculate_crit_chance(attacker, defender) -> int:
        crit_rate = attacker.get_critical_rate()
        crit_avoid = defender.luck
        
        # スキルによるクリティカル修正
        crit_modifier = 0
        for skill in attacker.active_skills:
            if skill.effect_type == SkillEffectType.CRITICAL_BOOST:
                crit_modifier += skill.effect_value
        
        crit_chance = crit_rate + crit_modifier - crit_avoid
        return max(0, min(100, crit_chance))
    
    @staticmethod
    def perform_attack(attacker, defender, game_map) -> Dict:
        # スキルの発動チェック（攻撃時）
        combat_data = {
            "attacker": attacker,
            "defender": defender,
            "is_attacker": True,
            "target": defender,
            "game_map": game_map
        }
        
        attacker.activate_skills(SkillTriggerType.ON_ATTACK, combat_data)
        defender.activate_skills(SkillTriggerType.ON_DEFEND, combat_data)
        
        # スキルを考慮した計算
        hit_chance = CombatSystem.calculate_hit_chance(attacker, defender, game_map)
        damage = CombatSystem.calculate_damage(attacker, defender, game_map)
        crit_chance = CombatSystem.calculate_crit_chance(attacker, defender)
        
        # 命中判定
        hit_roll = random.randint(1, 100)
        hit = hit_roll <= hit_chance
        
        # クリティカル判定
        crit_roll = random.randint(1, 100)
        crit = hit and crit_roll <= crit_chance
        
        # 連続攻撃スキルの処理
        multi_attack = False
        attack_count = 1
        damage_multiplier = 1.0
        
        for skill in attacker.active_skills:
            if skill.effect_type == SkillEffectType.SPECIAL_ATTACK:
                if isinstance(skill.effect_value, dict) and "attacks" in skill.effect_value:
                    multi_attack = True
                    attack_count = skill.effect_value.get("attacks", 1)
                    damage_multiplier = skill.effect_value.get("damage_multiplier", 1.0)
        
        # ダメージ計算と適用
        if hit:
            total_damage = 0
            
            if multi_attack:
                # 連続攻撃の処理
                for i in range(attack_count):
                    attack_damage = int(damage * damage_multiplier)
                    if i == 0 and crit:
                        attack_damage *= 3
                    defender.current_hp = max(0, defender.current_hp - attack_damage)
                    total_damage += attack_damage
                    if defender.is_dead():
                        break
            else:
                # 通常攻撃
                attack_damage = damage * 3 if crit else damage
                defender.current_hp = max(0, defender.current_hp - attack_damage)
                total_damage = attack_damage
                
            # 攻撃後の回復スキル処理
            for skill in attacker.active_skills:
                if skill.effect_type == SkillEffectType.HEAL:
                    if isinstance(skill.effect_value, dict) and "heal_ratio" in skill.effect_value:
                        heal_amount = int(total_damage * skill.effect_value["heal_ratio"])
                        attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal_amount)
            
            # 武器の耐久度を減らす
            if attacker.equipped_weapon:
                attacker.equipped_weapon.durability -= 1
        
        # 戦闘結果の作成
        result = {
            "hit": hit,
            "damage": total_damage if hit else 0,
            "critical": crit,
            "killed": defender.is_dead(),
            "hit_chance": hit_chance,
            "crit_chance": crit_chance,
            "multi_attack": multi_attack,
            "attack_count": attack_count if multi_attack and hit else 1,
        }
        
        # 戦闘結果に基づいたスキルの発動
        if hit and total_damage > 0:
            combat_data["damage_dealt"] = total_damage
            attacker.activate_skills(SkillTriggerType.ON_DAMAGE, combat_data)
        
        if defender.is_dead():
            combat_data["target_killed"] = True
            attacker.activate_skills(SkillTriggerType.ON_KILL, combat_data)
        
        return result
    
    @staticmethod
    def perform_combat(attacker, defender, game_map) -> Dict:
        """スキルを考慮した戦闘処理"""
        # 戦闘前のスキル処理
        pre_combat_data = {
            "attacker": attacker,
            "defender": defender,
            "is_attacker": True,
            "target": defender,
            "game_map": game_map
        }
        
        defender_pre_combat_data = {
            "attacker": defender,
            "defender": attacker,
            "is_attacker": False,
            "target": attacker, 
            "game_map": game_map
        }
        
        # 先制攻撃のスキルをチェック
        attacker_has_vantage = False
        defender_has_vantage = False
        
        for skill in attacker.skills:
            if (skill.trigger_type == SkillTriggerType.HP_THRESHOLD and 
                skill.effect_type == SkillEffectType.SPECIAL_ATTACK):
                if skill.check_trigger(attacker, pre_combat_data):
                    effect_value = skill.effect_value
                    if isinstance(effect_value, dict) and effect_value.get("vantage", False):
                        attacker_has_vantage = True
        
        for skill in defender.skills:
            if (skill.trigger_type == SkillTriggerType.HP_THRESHOLD and 
                skill.effect_type == SkillEffectType.SPECIAL_ATTACK):
                if skill.check_trigger(defender, defender_pre_combat_data):
                    effect_value = skill.effect_value
                    if isinstance(effect_value, dict) and effect_value.get("vantage", False):
                        defender_has_vantage = True
        
        # 戦闘順序の決定（先制攻撃スキルを考慮）
        if defender_has_vantage and not attacker_has_vantage:
            # 防御側が先制
            temp_attacker = defender
            temp_defender = attacker
            swap_roles = True
        else:
            # 通常の攻撃順序
            temp_attacker = attacker
            temp_defender = defender
            swap_roles = False
            
        # 戦闘開始前のスキル発動
        attacker.activate_skills(SkillTriggerType.PRE_COMBAT, pre_combat_data)
        defender.activate_skills(SkillTriggerType.PRE_COMBAT, defender_pre_combat_data)
        
        results = {
            "attacker_results": [],
            "defender_results": [],
            "attacker_unit": attacker,
            "defender_unit": defender
        }
        
        # 攻撃側の攻撃
        attacker_result = CombatSystem.perform_attack(temp_attacker, temp_defender, game_map)
        if swap_roles:
            results["defender_results"].append(attacker_result)
        else:
            results["attacker_results"].append(attacker_result)
        
        # 防御側が死亡した場合、戦闘終了
        if temp_defender.is_dead():
            if swap_roles:
                # 役割が逆転している場合、結果も入れ替える
                temp_results = results["attacker_results"]
                results["attacker_results"] = results["defender_results"]
                results["defender_results"] = temp_results
            
            # 戦闘後のスキル処理
            post_combat_data = {
                "attacker": attacker,
                "defender": defender,
                "results": results,
                "damage_dealt": sum(r.get("damage", 0) for r in results["attacker_results"]),
                "damage_received": 0,
                "target_killed": defender.is_dead(),
                "is_attacker": True,
            }
            
            defender_post_combat_data = {
                "attacker": defender,
                "defender": attacker,
                "results": results,
                "damage_dealt": 0,
                "damage_received": sum(r.get("damage", 0) for r in results["attacker_results"]),
                "target_killed": False,
                "is_attacker": False,
            }
            
            attacker.activate_skills(SkillTriggerType.POST_COMBAT, post_combat_data)
            defender.activate_skills(SkillTriggerType.POST_COMBAT, defender_post_combat_data)
            
            # 戦闘中に発動したスキルを結果に追加
            results["activated_skills"] = {
                "attacker": [skill.name for skill in attacker.active_skills],
                "defender": [skill.name for skill in defender.active_skills]
            }
            
            # スキルをリセット
            attacker.deactivate_skills()
            defender.deactivate_skills()
            
            return results
        
        # 防御側の反撃（射程内の場合）
        counter_range_check = temp_defender.equipped_weapon and temp_defender.equipped_weapon.range_min <= abs(temp_attacker.x - temp_defender.x) + abs(temp_attacker.y - temp_defender.y) <= temp_defender.equipped_weapon.range_max
        guaranteed_counter = False
        
        # 特殊なスキル効果（反撃保証）
        for skill in temp_defender.active_skills:
            if skill.effect_type == SkillEffectType.COUNTER_ATTACK:
                guaranteed_counter = True
                break
        
        can_counter = counter_range_check or guaranteed_counter
        
        if can_counter:
            defender_result = CombatSystem.perform_attack(temp_defender, temp_attacker, game_map)
            if swap_roles:
                results["attacker_results"].append(defender_result)
            else:
                results["defender_results"].append(defender_result)
            
            # 攻撃側が死亡した場合、戦闘終了
            if temp_attacker.is_dead():
                if swap_roles:
                    # 役割が逆転している場合、結果も入れ替える
                    temp_results = results["attacker_results"]
                    results["attacker_results"] = results["defender_results"]
                    results["defender_results"] = temp_results
                
                # 戦闘後のスキル処理
                post_combat_data = {
                    "attacker": attacker,
                    "defender": defender,
                    "results": results,
                    "damage_dealt": sum(r.get("damage", 0) for r in results["attacker_results"]),
                    "damage_received": sum(r.get("damage", 0) for r in results["defender_results"]),
                    "target_killed": defender.is_dead(),
                    "is_attacker": True,
                }
                
                defender_post_combat_data = {
                    "attacker": defender,
                    "defender": attacker,
                    "results": results,
                    "damage_dealt": sum(r.get("damage", 0) for r in results["defender_results"]),
                    "damage_received": sum(r.get("damage", 0) for r in results["attacker_results"]),
                    "target_killed": attacker.is_dead(),
                    "is_attacker": False,
                }
                
                attacker.activate_skills(SkillTriggerType.POST_COMBAT, post_combat_data)
                defender.activate_skills(SkillTriggerType.POST_COMBAT, defender_post_combat_data)
                
                # 戦闘中に発動したスキルを結果に追加
                results["activated_skills"] = {
                    "attacker": [skill.name for skill in attacker.active_skills],
                    "defender": [skill.name for skill in defender.active_skills]
                }
                
                # スキルをリセット
                attacker.deactivate_skills()
                defender.deactivate_skills()
                
                return results
        
        # 追撃（速度差が4以上ある場合）
        guaranteed_follow_up_attacker = False
        guaranteed_follow_up_defender = False
        
        # 特殊なスキル効果（追撃保証）
        for skill in temp_attacker.active_skills:
            if skill.effect_type == SkillEffectType.FOLLOW_UP:
                guaranteed_follow_up_attacker = True
                break
                
        for skill in temp_defender.active_skills:
            if skill.effect_type == SkillEffectType.FOLLOW_UP:
                guaranteed_follow_up_defender = True
                break
        
        if temp_attacker.can_double_attack(temp_defender) or guaranteed_follow_up_attacker:
            attacker_result2 = CombatSystem.perform_attack(temp_attacker, temp_defender, game_map)
            if swap_roles:
                results["defender_results"].append(attacker_result2)
            else:
                results["attacker_results"].append(attacker_result2)
                
            # 防御側が死亡した場合、戦闘終了
            if temp_defender.is_dead():
                if swap_roles:
                    # 役割が逆転している場合、結果も入れ替える
                    temp_results = results["attacker_results"]
                    results["attacker_results"] = results["defender_results"]
                    results["defender_results"] = temp_results
                
                # 戦闘後のスキル処理
                post_combat_data = {
                    "attacker": attacker,
                    "defender": defender,
                    "results": results,
                    "damage_dealt": sum(r.get("damage", 0) for r in results["attacker_results"]),
                    "damage_received": sum(r.get("damage", 0) for r in results["defender_results"]),
                    "target_killed": defender.is_dead(),
                    "is_attacker": True,
                }
                
                defender_post_combat_data = {
                    "attacker": defender,
                    "defender": attacker,
                    "results": results,
                    "damage_dealt": sum(r.get("damage", 0) for r in results["defender_results"]),
                    "damage_received": sum(r.get("damage", 0) for r in results["attacker_results"]),
                    "target_killed": False,
                    "is_attacker": False,
                }
                
                attacker.activate_skills(SkillTriggerType.POST_COMBAT, post_combat_data)
                defender.activate_skills(SkillTriggerType.POST_COMBAT, defender_post_combat_data)
                
                # 戦闘中に発動したスキルを結果に追加
                results["activated_skills"] = {
                    "attacker": [skill.name for skill in attacker.active_skills],
                    "defender": [skill.name for skill in defender.active_skills]
                }
                
                # スキルをリセット
                attacker.deactivate_skills()
                defender.deactivate_skills()
                
                return results
        
        elif can_counter and (temp_defender.can_double_attack(temp_attacker) or guaranteed_follow_up_defender):
            defender_result2 = CombatSystem.perform_attack(temp_defender, temp_attacker, game_map)
            if swap_roles:
                results["attacker_results"].append(defender_result2)
            else:
                results["defender_results"].append(defender_result2)
                
            # 攻撃側が死亡した場合、戦闘終了
            if temp_attacker.is_dead():
                if swap_roles:
                    # 役割が逆転している場合、結果も入れ替える
                    temp_results = results["attacker_results"]
                    results["attacker_results"] = results["defender_results"]
                    results["defender_results"] = temp_results
                
                # 戦闘後のスキル処理
                post_combat_data = {
                    "attacker": attacker,
                    "defender": defender,
                    "results": results,
                    "damage_dealt": sum(r.get("damage", 0) for r in results["attacker_results"]),
                    "damage_received": sum(r.get("damage", 0) for r in results["defender_results"]),
                    "target_killed": defender.is_dead(),
                    "is_attacker": True,
                }
                
                defender_post_combat_data = {
                    "attacker": defender,
                    "defender": attacker,
                    "results": results,
                    "damage_dealt": sum(r.get("damage", 0) for r in results["defender_results"]),
                    "damage_received": sum(r.get("damage", 0) for r in results["attacker_results"]),
                    "target_killed": attacker.is_dead(),
                    "is_attacker": False,
                }
                
                attacker.activate_skills(SkillTriggerType.POST_COMBAT, post_combat_data)
                defender.activate_skills(SkillTriggerType.POST_COMBAT, defender_post_combat_data)
                
                # 戦闘中に発動したスキルを結果に追加
                results["activated_skills"] = {
                    "attacker": [skill.name for skill in attacker.active_skills],
                    "defender": [skill.name for skill in defender.active_skills]
                }
                
                # スキルをリセット
                attacker.deactivate_skills()
                defender.deactivate_skills()
                
                return results
        
        # 役割が逆転している場合、結果も入れ替える
        if swap_roles:
            temp_results = results["attacker_results"]
            results["attacker_results"] = results["defender_results"]
            results["defender_results"] = temp_results
        
        # 戦闘後のスキル処理
        post_combat_data = {
            "attacker": attacker,
            "defender": defender,
            "results": results,
            "damage_dealt": sum(r.get("damage", 0) for r in results["attacker_results"]),
            "damage_received": sum(r.get("damage", 0) for r in results["defender_results"]),
            "target_killed": defender.is_dead(),
            "is_attacker": True,
        }
        
        defender_post_combat_data = {
            "attacker": defender,
            "defender": attacker,
            "results": results,
            "damage_dealt": sum(r.get("damage", 0) for r in results["defender_results"]),
            "damage_received": sum(r.get("damage", 0) for r in results["attacker_results"]),
            "target_killed": attacker.is_dead(),
            "is_attacker": False,
        }
        
        attacker.activate_skills(SkillTriggerType.POST_COMBAT, post_combat_data)
        defender.activate_skills(SkillTriggerType.POST_COMBAT, defender_post_combat_data)
        
        # 戦闘中に発動したスキルを結果に追加
        results["activated_skills"] = {
            "attacker": [skill.name for skill in attacker.active_skills],
            "defender": [skill.name for skill in defender.active_skills]
        }
        
        # スキルをリセット
        attacker.deactivate_skills()
        defender.deactivate_skills()
        
        return results
    
    @staticmethod
    def perform_capture_attack(attacker, defender, game_map) -> Dict:
        """捕獲目的の攻撃を実行"""
        # 捕獲時のステータス補正を適用
        capture_stats = attacker.get_capture_battle_stats()
        original_skill = attacker.skill
        original_speed = attacker.speed
        
        # 一時的にステータスを変更
        attacker.skill = capture_stats["skill"]
        attacker.speed = capture_stats["speed"]
        
        # 通常の攻撃処理を実行
        result = CombatSystem.perform_attack(attacker, defender, game_map)
        
        # ステータスを元に戻す
        attacker.skill = original_skill
        attacker.speed = original_speed
        
        # 捕獲フラグを追加
        result["capture_attempt"] = True
        
        return result