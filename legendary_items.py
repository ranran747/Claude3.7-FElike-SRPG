# legendary_items.py
from typing import List, Dict, Tuple, Optional
import random
from enum import Enum
from skills import Skill, SkillTriggerType, SkillEffectType
from weapon import Weapon
from constants import WeaponType

class ItemRarity(Enum):
    """アイテムのレア度を定義するクラス"""
    COMMON = 0     # 通常
    UNCOMMON = 1   # やや珍しい
    RARE = 2       # レア
    EPIC = 3       # エピック
    LEGENDARY = 4  # レジェンダリー

class ItemEffect:
    """アイテムの特殊効果を定義するクラス"""
    def __init__(self, 
                 name: str,
                 description: str,
                 effect_type: str,          # "stat_boost", "skill_grant", "special"のいずれか
                 effect_value: dict):       # 効果の詳細を格納した辞書
        self.name = name
        self.description = description
        self.effect_type = effect_type
        self.effect_value = effect_value
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（シリアライズ用）"""
        return {
            "name": self.name,
            "description": self.description,
            "effect_type": self.effect_type,
            "effect_value": self.effect_value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ItemEffect':
        """辞書からインスタンスを生成（デシリアライズ用）"""
        try:
            return cls(
                name=data["name"],
                description=data["description"],
                effect_type=data["effect_type"],
                effect_value=data["effect_value"]
            )
        except KeyError as e:
            print(f"アイテム効果データの読み込みエラー: {e}")
            return None

class LegendaryWeapon(Weapon):
    """スキルや特殊効果を持つ伝説の武器クラス"""
    def __init__(self, name, weapon_type, might, hit, crit, weight, range_min, range_max, durability,
                 rarity: ItemRarity = ItemRarity.LEGENDARY,
                 effects: List[ItemEffect] = None,
                 skills: List[Skill] = None,
                 lore: str = "",                 # 武器の背景ストーリー
                 required_level: int = 1,        # 必要レベル
                 unique_owner: Optional[str] = None):  # 専用キャラクター（いれば）
        super().__init__(name, weapon_type, might, hit, crit, weight, range_min, range_max, durability)
        
        self.rarity = rarity
        self.effects = effects or []
        self.skills = skills or []
        self.lore = lore
        self.required_level = required_level
        self.unique_owner = unique_owner
    
    def can_equip(self, unit) -> bool:
        """ユニットが装備可能かチェック"""
        # 専用キャラクターがいる場合はチェック
        if self.unique_owner and unit.name != self.unique_owner:
            return False
        
        # レベル要件
        if unit.level < self.required_level:
            return False
        
        # 通常の装備チェック
        return True
    
    def apply_effects(self, unit):
        """武器の効果をユニットに適用"""
        for effect in self.effects:
            if effect.effect_type == "stat_boost":
                # ステータス上昇効果
                stat_boosts = effect.effect_value.get("stats", {})
                for stat_name, value in stat_boosts.items():
                    # 一時的なステータス修正値を設定
                    unit.temp_stat_modifiers[stat_name] = unit.temp_stat_modifiers.get(stat_name, 0) + value
            
            # その他の効果は戦闘システム側で適用
    
    def remove_effects(self, unit):
        """武器の効果をユニットから除去"""
        # 一時的なステータス修正値をリセット
        unit.temp_stat_modifiers = {}
    
    def get_granted_skills(self) -> List[Skill]:
        """武器が付与するスキルのリストを取得"""
        granted_skills = []
        
        for effect in self.effects:
            if effect.effect_type == "skill_grant":
                skill_data = effect.effect_value.get("skill")
                if skill_data:
                    # スキルの生成
                    try:
                        skill = Skill(
                            name=skill_data.get("name", "不明なスキル"),
                            description=skill_data.get("description", ""),
                            trigger_type=SkillTriggerType[skill_data.get("trigger_type", "ALWAYS_ACTIVE")],
                            effect_type=SkillEffectType[skill_data.get("effect_type", "STAT_BOOST")],
                            trigger_value=skill_data.get("trigger_value"),
                            effect_value=skill_data.get("effect_value"),
                            duration=skill_data.get("duration", -1)
                        )
                        granted_skills.append(skill)
                    except (KeyError, ValueError) as e:
                        print(f"スキル生成エラー: {e}")
        
        # 武器に直接設定されたスキルも追加
        granted_skills.extend(self.skills)
        
        return granted_skills
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（シリアライズ用）"""
        base_dict = {
            "name": self.name,
            "weapon_type": self.weapon_type.name,
            "might": self.might,
            "hit": self.hit,
            "crit": self.crit,
            "weight": self.weight,
            "range_min": self.range_min,
            "range_max": self.range_max,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "rarity": self.rarity.name,
            "effects": [effect.to_dict() for effect in self.effects],
            "skills": [skill.__dict__ for skill in self.skills],  # 簡易的な変換
            "lore": self.lore,
            "required_level": self.required_level,
            "unique_owner": self.unique_owner
        }
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LegendaryWeapon':
        """辞書からインスタンスを生成（デシリアライズ用）"""
        try:
            # 効果のロード
            effects = []
            for effect_data in data.get("effects", []):
                effect = ItemEffect.from_dict(effect_data)
                if effect:
                    effects.append(effect)
            
            # スキルのロード（簡易的）
            skills = []
            for skill_data in data.get("skills", []):
                try:
                    skill = Skill(
                        name=skill_data.get("name", "不明なスキル"),
                        description=skill_data.get("description", ""),
                        trigger_type=SkillTriggerType[skill_data.get("trigger_type", "ALWAYS_ACTIVE")],
                        effect_type=SkillEffectType[skill_data.get("effect_type", "STAT_BOOST")],
                        trigger_value=skill_data.get("trigger_value"),
                        effect_value=skill_data.get("effect_value"),
                        duration=skill_data.get("duration", -1)
                    )
                    skills.append(skill)
                except (KeyError, ValueError) as e:
                    print(f"スキル読み込みエラー: {e}")
            
            return cls(
                name=data["name"],
                weapon_type=WeaponType[data["weapon_type"]],
                might=data["might"],
                hit=data["hit"],
                crit=data["crit"],
                weight=data["weight"],
                range_min=data["range_min"],
                range_max=data["range_max"],
                durability=data["durability"],
                rarity=ItemRarity[data.get("rarity", "LEGENDARY")],
                effects=effects,
                skills=skills,
                lore=data.get("lore", ""),
                required_level=data.get("required_level", 1),
                unique_owner=data.get("unique_owner")
            )
        except (KeyError, ValueError) as e:
            print(f"伝説の武器データの読み込みエラー: {e}")
            return None


class LegendaryItemGenerator:
    """伝説の武器・アイテムを生成するクラス"""
    def __init__(self):
        # 伝説アイテムのテンプレート
        self.weapon_templates = self._load_weapon_templates()
        
        # 効果のテンプレート
        self.effect_templates = self._load_effect_templates()
        
        # スキルのテンプレート
        self.skill_templates = self._load_skill_templates()
    
    def _load_weapon_templates(self) -> List[Dict]:
        """武器テンプレートをロード"""
        # 実際は外部ファイルから読み込む
        return [
            {
                "name_prefix": ["聖なる", "神々の", "英雄の", "太古の", "運命の"],
                "name_base": ["剣", "槍", "斧", "弓", "魔道書"],
                "name_suffix": ["", "・真実", "・勇気", "・救済", "・破滅"],
                "might_range": (8, 15),
                "hit_range": (80, 100),
                "crit_range": (5, 20),
                "weight_range": (3, 8),
                "effects_count": (1, 3),
                "skills_count": (0, 2)
            }
        ]
    
    def _load_effect_templates(self) -> List[Dict]:
        """効果テンプレートをロード"""
        # 実際は外部ファイルから読み込む
        return [
            # ステータス上昇効果
            {
                "name": "力の祝福",
                "description": "力+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"strength": (2, 5)}},
                "rarity_min": ItemRarity.UNCOMMON
            },
            {
                "name": "魔力の祝福",
                "description": "魔力+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"magic": (2, 5)}},
                "rarity_min": ItemRarity.UNCOMMON
            },
            {
                "name": "技の祝福",
                "description": "技+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"skill": (2, 5)}},
                "rarity_min": ItemRarity.UNCOMMON
            },
            {
                "name": "速さの祝福",
                "description": "速さ+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"speed": (2, 5)}},
                "rarity_min": ItemRarity.UNCOMMON
            },
            {
                "name": "幸運の祝福",
                "description": "幸運+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"luck": (2, 5)}},
                "rarity_min": ItemRarity.UNCOMMON
            },
            {
                "name": "守備の祝福",
                "description": "守備+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"defense": (2, 5)}},
                "rarity_min": ItemRarity.UNCOMMON
            },
            {
                "name": "魔防の祝福",
                "description": "魔防+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"resistance": (2, 5)}},
                "rarity_min": ItemRarity.UNCOMMON
            },
            # 複合効果（レア以上）
            {
                "name": "英雄の力",
                "description": "力+{str_value} 速さ+{spd_value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"strength": (3, 6), "speed": (2, 4)}},
                "rarity_min": ItemRarity.RARE
            },
            {
                "name": "魔道の極意",
                "description": "魔力+{mag_value} 魔防+{res_value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"magic": (3, 6), "resistance": (2, 4)}},
                "rarity_min": ItemRarity.RARE
            },
            {
                "name": "守護者の加護",
                "description": "守備+{def_value} 魔防+{res_value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {"defense": (3, 6), "resistance": (3, 6)}},
                "rarity_min": ItemRarity.RARE
            },
            # 特殊効果（レジェンダリー）
            {
                "name": "目覚めし英雄",
                "description": "全ステータス+{value}",
                "effect_type": "stat_boost",
                "effect_value": {"stats": {
                    "strength": (2, 3), "magic": (2, 3), "skill": (2, 3),
                    "speed": (2, 3), "luck": (2, 3), "defense": (2, 3), "resistance": (2, 3)
                }},
                "rarity_min": ItemRarity.LEGENDARY
            }
        ]
    
    def _load_skill_templates(self) -> List[Dict]:
        """スキルテンプレートをロード"""
        # 実際は外部ファイルから読み込む
        return [
            # 攻撃系スキル
            {
                "name": "会心",
                "description": "確率でクリティカル率が大幅に上昇",
                "trigger_type": "PERCENTAGE",
                "effect_type": "CRITICAL_BOOST",
                "trigger_value": (20, 35),
                "effect_value": (30, 50),
                "rarity_min": ItemRarity.RARE
            },
            {
                "name": "見切り",
                "description": "命中率が上昇",
                "trigger_type": "ALWAYS_ACTIVE",
                "effect_type": "HIT_BOOST",
                "trigger_value": None,
                "effect_value": (15, 25),
                "rarity_min": ItemRarity.RARE
            },
            {
                "name": "切り裂き",
                "description": "確率で敵の守備または魔防の一部を無視",
                "trigger_type": "PERCENTAGE",
                "effect_type": "SPECIAL_ATTACK",
                "trigger_value": (25, 40),
                "effect_value": {"defense_pierce": (0.3, 0.5)},
                "rarity_min": ItemRarity.EPIC
            },
            # 防御系スキル
            {
                "name": "守護の心得",
                "description": "受けるダメージを減少",
                "trigger_type": "ALWAYS_ACTIVE",
                "effect_type": "DAMAGE_REDUCE",
                "trigger_value": None,
                "effect_value": (2, 4),
                "rarity_min": ItemRarity.UNCOMMON
            },
            {
                "name": "不死鳥",
                "description": "HPが低い時、確率で被ダメージを大幅に軽減",
                "trigger_type": "HP_THRESHOLD",
                "effect_type": "DAMAGE_REDUCE",
                "trigger_value": ("<", 30),
                "effect_value": (0.3, 0.5),
                "rarity_min": ItemRarity.EPIC
            },
            # 回復系スキル
            {
                "name": "生命吸収",
                "description": "攻撃時、与えたダメージの一部を回復",
                "trigger_type": "ON_DAMAGE",
                "effect_type": "HEAL",
                "trigger_value": None,
                "effect_value": {"heal_ratio": (0.15, 0.3)},
                "rarity_min": ItemRarity.RARE
            },
            # レジェンダリースキル
            {
                "name": "神速",
                "description": "速さが相手より大幅に高い場合、確実に追撃を行う",
                "trigger_type": "ALWAYS_ACTIVE",
                "effect_type": "FOLLOW_UP",
                "trigger_value": None,
                "effect_value": True,
                "rarity_min": ItemRarity.LEGENDARY
            },
            {
                "name": "天帝の一撃",
                "description": "確率で敵に3回連続攻撃を行う",
                "trigger_type": "PERCENTAGE",
                "effect_type": "SPECIAL_ATTACK",
                "trigger_value": (20, 30),
                "effect_value": {"attacks": 3, "damage_multiplier": 0.6},
                "rarity_min": ItemRarity.LEGENDARY
            }
        ]
    
    def generate_legendary_weapon(self, rarity: ItemRarity = None, weapon_type: WeaponType = None) -> LegendaryWeapon:
        """
        ランダムな伝説の武器を生成
        
        Args:
            rarity: 希望するレア度（Noneの場合はランダム）
            weapon_type: 希望する武器タイプ（Noneの場合はランダム）
            
        Returns:
            LegendaryWeapon: 生成された伝説の武器
        """
        # レア度の決定
        if rarity is None:
            rarity_weights = {
                ItemRarity.UNCOMMON: 50,
                ItemRarity.RARE: 30,
                ItemRarity.EPIC: 15,
                ItemRarity.LEGENDARY: 5
            }
            rarity_choice = random.choices(
                list(rarity_weights.keys()),
                weights=list(rarity_weights.values()),
                k=1
            )[0]
            rarity = rarity_choice
        
        # 武器タイプの決定
        if weapon_type is None:
            weapon_type = random.choice(list(WeaponType))
        
        # テンプレートをランダムに選択
        template = random.choice(self.weapon_templates)
        
        # 名前の生成
        name_prefix = random.choice(template["name_prefix"])
        
        # 武器タイプに応じた名前の基本部分
        type_name_map = {
            WeaponType.SWORD: "剣",
            WeaponType.LANCE: "槍",
            WeaponType.AXE: "斧",
            WeaponType.BOW: "弓",
            WeaponType.MAGIC: "魔道書"
        }
        name_base = type_name_map.get(weapon_type, random.choice(template["name_base"]))
        
        name_suffix = ""
        if random.random() < 0.7:  # 70%の確率でサフィックスを追加
            name_suffix = random.choice(template["name_suffix"])
        
        weapon_name = f"{name_prefix}{name_base}{name_suffix}"
        
        # 武器性能の決定（レア度が高いほど強い）
        rarity_bonus = rarity.value * 2
        
        might_range = template["might_range"]
        might = random.randint(might_range[0], might_range[1]) + rarity_bonus
        
        hit_range = template["hit_range"]
        hit = min(100, random.randint(hit_range[0], hit_range[1]) + rarity_bonus)
        
        crit_range = template["crit_range"]
        crit = random.randint(crit_range[0], crit_range[1]) + rarity_bonus
        
        weight_range = template["weight_range"]
        weight = max(1, random.randint(weight_range[0], weight_range[1]) - rarity.value)
        
        # 武器タイプに応じた射程
        if weapon_type == WeaponType.BOW:
            range_min, range_max = 2, 2
        elif weapon_type == WeaponType.MAGIC:
            range_min, range_max = 1, 2
        else:
            range_min, range_max = 1, 1
        
        # 耐久度（レア度が高いほど高い）
        durability = 30 + rarity.value * 10
        
        # 効果の数を決定
        effects_count_range = template["effects_count"]
        effects_count = random.randint(effects_count_range[0], min(effects_count_range[1], rarity.value + 1))
        
        # 効果の生成
        effects = []
        for _ in range(effects_count):
            effect = self._generate_random_effect(rarity)
            if effect:
                effects.append(effect)
        
        # スキルの数を決定
        skills_count_range = template["skills_count"]
        skills_count = random.randint(skills_count_range[0], min(skills_count_range[1], rarity.value))
        
        # スキルの生成
        skills = []
        for _ in range(skills_count):
            skill = self._generate_random_skill(rarity)
            if skill:
                skills.append(skill)
        
        # 必要レベル（レア度に応じて）
        required_level = max(1, rarity.value * 5)
        
        # 伝説の武器を作成
        legendary_weapon = LegendaryWeapon(
            name=weapon_name,
            weapon_type=weapon_type,
            might=might,
            hit=hit,
            crit=crit,
            weight=weight,
            range_min=range_min,
            range_max=range_max,
            durability=durability,
            rarity=rarity,
            effects=effects,
            skills=skills,
            lore=self._generate_lore(weapon_name, rarity),
            required_level=required_level
        )
        
        return legendary_weapon
    
    def _generate_random_effect(self, rarity: ItemRarity) -> Optional[ItemEffect]:
        """
        ランダムな効果を生成
        
        Args:
            rarity: アイテムのレア度
            
        Returns:
            ItemEffect: 生成された効果、または None
        """
        # レア度に合った効果テンプレートをフィルタリング
        valid_templates = [
            t for t in self.effect_templates 
            if ItemRarity[t.get("rarity_min", "COMMON").name].value <= rarity.value
        ]
        
        if not valid_templates:
            return None
        
        # ランダムにテンプレートを選択
        template = random.choice(valid_templates)
        
        name = template["name"]
        description = template["description"]
        effect_type = template["effect_type"]
        effect_value_template = template["effect_value"].copy()
        
        # 効果値の生成
        effect_value = {}
        if effect_type == "stat_boost":
            stats = {}
            for stat_name, value_range in effect_value_template.get("stats", {}).items():
                value = random.randint(value_range[0], value_range[1])
                stats[stat_name] = value
                
                # 説明文のプレースホルダーを置換
                if stat_name == "strength":
                    description = description.replace("{str_value}", str(value))
                elif stat_name == "magic":
                    description = description.replace("{mag_value}", str(value))
                elif stat_name == "skill":
                    description = description.replace("{skl_value}", str(value))
                elif stat_name == "speed":
                    description = description.replace("{spd_value}", str(value))
                elif stat_name == "luck":
                    description = description.replace("{lck_value}", str(value))
                elif stat_name == "defense":
                    description = description.replace("{def_value}", str(value))
                elif stat_name == "resistance":
                    description = description.replace("{res_value}", str(value))
                
                # 汎用的な置換
                description = description.replace("{value}", str(value))
            
            effect_value["stats"] = stats
        else:
            # その他の効果タイプの処理
            effect_value = effect_value_template
        
        return ItemEffect(name, description, effect_type, effect_value)
    
    def _generate_random_skill(self, rarity: ItemRarity) -> Optional[Skill]:
        """
        ランダムなスキルを生成
        
        Args:
            rarity: アイテムのレア度
            
        Returns:
            Skill: 生成されたスキル、または None
        """
        # レア度に合ったスキルテンプレートをフィルタリング
        valid_templates = [
            t for t in self.skill_templates 
            if ItemRarity[t.get("rarity_min", "COMMON").name].value <= rarity.value
        ]
        
        if not valid_templates:
            return None
        
        # ランダムにテンプレートを選択
        template = random.choice(valid_templates)
        
        name = template["name"]
        description = template["description"]
        
        # トリガータイプの処理
        trigger_type = SkillTriggerType[template["trigger_type"]]
        
        # トリガー値の処理
        trigger_value_template = template["trigger_value"]
        trigger_value = None
        
        if isinstance(trigger_value_template, tuple) and len(trigger_value_template) == 2:
            # 範囲から値を選択
            trigger_value = random.randint(trigger_value_template[0], trigger_value_template[1])
            # 説明文のプレースホルダーを置換
            description = description.replace("{trigger_value}", str(trigger_value))
        elif isinstance(trigger_value_template, tuple) and len(trigger_value_template) >= 3:
            # 特殊な形式（例: HP条件）
            trigger_value = trigger_value_template
        else:
            trigger_value = trigger_value_template
        
        # 効果タイプの処理
        effect_type = SkillEffectType[template["effect_type"]]
        
        # 効果値の処理
        effect_value_template = template["effect_value"]
        effect_value = None
        
        if isinstance(effect_value_template, tuple) and len(effect_value_template) == 2:
            # 範囲から値を選択
            effect_value = random.randint(effect_value_template[0], effect_value_template[1])
            # 説明文のプレースホルダーを置換
            description = description.replace("{value}", str(effect_value))
        elif isinstance(effect_value_template, dict):
            # 辞書形式の効果値
            effect_value = {}
            for key, value in effect_value_template.items():
                if isinstance(value, tuple) and len(value) == 2:
                    # 範囲から値を選択
                    if isinstance(value[0], float) or isinstance(value[1], float):
                        # 小数の場合
                        effect_value[key] = round(random.uniform(value[0], value[1]), 2)
                    else:
                        # 整数の場合
                        effect_value[key] = random.randint(value[0], value[1])
                    
                    # 説明文のプレースホルダーを置換
                    description = description.replace(f"{{{key}}}", str(effect_value[key]))
                else:
                    effect_value[key] = value
        else:
            effect_value = effect_value_template
        
        return Skill(
            name=name,
            description=description,
            trigger_type=trigger_type,
            effect_type=effect_type,
            trigger_value=trigger_value,
            effect_value=effect_value
        )
    
    def _generate_lore(self, weapon_name: str, rarity: ItemRarity) -> str:
        """
        武器の背景ストーリーを生成
        
        Args:
            weapon_name: 武器の名前
            rarity: レア度
            
        Returns:
            str: 生成された背景ストーリー
        """
        lore_templates = [
            "{name}は、古代の{era}時代に{maker}によって作られたと言われている。{feature}を持ち、{hero}がこの武器を使って{feat}したという伝説が残っている。",
            "伝説によれば、{name}は{god}の力を宿した武器であり、{feature}を持つという。この武器を持つものは{blessing}を授かると言われている。",
            "{war}の際、{hero}がこの{name}を手にして戦場を駆け抜けた。{feature}を持つこの武器は、{effect}すると言われている。",
            "{name}には{curse}という呪いがかけられているという噂がある。しかし、その代わりに{blessing}という祝福も与えるとされる。"
        ]
        
        eras = ["黄金", "神話", "闇", "混沌", "創世", "終末"]
        makers = ["偉大な鍛冶師", "古代の賢者", "失われた文明", "神々", "妖精"]
        features = ["鋭い刃", "魔力を宿した刃", "不思議な輝き", "予知能力", "敵の弱点を見抜く力"]
        heroes = ["伝説の英雄", "古の王", "神に選ばれし者", "闇を打ち破る者", "予言の勇者"]
        feats = ["暗黒の魔王を打ち倒", "世界を救", "平和をもたら", "真の力を解放", "運命を変え"]
        gods = ["創造神", "戦神", "知恵の神", "太陽神", "月の女神"]
        blessings = ["無限の力", "不思議な知恵", "敵を倒す力", "傷を癒す力", "運命を変える力"]
        wars = ["大戦", "聖戦", "魔神戦争", "神々の戦い", "百年戦争"]
        effects = ["敵の心を恐怖で満た", "使い手の力を何倍にも高め", "周囲の魔力を吸収", "使い手を不死身にさせる", "時間を操る力を与え"]
        curses = ["使い手の寿命を削る", "魂を少しずつ奪う", "制御不能な力", "狂気をもたらす", "敵の呪い"]
        
        # レア度が高いほど複雑な背景ストーリー
        template = random.choice(lore_templates)
        
        # プレースホルダーの置換
        lore = template.format(
            name=weapon_name,
            era=random.choice(eras),
            maker=random.choice(makers),
            feature=random.choice(features),
            hero=random.choice(heroes),
            feat=random.choice(feats),
            god=random.choice(gods),
            blessing=random.choice(blessings),
            war=random.choice(wars),
            effect=random.choice(effects),
            curse=random.choice(curses)
        )
        
        # レア度に応じて追加の文章
        if rarity.value >= ItemRarity.EPIC.value:
            additional_lore = [
                f"多くの戦いを経て、{weapon_name}は今も失われていない。",
                f"{weapon_name}は使い手に選ばれるという。相応しくない者が手にすれば災いをもたらすだろう。",
                f"真の力を解放するには、特別な儀式が必要だという噂もある。"
            ]
            lore += " " + random.choice(additional_lore)
        
        return lore