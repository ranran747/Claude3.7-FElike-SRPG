# skills.py
from enum import Enum
import random
from typing import Dict, Union, Optional, List

class SkillTriggerType(Enum):
    # 確率系トリガー
    PERCENTAGE = 1        # 確率で発動
    STAT_BASED = 2        # 能力値に基づく確率で発動
    
    # 条件系トリガー
    ON_ATTACK = 3         # 攻撃時
    ON_DEFEND = 4         # 防御時
    ON_KILL = 5           # 敵を倒した時
    ON_DAMAGE = 6         # ダメージを受けた時
    PRE_COMBAT = 7        # 戦闘開始前
    POST_COMBAT = 8       # 戦闘終了後
    ON_TURN_START = 9     # ターン開始時
    ON_TURN_END = 10      # ターン終了時
    ALWAYS_ACTIVE = 11    # 常時発動
    HP_THRESHOLD = 12     # HPが特定の割合以下/以上
    WEAPON_TYPE = 13      # 特定の武器タイプ使用時
    
class SkillEffectType(Enum):
    STAT_BOOST = 1        # 能力値ブースト
    DAMAGE_BOOST = 2      # ダメージ増加
    DAMAGE_REDUCE = 3     # ダメージ減少
    HIT_BOOST = 4         # 命中率ブースト
    AVOID_BOOST = 5       # 回避率ブースト
    CRITICAL_BOOST = 6    # クリティカル率ブースト
    COUNTER_ATTACK = 7    # 反撃
    FOLLOW_UP = 8         # 追撃
    HEAL = 9              # 回復
    SPECIAL_ATTACK = 10   # 特殊攻撃
    SPECIAL_MOVEMENT = 11 # 特殊移動
    TERRAIN_EFFECT = 12   # 地形効果変更
    WEAPON_EFFECT = 13    # 武器効果変更
    RANGE_CHANGE = 14     # 攻撃範囲変更
    STATUS_IMMUNITY = 15  # 状態異常耐性

class Skill:
    def __init__(
        self, 
        name: str,
        description: str,
        trigger_type: SkillTriggerType,
        effect_type: SkillEffectType,
        trigger_value: Union[int, float, str, None] = None,
        effect_value: Union[int, float, str, None] = None,
        duration: int = -1  # -1は永続
    ):
        self.name = name
        self.description = description
        self.trigger_type = trigger_type
        self.effect_type = effect_type
        self.trigger_value = trigger_value
        self.effect_value = effect_value
        self.duration = duration
        self.remaining_duration = duration if duration > 0 else -1
        self.is_active = False
        
    def check_trigger(self, unit, combat_data: Dict = None) -> bool:
        """スキルのトリガー条件をチェックする"""
        if self.trigger_type == SkillTriggerType.PERCENTAGE:
            # 発動率に基づくチェック
            roll = random.randint(1, 100)
            return roll <= self.trigger_value
            
        elif self.trigger_type == SkillTriggerType.STAT_BASED:
            # 能力値に基づく発動率（例: 技×2%）
            if isinstance(self.trigger_value, tuple) and len(self.trigger_value) == 2:
                stat_name, multiplier = self.trigger_value
                if hasattr(unit, stat_name):
                    stat_value = getattr(unit, stat_name)
                    roll = random.randint(1, 100)
                    return roll <= (stat_value * multiplier)
            return False
            
        elif self.trigger_type == SkillTriggerType.HP_THRESHOLD:
            # HP閾値チェック（例: HP < 50%）
            if isinstance(self.trigger_value, tuple) and len(self.trigger_value) == 2:
                operator, threshold = self.trigger_value
                hp_ratio = unit.current_hp / unit.max_hp * 100
                if operator == "<":
                    return hp_ratio < threshold
                elif operator == "<=":
                    return hp_ratio <= threshold
                elif operator == ">":
                    return hp_ratio > threshold
                elif operator == ">=":
                    return hp_ratio >= threshold
            return False
            
        elif self.trigger_type == SkillTriggerType.WEAPON_TYPE:
            # 武器タイプチェック
            if unit.equipped_weapon:
                return unit.equipped_weapon.weapon_type == self.trigger_value
            return False
            
        elif self.trigger_type == SkillTriggerType.ALWAYS_ACTIVE:
            # 常時発動
            return True
            
        # 戦闘関連トリガー (combat_dataが必要)
        elif combat_data:
            if self.trigger_type == SkillTriggerType.ON_ATTACK:
                return combat_data.get("is_attacker", False)
                
            elif self.trigger_type == SkillTriggerType.ON_DEFEND:
                return not combat_data.get("is_attacker", True)
                
            elif self.trigger_type == SkillTriggerType.ON_KILL:
                return combat_data.get("target_killed", False)
                
            elif self.trigger_type == SkillTriggerType.ON_DAMAGE:
                return combat_data.get("damage_received", 0) > 0
                
        # 他のトリガータイプ
        return False
        
    def apply_effect(self, unit, target = None, combat_data: Dict = None) -> Dict:
        """スキル効果を適用し、変更された戦闘データを返す"""
        if not combat_data:
            combat_data = {}
            
        effect_result = {}
        
        # スキル効果の適用
        if self.effect_type == SkillEffectType.STAT_BOOST:
            # 一時的な能力値ブースト
            if isinstance(self.effect_value, tuple) and len(self.effect_value) == 2:
                stat_name, boost_value = self.effect_value
                if hasattr(unit, stat_name):
                    current_value = getattr(unit, stat_name)
                    effect_result["boosted_stat"] = stat_name
                    effect_result["boost_amount"] = boost_value
                    combat_data[f"temp_{stat_name}"] = current_value + boost_value
                    
        elif self.effect_type == SkillEffectType.DAMAGE_BOOST:
            # ダメージ増加
            combat_data["damage_modifier"] = combat_data.get("damage_modifier", 0) + self.effect_value
            effect_result["damage_boost"] = self.effect_value
            
        elif self.effect_type == SkillEffectType.DAMAGE_REDUCE:
            # ダメージ減少
            combat_data["damage_reduction"] = combat_data.get("damage_reduction", 0) + self.effect_value
            effect_result["damage_reduction"] = self.effect_value
            
        elif self.effect_type == SkillEffectType.HIT_BOOST:
            # 命中率ブースト
            combat_data["hit_modifier"] = combat_data.get("hit_modifier", 0) + self.effect_value
            effect_result["hit_boost"] = self.effect_value
            
        elif self.effect_type == SkillEffectType.AVOID_BOOST:
            # 回避率ブースト
            combat_data["avoid_modifier"] = combat_data.get("avoid_modifier", 0) + self.effect_value
            effect_result["avoid_boost"] = self.effect_value
            
        elif self.effect_type == SkillEffectType.CRITICAL_BOOST:
            # クリティカル率ブースト
            combat_data["crit_modifier"] = combat_data.get("crit_modifier", 0) + self.effect_value
            effect_result["crit_boost"] = self.effect_value
            
        elif self.effect_type == SkillEffectType.HEAL:
            # HP回復
            if isinstance(self.effect_value, float) and 0 <= self.effect_value <= 1:
                # 最大HPの割合で回復
                heal_amount = int(unit.max_hp * self.effect_value)
            else:
                # 固定値で回復
                heal_amount = int(self.effect_value)
                
            unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
            effect_result["healed"] = heal_amount
            
        elif self.effect_type == SkillEffectType.FOLLOW_UP:
            # 追撃を保証
            combat_data["guaranteed_follow_up"] = True
            effect_result["follow_up"] = True
            
        elif self.effect_type == SkillEffectType.COUNTER_ATTACK:
            # 反撃を保証（通常反撃できない状況でも）
            combat_data["guaranteed_counter"] = True
            effect_result["counter_attack"] = True
            
        # デュレーション管理
        if self.duration > 0:
            self.remaining_duration -= 1
            if self.remaining_duration <= 0:
                self.is_active = False
                
        return effect_result

def create_sample_skills():
    """サンプルスキルを作成する"""
    from constants import WeaponType
    
    # 攻撃系スキル
    astra = Skill(
        name="連続攻撃",
        description="確率で5回連続攻撃を行う（各攻撃のダメージは通常の30%）",
        trigger_type=SkillTriggerType.STAT_BASED,
        effect_type=SkillEffectType.SPECIAL_ATTACK,
        trigger_value=("skill", 0.5),  # 技×0.5%の確率で発動
        effect_value={"attacks": 5, "damage_multiplier": 0.3}
    )
    
    luna = Skill(
        name="月光",
        description="攻撃時、敵の守備または魔防の50%を無視する",
        trigger_type=SkillTriggerType.PERCENTAGE,
        effect_type=SkillEffectType.SPECIAL_ATTACK,
        trigger_value=35,  # 35%の確率で発動
        effect_value={"defense_pierce": 0.5}
    )
    
    adept = Skill(
        name="連撃",
        description="速さが一定以上高いと追撃が発生する確率が上がる",
        trigger_type=SkillTriggerType.STAT_BASED,
        effect_type=SkillEffectType.FOLLOW_UP,
        trigger_value=("speed", 0.75),  # 速さ×0.75%の確率で発動
        effect_value=True
    )

    # 防御系スキル
    pavise = Skill(
        name="大盾",
        description="物理攻撃のダメージを半減する",
        trigger_type=SkillTriggerType.STAT_BASED,
        effect_type=SkillEffectType.DAMAGE_REDUCE,
        trigger_value=("defense", 0.4),  # 守備×0.4%の確率で発動
        effect_value=0.5  # ダメージ50%減少
    )
    
    aegis = Skill(
        name="聖盾",
        description="魔法攻撃のダメージを半減する",
        trigger_type=SkillTriggerType.STAT_BASED,
        effect_type=SkillEffectType.DAMAGE_REDUCE,
        trigger_value=("resistance", 0.4),  # 魔防×0.4%の確率で発動
        effect_value=0.5  # ダメージ50%減少
    )

    # 能力強化系スキル
    vantage = Skill(
        name="先制攻撃",
        description="HPが50%以下のとき、敵より先に攻撃する",
        trigger_type=SkillTriggerType.HP_THRESHOLD,
        effect_type=SkillEffectType.SPECIAL_ATTACK,
        trigger_value=("<", 50),  # HP < 50%で発動
        effect_value={"vantage": True}
    )
    
    wrath = Skill(
        name="怒り",
        description="HPが50%以下のとき、クリティカル率+20",
        trigger_type=SkillTriggerType.HP_THRESHOLD,
        effect_type=SkillEffectType.CRITICAL_BOOST,
        trigger_value=("<", 50),  # HP < 50%で発動
        effect_value=20  # クリティカル率+20
    )
    
    sol = Skill(
        name="太陽",
        description="攻撃時、与えたダメージの半分を回復する",
        trigger_type=SkillTriggerType.PERCENTAGE,
        effect_type=SkillEffectType.HEAL,
        trigger_value=30,  # 30%の確率で発動
        effect_value={"heal_ratio": 0.5}  # 与ダメージの50%回復
    )

    # 武器タイプに関するスキル
    swordfaire = Skill(
        name="剣の達人",
        description="剣装備時、攻撃+5",
        trigger_type=SkillTriggerType.WEAPON_TYPE,
        effect_type=SkillEffectType.DAMAGE_BOOST,
        trigger_value=WeaponType.SWORD,
        effect_value=5  # 攻撃+5
    )
    
    axebreaker = Skill(
        name="斧殺し",
        description="斧使用ユニットとの戦闘時、命中・回避+30",
        trigger_type=SkillTriggerType.ALWAYS_ACTIVE,
        effect_type=SkillEffectType.SPECIAL_ATTACK,
        effect_value={
            "condition": "opponent_weapon_type == WeaponType.AXE",
            "hit_bonus": 30,
            "avoid_bonus": 30
        }
    )
    
    return [astra, luna, adept, pavise, aegis, vantage, wrath, sol, swordfaire, axebreaker]