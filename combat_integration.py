# combat_integration.py
# 既存の戦闘システムに支援効果とレジェンダリーアイテム効果を統合するモジュール

from typing import Dict, List, Tuple, Optional
from combat import CombatSystem
from support_system import SupportSystem
from legendary_items import LegendaryWeapon

class EnhancedCombatSystem(CombatSystem):
    """支援効果とレジェンダリーアイテム効果を統合した拡張戦闘システム"""
    
    @staticmethod
    def calculate_hit_chance(attacker, defender, game_map, support_system=None) -> int:
        """支援効果を考慮した命中率計算"""
        # 基本命中率を計算
        hit_chance = CombatSystem.calculate_hit_chance(attacker, defender, game_map)
        
        # 支援効果を適用
        if support_system:
            attacker_support_bonus = support_system.get_support_bonus(attacker, game_map)
            defender_support_bonus = support_system.get_support_bonus(defender, game_map)
            
            # 命中率ボーナスと回避率ボーナスを適用
            hit_chance = hit_chance + attacker_support_bonus.hit_bonus - defender_support_bonus.avoid_bonus
        
        # レジェンダリー武器の効果を考慮
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            # 武器の効果を適用
            for effect in attacker.equipped_weapon.effects:
                if effect.effect_type == "hit_boost":
                    hit_chance += effect.effect_value.get("value", 0)
        
        return max(0, min(100, hit_chance))
    
    @staticmethod
    def calculate_damage(attacker, defender, game_map, support_system=None) -> int:
        """支援効果を考慮したダメージ計算"""
        # 基本ダメージを計算
        damage = CombatSystem.calculate_damage(attacker, defender, game_map)
        
        # 支援効果を適用
        if support_system:
            attacker_support_bonus = support_system.get_support_bonus(attacker, game_map)
            defender_support_bonus = support_system.get_support_bonus(defender, game_map)
            
            # ダメージボーナスとダメージ軽減を適用
            damage = damage + attacker_support_bonus.damage_bonus - defender_support_bonus.defense_bonus
        
        # レジェンダリー武器の効果を考慮
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            # 武器の効果を適用
            for effect in attacker.equipped_weapon.effects:
                if effect.effect_type == "damage_boost":
                    damage += effect.effect_value.get("value", 0)
        
        if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
            # 防御側の武器効果を適用
            for effect in defender.equipped_weapon.effects:
                if effect.effect_type == "damage_reduce":
                    damage -= effect.effect_value.get("value", 0)
        
        return max(0, damage)
    
    @staticmethod
    def calculate_crit_chance(attacker, defender, support_system=None) -> int:
        """支援効果を考慮したクリティカル率計算"""
        # 基本クリティカル率を計算
        crit_chance = CombatSystem.calculate_crit_chance(attacker, defender)
        
        # レジェンダリー武器の効果を考慮
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            # 武器の効果を適用
            for effect in attacker.equipped_weapon.effects:
                if effect.effect_type == "critical_boost":
                    crit_chance += effect.effect_value.get("value", 0)
        
        return max(0, min(100, crit_chance))
    
    @staticmethod
    def perform_attack(attacker, defender, game_map, support_system=None) -> Dict:
        """支援効果とレジェンダリーアイテム効果を考慮した攻撃処理"""
        # 戦闘データを準備
        combat_data = {
            "attacker": attacker,
            "defender": defender,
            "is_attacker": True,
            "target": defender,
            "game_map": game_map
        }
        
        # 支援効果を適用
        if support_system:
            support_system.apply_support_effects(attacker, defender, combat_data, game_map)
        
        # レジェンダリー武器のスキルを適用
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            # 武器が付与するスキルを取得
            weapon_skills = attacker.equipped_weapon.get_granted_skills()
            
            # 一時的にスキルを追加
            for skill in weapon_skills:
                if skill not in attacker.skills:
                    attacker.add_skill(skill)
        
        # 通常の攻撃処理
        attacker.activate_skills(SkillTriggerType.ON_ATTACK, combat_data)
        defender.activate_skills(SkillTriggerType.ON_DEFEND, combat_data)
        
        # 支援効果とレジェンダリー効果を考慮した戦闘値計算
        hit_chance = EnhancedCombatSystem.calculate_hit_chance(attacker, defender, game_map, support_system)
        damage = EnhancedCombatSystem.calculate_damage(attacker, defender, game_map, support_system)
        crit_chance = EnhancedCombatSystem.calculate_crit_chance(attacker, defender, support_system)
        
        # 命中判定
        hit_roll = random.randint(1, 100)
        hit = hit_roll <= hit_chance
        
        # クリティカル判定
        crit_roll = random.randint(1, 100)
        crit = hit and crit_roll <= crit_chance
        
        # 連続攻撃スキル・効果の処理
        multi_attack = False
        attack_count = 1
        damage_multiplier = 1.0
        
        # スキルによる連続攻撃
        for skill in attacker.active_skills:
            if skill.effect_type == SkillEffectType.SPECIAL_ATTACK:
                if isinstance(skill.effect_value, dict) and "attacks" in skill.effect_value:
                    multi_attack = True
                    attack_count = skill.effect_value.get("attacks", 1)
                    damage_multiplier = skill.effect_value.get("damage_multiplier", 1.0)
        
        # レジェンダリー武器による連続攻撃
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            for effect in attacker.equipped_weapon.effects:
                if effect.effect_type == "special_attack" and isinstance(effect.effect_value, dict) and "attacks" in effect.effect_value:
                    if not multi_attack or effect.effect_value.get("attacks", 1) > attack_count:
                        multi_attack = True
                        attack_count = effect.effect_value.get("attacks", 1)
                        damage_multiplier = effect.effect_value.get("damage_multiplier", 1.0)
        
        # ダメージ計算と適用
        total_damage = 0
        if hit:
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
            
            # レジェンダリー武器による回復効果
            if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
                for effect in attacker.equipped_weapon.effects:
                    if effect.effect_type == "heal" and isinstance(effect.effect_value, dict) and "heal_ratio" in effect.effect_value:
                        heal_amount = int(total_damage * effect.effect_value["heal_ratio"])
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
    def perform_combat(attacker, defender, game_map, support_system=None) -> Dict:
        """支援効果とレジェンダリーアイテム効果を考慮した戦闘処理"""
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
        
        # レジェンダリー武器による先制効果
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            for effect in attacker.equipped_weapon.effects:
                if effect.effect_type == "special_attack" and isinstance(effect.effect_value, dict) and effect.effect_value.get("vantage", False):
                    attacker_has_vantage = True
        
        if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
            for effect in defender.equipped_weapon.effects:
                if effect.effect_type == "special_attack" and isinstance(effect.effect_value, dict) and effect.effect_value.get("vantage", False):
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
        
        # レジェンダリー武器の効果を適用
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            attacker.equipped_weapon.apply_effects(attacker)
        
        if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
            defender.equipped_weapon.apply_effects(defender)
        
        results = {
            "attacker_results": [],
            "defender_results": [],
            "attacker_unit": attacker,
            "defender_unit": defender
        }
        
        # 攻撃側の攻撃
        attacker_result = EnhancedCombatSystem.perform_attack(temp_attacker, temp_defender, game_map, support_system)
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
            
            # レジェンダリー武器の効果を除去
            if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
                attacker.equipped_weapon.remove_effects(attacker)
            
            if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
                defender.equipped_weapon.remove_effects(defender)
            
            # 戦闘中に発動したスキルを結果に追加
            results["activated_skills"] = {
                "attacker": [skill.name for skill in attacker.active_skills],
                "defender": [skill.name for skill in defender.active_skills]
            }
            
            # 支援システムの更新 - 一緒に戦闘した記録
            if support_system:
                for unit1 in game_map.units:
                    for unit2 in game_map.units:
                        if unit1.team == unit2.team and unit1 != unit2:
                            # 同じチームの異なるユニット同士で
                            distance = abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
                            if distance <= 3:  # 3マス以内のユニット
                                support_system.record_battle_together(unit1.name, unit2.name)
            
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
        
        # レジェンダリー武器による反撃保証
        if temp_defender.equipped_weapon and isinstance(temp_defender.equipped_weapon, LegendaryWeapon):
            for effect in temp_defender.equipped_weapon.effects:
                if effect.effect_type == "counter_attack" and effect.effect_value:
                    guaranteed_counter = True
                    break
        
        can_counter = counter_range_check or guaranteed_counter
        
        if can_counter:
            defender_result = EnhancedCombatSystem.perform_attack(temp_defender, temp_attacker, game_map, support_system)
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
                
                # レジェンダリー武器の効果を除去
                if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
                    attacker.equipped_weapon.remove_effects(attacker)
                
                if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
                    defender.equipped_weapon.remove_effects(defender)
                
                # 戦闘中に発動したスキルを結果に追加
                results["activated_skills"] = {
                    "attacker": [skill.name for skill in attacker.active_skills],
                    "defender": [skill.name for skill in defender.active_skills]
                }
                
                # 支援システムの更新 - 一緒に戦闘した記録
                if support_system:
                    for unit1 in game_map.units:
                        for unit2 in game_map.units:
                            if unit1.team == unit2.team and unit1 != unit2:
                                # 同じチームの異なるユニット同士で
                                distance = abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
                                if distance <= 3:  # 3マス以内のユニット
                                    support_system.record_battle_together(unit1.name, unit2.name)
                
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
        
        # レジェンダリー武器による追撃保証
        if temp_attacker.equipped_weapon and isinstance(temp_attacker.equipped_weapon, LegendaryWeapon):
            for effect in temp_attacker.equipped_weapon.effects:
                if effect.effect_type == "follow_up" and effect.effect_value:
                    guaranteed_follow_up_attacker = True
                    break
        
        if temp_defender.equipped_weapon and isinstance(temp_defender.equipped_weapon, LegendaryWeapon):
            for effect in temp_defender.equipped_weapon.effects:
                if effect.effect_type == "follow_up" and effect.effect_value:
                    guaranteed_follow_up_defender = True
                    break
        
        if temp_attacker.can_double_attack(temp_defender) or guaranteed_follow_up_attacker:
            attacker_result2 = EnhancedCombatSystem.perform_attack(temp_attacker, temp_defender, game_map, support_system)
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
                
                # レジェンダリー武器の効果を除去
                if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
                    attacker.equipped_weapon.remove_effects(attacker)
                
                if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
                    defender.equipped_weapon.remove_effects(defender)
                
                # 戦闘中に発動したスキルを結果に追加
                results["activated_skills"] = {
                    "attacker": [skill.name for skill in attacker.active_skills],
                    "defender": [skill.name for skill in defender.active_skills]
                }
                
                # 支援システムの更新 - 一緒に戦闘した記録
                if support_system:
                    for unit1 in game_map.units:
                        for unit2 in game_map.units:
                            if unit1.team == unit2.team and unit1 != unit2:
                                # 同じチームの異なるユニット同士で
                                distance = abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
                                if distance <= 3:  # 3マス以内のユニット
                                    support_system.record_battle_together(unit1.name, unit2.name)
                
                # スキルをリセット
                attacker.deactivate_skills()
                defender.deactivate_skills()
                
                return results
        
        elif can_counter and (temp_defender.can_double_attack(temp_attacker) or guaranteed_follow_up_defender):
            defender_result2 = EnhancedCombatSystem.perform_attack(temp_defender, temp_attacker, game_map, support_system)
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
                
                # レジェンダリー武器の効果を除去
                if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
                    attacker.equipped_weapon.remove_effects(attacker)
                
                if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
                    defender.equipped_weapon.remove_effects(defender)
                
                # 戦闘中に発動したスキルを結果に追加
                results["activated_skills"] = {
                    "attacker": [skill.name for skill in attacker.active_skills],
                    "defender": [skill.name for skill in defender.active_skills]
                }
                
                # 支援システムの更新 - 一緒に戦闘した記録
                if support_system:
                    for unit1 in game_map.units:
                        for unit2 in game_map.units:
                            if unit1.team == unit2.team and unit1 != unit2:
                                # 同じチームの異なるユニット同士で
                                distance = abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
                                if distance <= 3:  # 3マス以内のユニット
                                    support_system.record_battle_together(unit1.name, unit2.name)
                
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
        
        # レジェンダリー武器の効果を除去
        if attacker.equipped_weapon and isinstance(attacker.equipped_weapon, LegendaryWeapon):
            attacker.equipped_weapon.remove_effects(attacker)
        
        if defender.equipped_weapon and isinstance(defender.equipped_weapon, LegendaryWeapon):
            defender.equipped_weapon.remove_effects(defender)
        
        # 戦闘中に発動したスキルを結果に追加
        results["activated_skills"] = {
            "attacker": [skill.name for skill in attacker.active_skills],
            "defender": [skill.name for skill in defender.active_skills]
        }
        
        # 支援システムの更新 - 一緒に戦闘した記録
        if support_system:
            for unit1 in game_map.units:
                for unit2 in game_map.units:
                    if unit1.team == unit2.team and unit1 != unit2:
                        # 同じチームの異なるユニット同士で
                        distance = abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
                        if distance <= 3:  # 3マス以内のユニット
                            support_system.record_battle_together(unit1.name, unit2.name)
        
        # スキルをリセット
        attacker.deactivate_skills()
        defender.deactivate_skills()
        
        return results
    
    @staticmethod
    def generate_reward_weapon(defeated_unit, combat_results) -> Optional[LegendaryWeapon]:
        """戦闘結果に基づいたレジェンダリー武器の生成"""
        from legendary_items import LegendaryItemGenerator, ItemRarity
        
        # 強いユニットを倒すほど良い武器が出やすい
        level_factor = defeated_unit.level / 20.0  # レベル20が最大値として正規化
        
        # クリティカルや連続攻撃などでの派手な勝利
        spectacular_victory = any(r.get("critical", False) for r in combat_results["attacker_results"])
        spectacular_victory = spectacular_victory or any(r.get("multi_attack", False) for r in combat_results["attacker_results"])
        
        # レア度の確率決定
        rarity_weights = {
            ItemRarity.UNCOMMON: 100 * (1.0 - level_factor),
            ItemRarity.RARE: 50 * level_factor,
            ItemRarity.EPIC: 20 * level_factor,
            ItemRarity.LEGENDARY: 5 * level_factor
        }
        
        # 派手な勝利ならレア度の高い武器が出やすくする
        if spectacular_victory:
            for rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
                rarity_weights[rarity] *= 1.5
        
        # ドロップするかの判定（倒したユニットが強いほど確率上昇）
        drop_chance = 5 + 25 * level_factor  # 5-30%
        if spectacular_victory:
            drop_chance *= 1.5  # 派手な勝利なら1.5倍
        
        if random.random() * 100 > drop_chance:
            return None  # ドロップなし
        
        # レア度の選択
        rarity_choice = random.choices(
            list(rarity_weights.keys()),
            weights=list(rarity_weights.values()),
            k=1
        )[0]
        
        # 倒したユニットの武器タイプを高確率で引き継ぐ
        weapon_type = None
        if defeated_unit.equipped_weapon and random.random() < 0.7:
            weapon_type = defeated_unit.equipped_weapon.weapon_type
        
        # レジェンダリー武器の生成
        generator = LegendaryItemGenerator()
        return generator.generate_legendary_weapon(rarity_choice, weapon_type)