# character_creator_enhanced.py
import pygame
import random
import os
import json
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from ui_system import Panel, Label, Button, ScrollPanel, ProgressBar
from unit import Unit
from constants import WeaponType
from skills import Skill, create_sample_skills
from movement_system import MovementType
from font_manager import get_font

class EnhancedRace:
    """拡張された種族クラス"""
    def __init__(self, name: str, stat_bonuses: Dict[str, int], allowed_factions: List[str], 
                 special_skills: List[str] = None, penalties: Dict[str, int] = None, 
                 description: str = "", icon_path: str = None, growth_modifiers: Dict[str, int] = None,
                 terrain_affinities: Dict[str, int] = None):
        self.name = name
        self.stat_bonuses = stat_bonuses
        self.allowed_factions = allowed_factions
        self.special_skills = special_skills or []
        self.penalties = penalties or {}
        self.description = description
        self.icon_path = icon_path
        self.growth_modifiers = growth_modifiers or {}  # 成長率への修正
        self.terrain_affinities = terrain_affinities or {}  # 地形との相性
        
        # 使用可能武器タイプ
        self.weapon_affinities = []
        
        # カスタム属性
        self.custom_attributes = {}
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（保存用）"""
        return {
            "name": self.name,
            "stat_bonuses": self.stat_bonuses,
            "allowed_factions": self.allowed_factions,
            "special_skills": self.special_skills,
            "penalties": self.penalties,
            "description": self.description,
            "icon_path": self.icon_path,
            "growth_modifiers": self.growth_modifiers,
            "terrain_affinities": self.terrain_affinities,
            "weapon_affinities": self.weapon_affinities,
            "custom_attributes": self.custom_attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EnhancedRace':
        """辞書からインスタンスを生成"""
        race = cls(
            name=data["name"],
            stat_bonuses=data.get("stat_bonuses", {}),
            allowed_factions=data.get("allowed_factions", []),
            special_skills=data.get("special_skills", []),
            penalties=data.get("penalties", {}),
            description=data.get("description", ""),
            icon_path=data.get("icon_path", None),
            growth_modifiers=data.get("growth_modifiers", {}),
            terrain_affinities=data.get("terrain_affinities", {})
        )
        race.weapon_affinities = data.get("weapon_affinities", [])
        race.custom_attributes = data.get("custom_attributes", {})
        return race

class EnhancedFaction:
    """拡張された所属クラス"""
    def __init__(self, name: str, stat_bonuses: Dict[str, int], allowed_races: List[str], 
                 allowed_alignments: List[str], allowed_classes: List[str], description: str = "",
                 icon_path: str = None, unique_skills: List[str] = None, 
                 growth_modifiers: Dict[str, int] = None, base_support_values: Dict[str, int] = None):
        self.name = name
        self.stat_bonuses = stat_bonuses
        self.allowed_races = allowed_races
        self.allowed_alignments = allowed_alignments
        self.allowed_classes = allowed_classes
        self.description = description
        self.icon_path = icon_path
        self.unique_skills = unique_skills or []  # 所属特有のスキル
        self.growth_modifiers = growth_modifiers or {}  # 成長率への修正
        self.base_support_values = base_support_values or {}  # 初期支援値
        
        # 外交関係（他勢力との関係性）
        self.diplomacy = {}
        
        # 勢力特有の建物/機能
        self.special_buildings = []
        
        # カスタム属性
        self.custom_attributes = {}
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（保存用）"""
        return {
            "name": self.name,
            "stat_bonuses": self.stat_bonuses,
            "allowed_races": self.allowed_races,
            "allowed_alignments": self.allowed_alignments,
            "allowed_classes": self.allowed_classes,
            "description": self.description,
            "icon_path": self.icon_path,
            "unique_skills": self.unique_skills,
            "growth_modifiers": self.growth_modifiers,
            "base_support_values": self.base_support_values,
            "diplomacy": self.diplomacy,
            "special_buildings": self.special_buildings,
            "custom_attributes": self.custom_attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EnhancedFaction':
        """辞書からインスタンスを生成"""
        faction = cls(
            name=data["name"],
            stat_bonuses=data.get("stat_bonuses", {}),
            allowed_races=data.get("allowed_races", []),
            allowed_alignments=data.get("allowed_alignments", []),
            allowed_classes=data.get("allowed_classes", []),
            description=data.get("description", ""),
            icon_path=data.get("icon_path", None),
            unique_skills=data.get("unique_skills", []),
            growth_modifiers=data.get("growth_modifiers", {}),
            base_support_values=data.get("base_support_values", {})
        )
        faction.diplomacy = data.get("diplomacy", {})
        faction.special_buildings = data.get("special_buildings", [])
        faction.custom_attributes = data.get("custom_attributes", {})
        return faction

class EnhancedClass:
    """拡張されたユニットクラス（職業）"""
    def __init__(self, name: str, base_stats: Dict[str, int], growth_rates: Dict[str, int],
                 weapon_types: List[WeaponType], movement_type: MovementType,
                 promotion_classes: List[str] = None, promotion_level: int = 10,
                 description: str = "", icon_path: str = None, skills_learned: Dict[int, str] = None,
                 terrain_bonuses: Dict[str, Dict[str, int]] = None):
        self.name = name
        self.base_stats = base_stats
        self.growth_rates = growth_rates
        self.weapon_types = weapon_types
        self.movement_type = movement_type
        self.promotion_classes = promotion_classes or []
        self.promotion_level = promotion_level
        self.description = description
        self.icon_path = icon_path
        self.skills_learned = skills_learned or {}  # レベルごとに習得するスキル
        self.terrain_bonuses = terrain_bonuses or {}  # 地形による特殊ボーナス
        
        # 特殊能力
        self.special_abilities = []
        
        # カスタム属性
        self.custom_attributes = {}
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（保存用）"""
        return {
            "name": self.name,
            "base_stats": self.base_stats,
            "growth_rates": self.growth_rates,
            "weapon_types": [wt.name for wt in self.weapon_types],
            "movement_type": self.movement_type.name,
            "promotion_classes": self.promotion_classes,
            "promotion_level": self.promotion_level,
            "description": self.description,
            "icon_path": self.icon_path,
            "skills_learned": self.skills_learned,
            "terrain_bonuses": self.terrain_bonuses,
            "special_abilities": self.special_abilities,
            "custom_attributes": self.custom_attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EnhancedClass':
        """辞書からインスタンスを生成"""
        # 武器タイプとMovementTypeの変換
        weapon_types = [WeaponType[wt] for wt in data.get("weapon_types", [])]
        movement_type = MovementType[data.get("movement_type", "INFANTRY")]
        
        unit_class = cls(
            name=data["name"],
            base_stats=data.get("base_stats", {}),
            growth_rates=data.get("growth_rates", {}),
            weapon_types=weapon_types,
            movement_type=movement_type,
            promotion_classes=data.get("promotion_classes", []),
            promotion_level=data.get("promotion_level", 10),
            description=data.get("description", ""),
            icon_path=data.get("icon_path", None),
            skills_learned=data.get("skills_learned", {}),
            terrain_bonuses=data.get("terrain_bonuses", {})
        )
        unit_class.special_abilities = data.get("special_abilities", [])
        unit_class.custom_attributes = data.get("custom_attributes", {})
        return unit_class

class CharacterPreset:
    """キャラクタープリセット"""
    def __init__(self, name: str, race: str, faction: str, alignment: str, unit_class: str,
                 stats: Dict[str, int] = None, skills: List[str] = None, equipment: List[str] = None,
                 growth_rates: Dict[str, int] = None, icon_path: str = None, description: str = "",
                 personality: Dict[str, Any] = None):
        self.name = name
        self.race = race
        self.faction = faction
        self.alignment = alignment
        self.unit_class = unit_class
        self.stats = stats or {}
        self.skills = skills or []
        self.equipment = equipment or []
        self.growth_rates = growth_rates or {}
        self.icon_path = icon_path
        self.description = description
        self.personality = personality or {}
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（保存用）"""
        return {
            "name": self.name,
            "race": self.race,
            "faction": self.faction,
            "alignment": self.alignment,
            "unit_class": self.unit_class,
            "stats": self.stats,
            "skills": self.skills,
            "equipment": self.equipment,
            "growth_rates": self.growth_rates,
            "icon_path": self.icon_path,
            "description": self.description,
            "personality": self.personality
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CharacterPreset':
        """辞書からインスタンスを生成"""
        return cls(
            name=data["name"],
            race=data["race"],
            faction=data["faction"],
            alignment=data["alignment"],
            unit_class=data["unit_class"],
            stats=data.get("stats", {}),
            skills=data.get("skills", []),
            equipment=data.get("equipment", []),
            growth_rates=data.get("growth_rates", {}),
            icon_path=data.get("icon_path", None),
            description=data.get("description", ""),
            personality=data.get("personality", {})
        )

class EnhancedCharacterCreator:
    """拡張版キャラクター作成システム"""
    def __init__(self, data_path="data/", skill_manager=None, support_system=None):
        self.data_path = data_path
        self.skill_manager = skill_manager
        self.support_system = support_system
        
        # フォルダ作成
        os.makedirs(os.path.join(data_path, "races"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "factions"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "classes"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "presets"), exist_ok=True)
        
        # 種族データ
        self.races = self._load_races()
        
        # 所属データ
        self.factions = self._load_factions()
        
        # 性格データ
        self.alignments = ["善", "普通", "悪"]
        
        # 職業データ
        self.classes = self._load_classes()
        
        # スキルデータ
        self.skills = create_sample_skills() if not skill_manager else skill_manager.get_all_skills()
        
        # カスタマイズ履歴
        self.creation_history = []
        
        # プリセット
        self.presets = self._load_presets()
    
    def _load_races(self) -> Dict[str, EnhancedRace]:
        """種族データをロード"""
        races = {}
        race_dir = os.path.join(self.data_path, "races")
        
        # 保存されたファイルがあればロード
        if os.path.exists(race_dir):
            for filename in os.listdir(race_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(race_dir, filename), "r", encoding="utf-8") as f:
                            race_data = json.load(f)
                            race = EnhancedRace.from_dict(race_data)
                            races[race.name] = race
                    except Exception as e:
                        print(f"種族データ読み込みエラー: {filename} - {e}")
        
        # データが読み込めなかった場合はデフォルトデータを使用
        if not races:
            races = self._initialize_default_races()
            self._save_races(races)
        
        return races
    
    def _save_races(self, races: Dict[str, EnhancedRace]):
        """種族データを保存"""
        race_dir = os.path.join(self.data_path, "races")
        os.makedirs(race_dir, exist_ok=True)
        
        for name, race in races.items():
            try:
                with open(os.path.join(race_dir, f"{name}.json"), "w", encoding="utf-8") as f:
                    json.dump(race.to_dict(), f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"種族データ保存エラー: {name} - {e}")
    
    def _initialize_default_races(self) -> Dict[str, EnhancedRace]:
        """デフォルトの種族データを初期化"""
        races = {}
        
        # 人間
        races["人間"] = EnhancedRace(
            name="人間",
            stat_bonuses={},  # ボーナスなし
            allowed_factions=["シュトロイゼル騎士団", "都市連合", "冒険者ギルド"],
            description="適応性が高く、あらゆる環境で活躍できる種族。特別な強みはないが、弱点も少ない。",
            growth_modifiers={"hp": 5, "strength": 5, "magic": 5, "skill": 5, "speed": 5, "luck": 5, "defense": 5, "resistance": 5}
        )
        
        # エルフ
        races["エルフ"] = EnhancedRace(
            name="エルフ",
            stat_bonuses={"speed": 5},
            penalties={"hp": -5, "defense": -3},
            allowed_factions=["冒険者ギルド"],
            description="長命で俊敏な森の民。魔法との親和性が高く、弓の名手が多い。",
            growth_modifiers={"magic": 10, "skill": 10, "speed": 15, "resistance": 10},
            terrain_affinities={"forest": 2, "desert": -1}
        )
        
        # 古代人
        races["古代人"] = EnhancedRace(
            name="古代人",
            stat_bonuses={"magic": 3, "resistance": 3},
            allowed_factions=["シュトロイゼル騎士団", "都市連合", "冒険者ギルド"],
            description="失われた古代文明の末裔。高度な知識を持ち、魔法の才能に恵まれている。",
            growth_modifiers={"magic": 15, "skill": 5, "resistance": 10},
            terrain_affinities={"ruins": 2}
        )
        
        # 妖精
        races["妖精"] = EnhancedRace(
            name="妖精",
            stat_bonuses={"magic": 3, "speed": 2},
            penalties={"hp": -2, "defense": -2},
            allowed_factions=["冒険者ギルド"],
            description="小柄で魔法に長けた自然の精霊。物理的な耐久力は低いが、魔法の才能は高い。",
            growth_modifiers={"magic": 20, "speed": 15, "luck": 10, "defense": -10, "hp": -10},
            terrain_affinities={"forest": 3, "mountain": 1}
        )
        
        # 獣人（犬）
        races["獣人（犬）"] = EnhancedRace(
            name="獣人（犬）",
            stat_bonuses={"hp": 2, "strength": 2, "defense": 2},
            penalties={"magic": -2, "resistance": -2},
            allowed_factions=["シュトロイゼル騎士団", "冒険者ギルド"],
            description="忠誠心が強く、体力に恵まれた犬の特性を持つ獣人。物理攻撃に優れるが、魔法は苦手。",
            growth_modifiers={"hp": 10, "strength": 10, "defense": 10, "magic": -10, "resistance": -5},
            terrain_affinities={"plain": 1, "forest": 1}
        )
        
        # 獣人（猫）
        races["獣人（猫）"] = EnhancedRace(
            name="獣人（猫）",
            stat_bonuses={"strength": 2, "skill": 2, "speed": 2},
            penalties={"magic": -2, "defense": -2},
            allowed_factions=["シュトロイゼル騎士団", "冒険者ギルド"],
            description="俊敏で器用な猫の特性を持つ獣人。攻撃と回避に優れるが、防御力は低め。",
            growth_modifiers={"strength": 5, "skill": 15, "speed": 15, "defense": -10},
            terrain_affinities={"forest": 2, "mountain": 1}
        )
        
        # 獣人（ウサギ）
        races["獣人（ウサギ）"] = EnhancedRace(
            name="獣人（ウサギ）",
            stat_bonuses={"speed": 5},
            penalties={"defense": -2, "resistance": -2},
            allowed_factions=["シュトロイゼル騎士団", "冒険者ギルド"],
            description="驚異的な俊敏性を持つウサギの特性を持つ獣人。素早さは群を抜くが、耐久力に難がある。",
            growth_modifiers={"speed": 20, "luck": 10, "defense": -5, "resistance": -5},
            terrain_affinities={"plain": 2, "forest": 1}
        )
        
        # 獣人（鳥）
        races["獣人（鳥）"] = EnhancedRace(
            name="獣人（鳥）",
            stat_bonuses={"speed": 1},
            penalties={"defense": -2},
            special_skills=["飛行能力"],
            allowed_factions=["シュトロイゼル騎士団", "冒険者ギルド"],
            description="翼を持ち、地形に関わらず移動できる鳥の特性を持つ獣人。防御力は低いが、機動力は最高。",
            growth_modifiers={"speed": 15, "skill": 10, "defense": -10},
            terrain_affinities={"mountain": 2}
        )
        
        # 機械
        races["機械"] = EnhancedRace(
            name="機械",
            stat_bonuses={"strength": 2, "defense": 2, "resistance": 2},
            special_skills=["エンジン稼働"],
            allowed_factions=["都市連合", "冒険者ギルド"],
            description="最先端技術で作られた人工生命体。物理攻撃と防御に優れるが、魔法との相性は個体による。",
            growth_modifiers={"hp": -5, "strength": 10, "defense": 15, "resistance": 10, "luck": -10},
            terrain_affinities={"water": -2}
        )
        
        return races
    
    def _load_factions(self) -> Dict[str, EnhancedFaction]:
        """所属データをロード"""
        factions = {}
        faction_dir = os.path.join(self.data_path, "factions")
        
        # 保存されたファイルがあればロード
        if os.path.exists(faction_dir):
            for filename in os.listdir(faction_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(faction_dir, filename), "r", encoding="utf-8") as f:
                            faction_data = json.load(f)
                            faction = EnhancedFaction.from_dict(faction_data)
                            factions[faction.name] = faction
                    except Exception as e:
                        print(f"所属データ読み込みエラー: {filename} - {e}")
        
        # データが読み込めなかった場合はデフォルトデータを使用
        if not factions:
            factions = self._initialize_default_factions()
            self._save_factions(factions)
        
        return factions
    
    def _save_factions(self, factions: Dict[str, EnhancedFaction]):
        """所属データを保存"""
        faction_dir = os.path.join(self.data_path, "factions")
        os.makedirs(faction_dir, exist_ok=True)
        
        for name, faction in factions.items():
            try:
                with open(os.path.join(faction_dir, f"{name}.json"), "w", encoding="utf-8") as f:
                    json.dump(faction.to_dict(), f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"所属データ保存エラー: {name} - {e}")
    
    def _initialize_default_factions(self) -> Dict[str, EnhancedFaction]:
        """デフォルトの所属データを初期化"""
        factions = {}
        
        # 都市連合
        factions["都市連合"] = EnhancedFaction(
            name="都市連合",
            stat_bonuses={"hp": 2, "strength": 2, "skill": 2, "defense": 2},
            allowed_races=["人間", "古代人", "機械"],
            allowed_alignments=["普通", "悪"],
            allowed_classes=["傭兵", "剣士", "重装兵", "アーチャー", "盗賊", "暗殺者", "マーチャント"],
            description="自己利益を追求する資本主義社会。技術力は高いが、人道的な価値観は低い。",
            growth_modifiers={"strength": 5, "skill": 5, "defense": 5},
            unique_skills=["商才", "交渉術"]
        )
        
        # シュトロイゼル騎士団
        factions["シュトロイゼル騎士団"] = EnhancedFaction(
            name="シュトロイゼル騎士団",
            stat_bonuses={"strength": 1, "magic": 2, "luck": 2, "resistance": 3},
            allowed_races=["人間", "古代人", "獣人（犬）", "獣人（猫）", "獣人（ウサギ）", "獣人（鳥）"],
            allowed_alignments=["普通", "善"],
            allowed_classes=["騎士", "ペガサスナイト", "魔道士", "僧侶", "賢者", "ヒーラー", "パラディン"],
            description="迫害から逃れた者たちが築いた騎士団。宗教的価値観を重んじ、魔法技術が発達している。",
            growth_modifiers={"magic": 5, "resistance": 10, "luck": 5},
            unique_skills=["信仰心", "魔法耐性"]
        )
        
        # 冒険者ギルド
        factions["冒険者ギルド"] = EnhancedFaction(
            name="冒険者ギルド",
            stat_bonuses={},  # ボーナスなし
            allowed_races=["人間", "エルフ", "古代人", "妖精", "獣人（犬）", "獣人（猫）", "獣人（ウサギ）", "獣人（鳥）", "機械"],
            allowed_alignments=["善", "普通", "悪"],
            allowed_classes=["傭兵", "剣士", "重装兵", "アーチャー", "盗賊", "暗殺者", "マーチャント", "騎士", "ペガサスナイト", "魔道士", "僧侶", "賢者", "ヒーラー", "パラディン"],
            description="特定の勢力に属さない自由な冒険者の集団。様々な種族や価値観を受け入れる。",
            growth_modifiers={"speed": 3, "luck": 5, "skill": 3},
            unique_skills=["宝探し", "サバイバル"]
        )
        
        return factions
    
    def _load_classes(self) -> Dict[str, EnhancedClass]:
        """職業データをロード"""
        classes = {}
        class_dir = os.path.join(self.data_path, "classes")
        
        # 保存されたファイルがあればロード
        if os.path.exists(class_dir):
            for filename in os.listdir(class_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(class_dir, filename), "r", encoding="utf-8") as f:
                            class_data = json.load(f)
                            unit_class = EnhancedClass.from_dict(class_data)
                            classes[unit_class.name] = unit_class
                    except Exception as e:
                        print(f"職業データ読み込みエラー: {filename} - {e}")
        
        # データが読み込めなかった場合はデフォルトデータを使用
        if not classes:
            classes = self._initialize_default_classes()
            self._save_classes(classes)
        
        return classes
    
    def _save_classes(self, classes: Dict[str, EnhancedClass]):
        """職業データを保存"""
        class_dir = os.path.join(self.data_path, "classes")
        os.makedirs(class_dir, exist_ok=True)
        
        for name, unit_class in classes.items():
            try:
                with open(os.path.join(class_dir, f"{name}.json"), "w", encoding="utf-8") as f:
                    json.dump(unit_class.to_dict(), f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"職業データ保存エラー: {name} - {e}")

    def _initialize_default_classes(self) -> Dict[str, EnhancedClass]:
        """デフォルトの職業データを初期化"""
        classes = {}
        
        # 剣士
        classes["剣士"] = EnhancedClass(
            name="剣士",
            base_stats={
                "hp": 18, "strength": 6, "magic": 0, "skill": 9, 
                "speed": 8, "luck": 4, "defense": 4, "resistance": 1
            },
            growth_rates={
                "hp": 70, "strength": 45, "magic": 10, "skill": 65,
                "speed": 60, "luck": 35, "defense": 30, "resistance": 20
            },
            weapon_types=[WeaponType.SWORD],
            movement_type=MovementType.INFANTRY,
            promotion_classes=["ソードマスター", "ヒーロー"],
            description="剣を主武器とする戦士。バランスの取れた能力を持ち、特に技と速さに優れる。",
            skills_learned={1: "剣の達人", 10: "流し斬り"}
        )
        
        # 重装兵
        classes["重装兵"] = EnhancedClass(
            name="重装兵",
            base_stats={
                "hp": 22, "strength": 9, "magic": 0, "skill": 4, 
                "speed": 3, "luck": 2, "defense": 10, "resistance": 2
            },
            growth_rates={
                "hp": 90, "strength": 65, "magic": 5, "skill": 30,
                "speed": 20, "luck": 25, "defense": 70, "resistance": 25
            },
            weapon_types=[WeaponType.LANCE, WeaponType.AXE],
            movement_type=MovementType.ARMORED,
            promotion_classes=["ジェネラル", "グレートナイト"],
            description="重装備の騎士。高い防御力と攻撃力を持つが、移動力と速さが低い。",
            skills_learned={1: "大盾", 10: "鉄壁"}
        )
        
        # 傭兵
        classes["傭兵"] = EnhancedClass(
            name="傭兵",
            base_stats={
                "hp": 20, "strength": 8, "magic": 0, "skill": 6, 
                "speed": 6, "luck": 3, "defense": 5, "resistance": 1
            },
            growth_rates={
                "hp": 80, "strength": 60, "magic": 10, "skill": 50,
                "speed": 45, "luck": 30, "defense": 40, "resistance": 20
            },
            weapon_types=[WeaponType.SWORD, WeaponType.AXE],
            movement_type=MovementType.INFANTRY,
            promotion_classes=["ヒーロー", "戦士"],
            description="金のために戦う兵士。剣と斧を扱い、バランスの良い成長が見込める。",
            skills_learned={1: "追撃", 10: "連撃"}
        )
        
        # アーチャー
        classes["アーチャー"] = EnhancedClass(
            name="アーチャー",
            base_stats={
                "hp": 17, "strength": 5, "magic": 0, "skill": 8, 
                "speed": 7, "luck": 4, "defense": 4, "resistance": 2
            },
            growth_rates={
                "hp": 65, "strength": 45, "magic": 10, "skill": 60,
                "speed": 55, "luck": 40, "defense": 30, "resistance": 25
            },
            weapon_types=[WeaponType.BOW],
            movement_type=MovementType.INFANTRY,
            promotion_classes=["スナイパー", "ボウナイト"],
            description="弓を専門とする兵士。遠距離攻撃が可能だが、近接戦闘は苦手。",
            skills_learned={1: "狙撃", 10: "必中"}
        )
        
        # 魔道士
        classes["魔道士"] = EnhancedClass(
            name="魔道士",
            base_stats={
                "hp": 16, "strength": 2, "magic": 7, "skill": 6, 
                "speed": 6, "luck": 4, "defense": 2, "resistance": 7
            },
            growth_rates={
                "hp": 60, "strength": 15, "magic": 65, "skill": 50,
                "speed": 45, "luck": 35, "defense": 20, "resistance": 55
            },
            weapon_types=[WeaponType.MAGIC],
            movement_type=MovementType.MAGE,
            promotion_classes=["賢者", "ダークマージ"],
            description="攻撃魔法を操る魔術師。高い魔力と魔防を持つが、物理防御は低い。",
            skills_learned={1: "魔力の一撃", 10: "魔法貫通"}
        )
        
        # 僧侶
        classes["僧侶"] = EnhancedClass(
            name="僧侶",
            base_stats={
                "hp": 17, "strength": 3, "magic": 6, "skill": 5, 
                "speed": 5, "luck": 7, "defense": 3, "resistance": 8
            },
            growth_rates={
                "hp": 65, "strength": 20, "magic": 55, "skill": 40,
                "speed": 40, "luck": 50, "defense": 25, "resistance": 60
            },
            weapon_types=[WeaponType.STAFF],
            movement_type=MovementType.INFANTRY,
            promotion_classes=["ビショップ", "ヴァルキリー"],
            description="回復魔法を操る聖職者。高い魔防と幸運を持ち、味方を回復できる。",
            skills_learned={1: "祈り", 10: "聖盾"}
        )
        
        # 他の職業も同様に追加
        
        return classes
    
    def _load_presets(self) -> Dict[str, CharacterPreset]:
        """キャラクタープリセットをロード"""
        presets = {}
        preset_dir = os.path.join(self.data_path, "presets")
        
        # 保存されたファイルがあればロード
        if os.path.exists(preset_dir):
            for filename in os.listdir(preset_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(preset_dir, filename), "r", encoding="utf-8") as f:
                            preset_data = json.load(f)
                            preset = CharacterPreset.from_dict(preset_data)
                            presets[preset.name] = preset
                    except Exception as e:
                        print(f"プリセットデータ読み込みエラー: {filename} - {e}")
        
        # データが読み込めなかった場合はデフォルトデータを使用
        if not presets:
            presets = self._initialize_default_presets()
            self._save_presets(presets)
        
        return presets
    
    def _save_presets(self, presets: Dict[str, CharacterPreset]):
        """プリセットデータを保存"""
        preset_dir = os.path.join(self.data_path, "presets")
        os.makedirs(preset_dir, exist_ok=True)
        
        for name, preset in presets.items():
            try:
                with open(os.path.join(preset_dir, f"{name}.json"), "w", encoding="utf-8") as f:
                    json.dump(preset.to_dict(), f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"プリセット保存エラー: {name} - {e}")
    
    def _initialize_default_presets(self) -> Dict[str, CharacterPreset]:
        """デフォルトのプリセットを初期化"""
        presets = {}
        
        # ヒーロー的キャラクター
        presets["勇者アレクス"] = CharacterPreset(
            name="勇者アレクス",
            race="人間",
            faction="シュトロイゼル騎士団",
            alignment="善",
            unit_class="剣士",
            stats={"hp": 20, "strength": 7, "skill": 10, "speed": 9, "luck": 6, "defense": 5, "resistance": 3},
            skills=["剣の達人", "勇気"],
            equipment=["鋼の剣", "鉄の剣", "傷薬"],
            description="正義感が強く、困っている人を見過ごせない性格。幼い頃から剣術の才能を見せ、多くの人に慕われている。",
            personality={"正義感": 10, "勇気": 9, "忠誠心": 8, "信頼性": 9}
        )
        
        # 魔法使い
        presets["魔道師リリア"] = CharacterPreset(
            name="魔道師リリア",
            race="古代人",
            faction="シュトロイゼル騎士団",
            alignment="普通",
            unit_class="魔道士",
            stats={"hp": 17, "magic": 9, "skill": 8, "speed": 7, "luck": 5, "defense": 2, "resistance": 8},
            skills=["魔力の一撃", "魔法看破"],
            equipment=["ファイアー", "サンダー", "魔力のしずく"],
            description="好奇心旺盛で物事の真理を追求する学者タイプ。魔法の研究に没頭し、古代の魔法書を解読している。",
            personality={"好奇心": 10, "冷静さ": 8, "知性": 9, "孤独": 7}
        )
        
        # 盗賊キャラクター
        presets["怪盗ジャック"] = CharacterPreset(
            name="怪盗ジャック",
            race="人間",
            faction="冒険者ギルド",
            alignment="普通",
            unit_class="盗賊",
            stats={"hp": 18, "strength": 6, "skill": 10, "speed": 12, "luck": 7, "defense": 4, "resistance": 3},
            skills=["鍵開け", "盗み"],
            equipment=["鋼の短剣", "盗賊の鍵", "煙玉"],
            description="自由を愛する盗賊。権力者からのみ盗みを働き、貧しい人々に分け与えることもある。技術は一流。",
            personality={"自由": 10, "反権力": 8, "義侠心": 7, "機転": 9}
        )
        
        return presets
    
    def get_compatible_classes(self, race_name: str, faction_name: str, alignment: str) -> List[str]:
        """指定された種族、所属、性格に対応する職業リストを取得"""
        race = self.races.get(race_name)
        faction = self.factions.get(faction_name)
        
        if not race or not faction:
            return []
        
        # 種族が所属可能な勢力かチェック
        if faction_name not in race.allowed_factions:
            return []
            
        # 性格が所属に合っているかチェック
        if alignment not in faction.allowed_alignments:
            return []
        
        # 対応する職業を返す
        return faction.allowed_classes
    
    def create_character(self, name: str, race_name: str, faction_name: str, 
                         alignment: str, class_name: str, level: int = 1,
                         custom_stats: Dict[str, int] = None) -> Unit:
        """キャラクターを生成する"""
        race = self.races.get(race_name)
        faction = self.factions.get(faction_name)
        class_data = self.classes.get(class_name)
        
        if not race or not faction or not class_data:
            return None
        
        # ベースステータスの計算
        # 職業基本値 + 種族ボーナス + 所属ボーナス
        
        stats = {
            "hp": class_data.base_stats.get("hp", 18),
            "strength": class_data.base_stats.get("strength", 5),
            "magic": class_data.base_stats.get("magic", 0),
            "skill": class_data.base_stats.get("skill", 5),
            "speed": class_data.base_stats.get("speed", 5),
            "luck": class_data.base_stats.get("luck", 3),
            "defense": class_data.base_stats.get("defense", 4),
            "resistance": class_data.base_stats.get("resistance", 2)
        }
        
        # 種族ボーナスの適用
        for stat, value in race.stat_bonuses.items():
            if stat in stats:
                stats[stat] += value
        
        # 種族ペナルティの適用
        for stat, value in race.penalties.items():
            if stat in stats:
                stats[stat] += value
        
        # 所属ボーナスの適用
        for stat, value in faction.stat_bonuses.items():
            if stat in stats:
                stats[stat] += value
        
        # カスタムステータスがあれば適用
        if custom_stats:
            for stat, value in custom_stats.items():
                if stat in stats:
                    stats[stat] = value
        
        # 成長率の計算（職業 + 種族修正 + 所属修正）
        growth_rates = class_data.growth_rates.copy()
        
        # 種族の成長率修正
        for stat, value in race.growth_modifiers.items():
            if stat in growth_rates:
                growth_rates[stat] += value
        
        # 所属の成長率修正
        for stat, value in faction.growth_modifiers.items():
            if stat in growth_rates:
                growth_rates[stat] += value
        
        # レベルアップによる成長（レベル2以上の場合）
        if level > 1:
            for i in range(1, level):
                for stat, growth in growth_rates.items():
                    # 成長率に基づく乱数判定
                    if random.randint(1, 100) <= growth:
                        stats[stat] += 1
        
        # 最低値を保証
        for stat in stats:
            stats[stat] = max(1, stats[stat])
        
        # 移動力を設定
        movement = 5  # デフォルト
        if hasattr(class_data, "movement"):
            movement = class_data.movement
        
        # ユニットの生成
        unit = Unit(
            name=name,
            unit_class=class_name,
            level=level,
            hp=stats["hp"],
            strength=stats["strength"],
            magic=stats["magic"],
            skill=stats["skill"],
            speed=stats["speed"],
            luck=stats["luck"],
            defense=stats["defense"],
            resistance=stats["resistance"],
            movement=movement,
            team=0,  # プレイヤーチーム
            weapons=[],  # 武器は別途設定
            movement_type=class_data.movement_type
        )
        
        # スキルの設定
        # レベルに応じたスキルを習得
        if class_data.skills_learned:
            for level_req, skill_name in class_data.skills_learned.items():
                if level >= int(level_req) and self.skill_manager:
                    skill = self.skill_manager.get_skill_by_name(skill_name)
                    if skill:
                        unit.add_skill(skill)
        
        # 種族特性スキルの追加
        if race.special_skills and self.skill_manager:
            for skill_name in race.special_skills:
                skill = self.skill_manager.get_skill_by_name(skill_name)
                if skill:
                    unit.add_skill(skill)
        
        # 所属特有スキルの追加
        if faction.unique_skills and self.skill_manager:
            for skill_name in faction.unique_skills:
                skill = self.skill_manager.get_skill_by_name(skill_name)
                if skill:
                    unit.add_skill(skill)
        
        # メタデータを追加
        unit.race = race_name
        unit.faction = faction_name
        unit.alignment = alignment
        unit.growth_rates = growth_rates
        
        # 支援関係の初期化
        if self.support_system:
            self.support_system.register_character(unit.name, {
                "race": race_name,
                "faction": faction_name,
                "alignment": alignment
            })
        
        return unit
    
    def add_default_equipment(self, unit: Unit):
        """ユニットに職業に応じたデフォルト装備を追加"""
        # 職業に基づいた装備を追加（実装例）
        weapon_types = []
        if unit.unit_class in self.classes:
            weapon_types = self.classes[unit.unit_class].weapon_types
        
        # 最適な武器を選択
        from weapon import Weapon
        
        # 簡易的な実装（実際のゲームではより複雑なロジックが必要）
        if WeaponType.SWORD in weapon_types:
            unit.weapons.append(Weapon("鉄の剣", WeaponType.SWORD, 5, 90, 0, 5, 1, 1, 45))
            unit.equipped_weapon = unit.weapons[0]
        elif WeaponType.LANCE in weapon_types:
            unit.weapons.append(Weapon("鉄の槍", WeaponType.LANCE, 6, 80, 0, 7, 1, 1, 45))
            unit.equipped_weapon = unit.weapons[0]
        elif WeaponType.AXE in weapon_types:
            unit.weapons.append(Weapon("鉄の斧", WeaponType.AXE, 8, 70, 0, 10, 1, 1, 45))
            unit.equipped_weapon = unit.weapons[0]
        elif WeaponType.BOW in weapon_types:
            unit.weapons.append(Weapon("鉄の弓", WeaponType.BOW, 6, 85, 0, 5, 2, 2, 45))
            unit.equipped_weapon = unit.weapons[0]
        elif WeaponType.MAGIC in weapon_types:
            unit.weapons.append(Weapon("ファイアー", WeaponType.MAGIC, 5, 90, 0, 4, 1, 2, 40))
            unit.equipped_weapon = unit.weapons[0]
        elif WeaponType.STAFF in weapon_types:
            unit.weapons.append(Weapon("ヒールの杖", WeaponType.STAFF, 0, 100, 0, 2, 1, 1, 30))
            unit.equipped_weapon = unit.weapons[0]
    
    def generate_random_name(self, race: str, faction: str) -> str:
        """ランダムな名前を生成する"""
        # 種族や所属に応じた名前の生成ロジック
        race_prefixes = {
            "人間": ["アレックス", "マーク", "エレン", "サラ", "ジョン", "マリア", "トーマス", "レイチェル"],
            "エルフ": ["エルロンド", "レゴラス", "アリエル", "エラニア", "セレン", "タリエル", "フィンダリアス"],
            "古代人": ["アズラエル", "メトセラ", "エノク", "セラフィナ", "ザカリア", "リリス", "ノア"],
            "妖精": ["ピクシー", "ティンク", "フェイ", "ブルーム", "スプライト", "シマー", "グリッター"],
            "獣人（犬）": ["ファング", "ハウル", "バーク", "ルーファス", "ルナ", "シャドウ", "ウルフ"],
            "獣人（猫）": ["ニャン", "ミャウ", "プーマ", "ティグラ", "レオ", "フェリクス", "キティ"],
            "獣人（ウサギ）": ["ホップ", "バニー", "フロップ", "コットン", "タフト", "スキップ", "ジャンプ"],
            "獣人（鳥）": ["ホーク", "タロン", "ウィング", "スイフト", "レイヴン", "カイト", "フラッター"],
            "機械": ["メック", "ギア", "コグ", "バイト", "サーキット", "ワイヤー", "ボルト", "ナノ"],
        }
        
        faction_suffixes = {
            "都市連合": ["フォージ", "テック", "スティール", "キャピタル", "クレジット", "プロフィット"],
            "シュトロイゼル騎士団": ["ライト", "フェイス", "セイント", "ブレイブ", "ノーブル", "ピュア"],
            "冒険者ギルド": ["ワンダラー", "シーカー", "トレイル", "クエスト", "フリー"]
        }
        
        race_list = race_prefixes.get(race, race_prefixes["人間"])
        faction_list = faction_suffixes.get(faction, faction_suffixes["冒険者ギルド"])
        
        first_name = random.choice(race_list)
        if random.random() < 0.5:  # 50%の確率でサフィックスを追加
            last_name = random.choice(faction_list)
            return f"{first_name} {last_name}"
        return first_name
    
    def generate_random_character(self, level_range: Tuple[int, int] = (1, 5)) -> Unit:
        """ランダムなキャラクターを生成する"""
        # ランダムな種族
        race_name = random.choice(list(self.races.keys()))
        race = self.races[race_name]
        
        # 種族に対応した所属をランダムに選択
        available_factions = race.allowed_factions
        faction_name = random.choice(available_factions)
        faction = self.factions[faction_name]
        
        # 性格をランダムに選択（所属に合う性格のみ）
        alignment = random.choice(faction.allowed_alignments)
        
        # 職業をランダムに選択
        available_classes = self.get_compatible_classes(race_name, faction_name, alignment)
        if not available_classes:
            # 互換性のある職業がない場合はデフォルト職業を使用
            class_name = "傭兵" if faction_name == "都市連合" else "騎士" if faction_name == "シュトロイゼル騎士団" else "傭兵"
        else:
            class_name = random.choice(available_classes)
        
        # レベルをランダムに決定
        level = random.randint(level_range[0], level_range[1])
        
        # 名前を生成
        name = self.generate_random_name(race_name, faction_name)
        
        # キャラクター生成
        unit = self.create_character(name, race_name, faction_name, alignment, class_name, level)
        
        # デフォルト装備を追加
        self.add_default_equipment(unit)
        
        return unit
    
    def save_character_preset(self, unit: Unit, description: str = "") -> bool:
        """ユニットをプリセットとして保存"""
        if not unit:
            return False
        
        # プリセットデータの作成
        equipment = []
        if unit.weapons:
            equipment = [weapon.name for weapon in unit.weapons]
        
        skills = []
        if hasattr(unit, 'skills') and unit.skills:
            skills = [skill.name for skill in unit.skills]
        
        # 成長率データを取得
        growth_rates = {}
        if hasattr(unit, 'growth_rates'):
            growth_rates = unit.growth_rates
        
        preset = CharacterPreset(
            name=unit.name,
            race=getattr(unit, 'race', "人間"),
            faction=getattr(unit, 'faction', "冒険者ギルド"),
            alignment=getattr(unit, 'alignment', "普通"),
            unit_class=unit.unit_class,
            stats={
                "hp": unit.max_hp,
                "strength": unit.strength,
                "magic": unit.magic,
                "skill": unit.skill,
                "speed": unit.speed,
                "luck": unit.luck,
                "defense": unit.defense,
                "resistance": unit.resistance
            },
            skills=skills,
            equipment=equipment,
            growth_rates=growth_rates,
            description=description
        )
        
        # プリセットを保存
        self.presets[unit.name] = preset
        self._save_presets(self.presets)
        
        return True
    
    def load_character_preset(self, preset_name: str) -> Unit:
        """プリセットからキャラクターを生成"""
        if preset_name not in self.presets:
            return None
        
        preset = self.presets[preset_name]
        
        # プリセットからキャラクターを生成
        unit = self.create_character(
            preset.name,
            preset.race,
            preset.faction,
            preset.alignment,
            preset.unit_class,
            1,  # レベルは後で設定
            preset.stats
        )
        
        # 武器と装備の追加
        # 実際のゲームでは装備管理システムを使用
        
        return unit
    
    def get_creation_history(self) -> List[Unit]:
        """作成履歴を取得"""
        return self.creation_history
    
    def add_to_history(self, unit: Unit):
        """作成履歴に追加"""
        self.creation_history.append(unit)
        # 履歴が長すぎる場合は古いものを削除
        if len(self.creation_history) > 10:
            self.creation_history.pop(0)


class EnhancedCharacterCreationWindow(Panel):
    """拡張版キャラクター作成ウィンドウ"""
    def __init__(self, x, y, width, height, character_creator, game_manager, on_create=None, on_close=None):
        super().__init__(x, y, width, height, (40, 40, 50), (255, 255, 255), 2, 230)
        self.character_creator = character_creator
        self.game_manager = game_manager
        self.on_create = on_create
        self.on_close = on_close
        
        # フォント
        self.title_font = get_font(30)
        self.header_font = get_font(24)
        self.normal_font = get_font(20)
        self.small_font = get_font(16)
        
        # 選択状態
        self.selected_race = None
        self.selected_faction = None
        self.selected_alignment = None
        self.selected_class = None
        self.character_name = ""
        self.character_level = 1
        
        # 各パネル
        self.race_panel = None
        self.faction_panel = None
        self.alignment_panel = None
        self.class_panel = None
        self.stats_panel = None
        self.preview_panel = None
        
        # 情報パネル
        self.race_info_panel = None
        self.faction_info_panel = None
        self.class_info_panel = None
        
        # 詳細タブパネル
        self.presets_panel = None
        self.history_panel = None
        
        # タブ管理
        self.current_tab = "create"  # create, presets, history
        
        # キャラクタープレビュー
        self.preview_unit = None
        
        # UIセットアップ
        self._setup_ui()
    
    def _setup_ui(self):
        """UIセットアップ"""
        # タイトル
        title_label = Label(self.width // 2, 20, "キャラクター作成", self.title_font, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # 閉じるボタン
        close_btn = Button(self.width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close_window)
        self.add_child(close_btn)
        
        # タブボタン
        tab_width = 150
        tab_x1 = self.width // 2 - tab_width - 10
        tab_x2 = self.width // 2 - tab_width // 2
        tab_x3 = self.width // 2 + 10
        
        create_tab = Button(tab_x1, 60, tab_width, 30, "新規作成", None, 20,
                          (60, 100, 60), (255, 255, 255), (80, 150, 80),
                          (0, 0, 0), 1, lambda: self.change_tab("create"))
        self.add_child(create_tab)
        
        presets_tab = Button(tab_x2, 60, tab_width, 30, "プリセット", None, 20,
                           (60, 60, 100), (255, 255, 255), (80, 80, 150),
                           (0, 0, 0), 1, lambda: self.change_tab("presets"))
        self.add_child(presets_tab)
        
        history_tab = Button(tab_x3, 60, tab_width, 30, "履歴", None, 20,
                           (100, 60, 100), (255, 255, 255), (150, 80, 150),
                           (0, 0, 0), 1, lambda: self.change_tab("history"))
        self.add_child(history_tab)
        
        # コンテンツパネル
        content_panel = Panel(20, 100, self.width - 40, self.height - 120, (40, 40, 50), (0, 0, 0), 1, 200)
        self.add_child(content_panel)
        self.content_panel = content_panel
        
        # 新規作成タブの内容を初期表示
        self._setup_create_tab()
    
    def change_tab(self, tab_name):
        """タブを切り替え"""
        if self.current_tab == tab_name:
            return
        
        self.current_tab = tab_name
        self.content_panel.clear_children()
        
        if tab_name == "create":
            self._setup_create_tab()
        elif tab_name == "presets":
            self._setup_presets_tab()
        elif tab_name == "history":
            self._setup_history_tab()
    
    def _setup_create_tab(self):
        """新規作成タブの内容をセットアップ"""
        # 左サイド（種族・所属・性格・職業選択）
        left_panel = Panel(0, 0, self.content_panel.width // 2 - 5, self.content_panel.height, (40, 40, 50), None, 0, 0)
        self.content_panel.add_child(left_panel)
        
        # 種族選択パネル
        race_panel = ScrollPanel(0, 0, left_panel.width, 150, 300, (50, 50, 60), (0, 0, 0), 1, 220)
        left_panel.add_child(race_panel)
        self.race_panel = race_panel
        
        race_label = Label(race_panel.width // 2, 5, "種族", None, 24, (255, 255, 200), None, "center")
        race_panel.add_child(race_label)
        
        # 種族情報パネル
        race_info_panel = RaceInfoPanel(0, 155, left_panel.width, 180)
        left_panel.add_child(race_info_panel)
        self.race_info_panel = race_info_panel
        
        # 所属選択パネル
        faction_panel = ScrollPanel(0, 340, left_panel.width, 150, 300, (50, 50, 60), (0, 0, 0), 1, 220)
        left_panel.add_child(faction_panel)
        self.faction_panel = faction_panel
        
        faction_label = Label(faction_panel.width // 2, 5, "所属", None, 24, (255, 255, 200), None, "center")
        faction_panel.add_child(faction_label)
        
        # 所属情報パネル
        faction_info_panel = FactionInfoPanel(0, 495, left_panel.width, 180)
        left_panel.add_child(faction_info_panel)
        self.faction_info_panel = faction_info_panel
        
        # 右サイド（性格・職業選択とプレビュー）
        right_panel = Panel(self.content_panel.width // 2 + 5, 0, self.content_panel.width // 2 - 5, self.content_panel.height, (40, 40, 50), None, 0, 0)
        self.content_panel.add_child(right_panel)
        
        # 性格選択パネル
        alignment_panel = Panel(0, 0, right_panel.width, 80, (50, 50, 60), (0, 0, 0), 1, 220)
        right_panel.add_child(alignment_panel)
        self.alignment_panel = alignment_panel
        
        alignment_label = Label(alignment_panel.width // 2, 5, "性格", None, 24, (255, 255, 200), None, "center")
        alignment_panel.add_child(alignment_label)
        
        # 職業選択パネル
        class_panel = ScrollPanel(0, 85, right_panel.width, 150, 300, (50, 50, 60), (0, 0, 0), 1, 220)
        right_panel.add_child(class_panel)
        self.class_panel = class_panel
        
        class_label = Label(class_panel.width // 2, 5, "職業", None, 24, (255, 255, 200), None, "center")
        class_panel.add_child(class_label)
        
        # 職業情報パネル
        class_info_panel = ClassInfoPanel(0, 240, right_panel.width, 180)
        right_panel.add_child(class_info_panel)
        self.class_info_panel = class_info_panel
        
        # 名前入力
        name_label = Label(right_panel.width // 4, 425, "名前", None, 24, (255, 255, 200), None, "center")
        right_panel.add_child(name_label)
        
        self.name_input = Label(right_panel.width // 4, 455, "クリックして入力", None, 20, (200, 200, 255), None, "center")
        right_panel.add_child(self.name_input)
        self.name_input.handle_event = lambda event: self.prompt_name_input() if event.type == pygame.MOUSEBUTTONDOWN else False
        
        # レベル選択
        level_label = Label(right_panel.width * 3 // 4, 425, "レベル", None, 24, (255, 255, 200), None, "center")
        right_panel.add_child(level_label)
        
        level_down_btn = Button(right_panel.width * 3 // 4 - 50, 455, 30, 30, "-", None, 20,
                              (60, 60, 100), (255, 255, 255), (80, 80, 150),
                              (0, 0, 0), 1, lambda: self.change_level(-1))
        right_panel.add_child(level_down_btn)
        
        self.level_value = Label(right_panel.width * 3 // 4, 455, "1", None, 20, (255, 255, 255), None, "center")
        right_panel.add_child(self.level_value)
        
        level_up_btn = Button(right_panel.width * 3 // 4 + 20, 455, 30, 30, "+", None, 20,
                            (60, 60, 100), (255, 255, 255), (80, 80, 150),
                            (0, 0, 0), 1, lambda: self.change_level(1))
        right_panel.add_child(level_up_btn)
        
        # プレビューボタン
        preview_btn = Button(right_panel.width // 2 - 60, 490, 120, 40, "プレビュー", None, 20,
                           (60, 100, 150), (255, 255, 255), (80, 130, 180),
                           (0, 0, 0), 1, self.show_preview)
        right_panel.add_child(preview_btn)
        
        # 作成ボタン
        create_btn = Button(right_panel.width // 2 - 60, 540, 120, 40, "作成", None, 24,
                          (60, 100, 60), (255, 255, 255), (80, 150, 80),
                          (0, 0, 0), 1, self.create_character)
        right_panel.add_child(create_btn)
        self.create_btn = create_btn
        
        # コスト表示
        self.cost_label = Label(right_panel.width // 2, 590, "コスト: 1000G", None, 20, (255, 255, 0), None, "center")
        right_panel.add_child(self.cost_label)
        
        # ランダム生成ボタン
        random_btn = Button(right_panel.width // 2 - 60, 620, 120, 40, "ランダム", None, 20,
                          (150, 100, 60), (255, 255, 255), (180, 130, 80),
                          (0, 0, 0), 1, self.generate_random)
        right_panel.add_child(random_btn)
        
        # 選択肢の更新
        self.update_race_options()
        self.update_faction_options()
        self.update_alignment_options()
        self.update_class_options()
        
        # ボタンの初期状態
        self.create_btn.set_active(False)
    
    def _setup_presets_tab(self):
        """プリセットタブの内容をセットアップ"""
        # プリセット一覧パネル
        presets_panel = PresetPanel(0, 0, self.content_panel.width // 2 - 5, self.content_panel.height,
                                  self.character_creator.presets, self.load_preset)
        self.content_panel.add_child(presets_panel)
        self.presets_panel = presets_panel
        
        # プレビューパネル
        preview_panel = UnitPreviewPanel(self.content_panel.width // 2 + 5, 0,
                                       self.content_panel.width // 2 - 5, self.content_panel.height)
        self.content_panel.add_child(preview_panel)
        self.preview_panel = preview_panel
    
    def _setup_history_tab(self):
        """履歴タブの内容をセットアップ"""
        # 履歴一覧パネル
        history_panel = HistoryPanel(0, 0, self.content_panel.width // 2 - 5, self.content_panel.height,
                                   self.character_creator.get_creation_history(), self.load_from_history)
        self.content_panel.add_child(history_panel)
        self.history_panel = history_panel
        
        # プレビューパネル
        preview_panel = UnitPreviewPanel(self.content_panel.width // 2 + 5, 0,
                                       self.content_panel.width // 2 - 5, self.content_panel.height)
        self.content_panel.add_child(preview_panel)
        self.preview_panel = preview_panel
    
    def update_race_options(self):
        """種族選択肢を更新"""
        self.race_panel.clear_children()
        
        # タイトル
        race_label = Label(self.race_panel.width // 2, 5, "種族", None, 24, (255, 255, 200), None, "center")
        self.race_panel.add_child(race_label)
        
        y_offset = 40
        for race_name, race in self.character_creator.races.items():
            race_btn = Button(10, y_offset, self.race_panel.width - 20, 30, race_name, None, 18,
                            (60, 60, 80), (255, 255, 255), (100, 100, 150),
                            (0, 0, 0), 1, lambda r=race_name: self.select_race(r))
            
            # 現在選択中の種族をハイライト
            if race_name == self.selected_race:
                race_btn.color = (100, 100, 150)
            
            self.race_panel.add_child(race_btn)
            y_offset += 40
        
        self.race_panel.update_content_height()
    
    def update_faction_options(self):
        """所属選択肢を更新"""
        self.faction_panel.clear_children()
        
        # タイトル
        faction_label = Label(self.faction_panel.width // 2, 5, "所属", None, 24, (255, 255, 200), None, "center")
        self.faction_panel.add_child(faction_label)
        
        y_offset = 40
        for faction_name, faction in self.character_creator.factions.items():
            # 選択中の種族が所属可能な勢力のみ表示
            if self.selected_race is None or faction_name in self.character_creator.races[self.selected_race].allowed_factions:
                faction_btn = Button(10, y_offset, self.faction_panel.width - 20, 30, faction_name, None, 18,
                                   (60, 60, 80), (255, 255, 255), (100, 100, 150),
                                   (0, 0, 0), 1, lambda f=faction_name: self.select_faction(f))
                
                # 現在選択中の所属をハイライト
                if faction_name == self.selected_faction:
                    faction_btn.color = (100, 100, 150)
                
                self.faction_panel.add_child(faction_btn)
                y_offset += 40
        
        self.faction_panel.update_content_height()
    
    def update_alignment_options(self):
        """性格選択肢を更新"""
        self.alignment_panel.clear_children()
        
        # タイトル
        alignment_label = Label(self.alignment_panel.width // 2, 5, "性格", None, 24, (255, 255, 200), None, "center")
        self.alignment_panel.add_child(alignment_label)
        
        # 性格ボタン
        btn_width = self.alignment_panel.width // 3 - 10
        x_pos = [5, self.alignment_panel.width // 2 - btn_width // 2, self.alignment_panel.width - btn_width - 5]
        
        for i, alignment in enumerate(self.character_creator.alignments):
            # 選択中の所属が許可する性格のみアクティブ
            active = True
            color = (60, 60, 80)
            if self.selected_faction:
                if alignment not in self.character_creator.factions[self.selected_faction].allowed_alignments:
                    active = False
                    color = (40, 40, 40)
            
            alignment_btn = Button(x_pos[i], 40, btn_width, 30, alignment, None, 18,
                                  color, (255, 255, 255), (100, 100, 150),
                                  (0, 0, 0), 1, lambda a=alignment: self.select_alignment(a))
            
            # 現在選択中の性格をハイライト
            if alignment == self.selected_alignment:
                alignment_btn.color = (100, 100, 150)
            
            alignment_btn.set_active(active)
            self.alignment_panel.add_child(alignment_btn)
    
    def update_class_options(self):
        """職業選択肢を更新"""
        self.class_panel.clear_children()
        
        # タイトル
        class_label = Label(self.class_panel.width // 2, 5, "職業", None, 24, (255, 255, 200), None, "center")
        self.class_panel.add_child(class_label)
        
        # 種族、所属、性格が全て選択されている場合のみ表示
        y_offset = 40
        if self.selected_race and self.selected_faction and self.selected_alignment:
            compatible_classes = self.character_creator.get_compatible_classes(
                self.selected_race, self.selected_faction, self.selected_alignment
            )
            
            for class_name in compatible_classes:
                if class_name in self.character_creator.classes:
                    class_btn = Button(10, y_offset, self.class_panel.width - 20, 30, class_name, None, 18,
                                     (60, 60, 80), (255, 255, 255), (100, 100, 150),
                                     (0, 0, 0), 1, lambda c=class_name: self.select_class(c))
                    
                    # 現在選択中の職業をハイライト
                    if class_name == self.selected_class:
                        class_btn.color = (100, 100, 150)
                    
                    self.class_panel.add_child(class_btn)
                    y_offset += 40
        else:
            # 選択が不完全な場合は案内メッセージ
            msg = "種族、所属、性格を選択してください"
            self.class_panel.add_child(Label(self.class_panel.width // 2, 40, msg, None, 18, (200, 200, 200), None, "center"))
        
        self.class_panel.update_content_height()
    
    def select_race(self, race_name):
        """種族を選択"""
        self.selected_race = race_name
        
        # 種族情報を更新
        if race_name in self.character_creator.races:
            self.race_info_panel.update_race(self.character_creator.races[race_name])
        
        # 所属が種族と互換性がない場合はリセット
        if self.selected_faction and race_name not in self.character_creator.factions[self.selected_faction].allowed_races:
            self.selected_faction = None
            self.faction_info_panel.update_faction(None)
        
        # UI更新
        self.update_race_options()
        self.update_faction_options()
        self.update_alignment_options()
        self.update_class_options()
        
        # 名前のランダム生成（種族に応じた名前）
        if race_name and self.selected_faction:
            self.character_name = self.character_creator.generate_random_name(race_name, self.selected_faction)
            self.name_input.set_text(self.character_name)
        
        # プレビュー更新
        self.update_preview()
    
    def select_faction(self, faction_name):
        """所属を選択"""
        self.selected_faction = faction_name
        
        # 所属情報を更新
        if faction_name in self.character_creator.factions:
            self.faction_info_panel.update_faction(self.character_creator.factions[faction_name])
        
        # 性格が所属と互換性がない場合はリセット
        if self.selected_alignment and self.selected_alignment not in self.character_creator.factions[faction_name].allowed_alignments:
            self.selected_alignment = None
        
        # UI更新
        self.update_faction_options()
        self.update_alignment_options()
        self.update_class_options()
        
        # 名前のランダム生成（所属に応じた名前）
        if self.selected_race and faction_name:
            self.character_name = self.character_creator.generate_random_name(self.selected_race, faction_name)
            self.name_input.set_text(self.character_name)
        
        # プレビュー更新
        self.update_preview()
    
    def select_alignment(self, alignment):
        """性格を選択"""
        # 選択した所属が性格を許可しているか確認
        if self.selected_faction and alignment not in self.character_creator.factions[self.selected_faction].allowed_alignments:
            return
        
        self.selected_alignment = alignment
        
        # UI更新
        self.update_alignment_options()
        self.update_class_options()
        
        # プレビュー更新
        self.update_preview()
    
    def select_class(self, class_name):
        """職業を選択"""
        self.selected_class = class_name
        
        # 職業情報を更新
        if class_name in self.character_creator.classes:
            self.class_info_panel.update_class(self.character_creator.classes[class_name])
        
        # UI更新
        self.update_class_options()
        
        # プレビュー更新
        self.update_preview()
    
    def prompt_name_input(self):
        """名前入力プロンプト"""
        # 名前入力用のダイアログが必要（simpleguiなどを利用）
        # ここでは仮の実装としてランダム名を設定
        if self.selected_race and self.selected_faction:
            self.character_name = self.character_creator.generate_random_name(
                self.selected_race, self.selected_faction
            )
            self.name_input.set_text(self.character_name)
            
            # プレビュー更新
            self.update_preview()
    
    def change_level(self, delta):
        """レベルを変更"""
        new_level = max(1, min(20, self.character_level + delta))
        if new_level != self.character_level:
            self.character_level = new_level
            self.level_value.set_text(str(self.character_level))
            
            # コスト更新
            self.update_cost()
            
            # プレビュー更新
            self.update_preview()
    
    def update_cost(self):
        """採用コストを更新"""
        base_cost = 1000
        level_cost = (self.character_level - 1) * 500
        
        # 種族による追加コスト
        race_cost = 0
        if self.selected_race:
            race = self.character_creator.races[self.selected_race]
            # 特殊能力を持つ種族は高価
            race_cost = len(race.special_skills) * 300
            
            # 稀少種族は高価
            if self.selected_race in ["獣人（鳥）", "妖精", "機械"]:
                race_cost += 500
        
        total_cost = base_cost + level_cost + race_cost
        self.cost_label.set_text(f"コスト: {total_cost}G")
        
        # コストが所持金を超える場合は作成ボタンを無効化
        if total_cost > self.game_manager.player_gold:
            self.create_btn.set_active(False)
            self.create_btn.color = (100, 100, 100)
        else:
            # その他の条件も確認
            can_create = (self.selected_race and self.selected_faction and 
                        self.selected_alignment and self.selected_class and 
                        self.character_name)
            self.create_btn.set_active(can_create)
            self.create_btn.color = (60, 100, 60) if can_create else (100, 100, 100)
    
    def update_preview(self):
        """キャラクタープレビューを更新"""
        if (self.selected_race and self.selected_faction and 
            self.selected_alignment and self.selected_class):
            # 名前が設定されていなければデフォルト名を使用
            name = self.character_name or "新規キャラクター"
            
            # キャラクタープレビューの生成
            self.preview_unit = self.character_creator.create_character(
                name=name,
                race_name=self.selected_race,
                faction_name=self.selected_faction,
                alignment=self.selected_alignment,
                class_name=self.selected_class,
                level=self.character_level
            )
            
            # 装備の追加
            self.character_creator.add_default_equipment(self.preview_unit)
            
            # コスト更新
            self.update_cost()
        else:
            self.preview_unit = None
        
        # プレビューパネルがある場合は更新
        if hasattr(self, 'preview_panel') and self.preview_panel:
            self.preview_panel.update_unit(self.preview_unit)
    
    def show_preview(self):
        """プレビューウィンドウを表示"""
        if not self.preview_unit:
            return
        
        # プレビューパネルをポップアップとして表示
        preview_panel = UnitPreviewPanel(self.width // 4, self.height // 4,
                                       self.width // 2, self.height // 2,
                                       self.preview_unit)
        
        # 閉じるボタン
        close_btn = Button(preview_panel.width - 30, 10, 20, 20, "×", None, 20,
                          (200, 50, 50), (255, 255, 255), (255, 100, 100),
                          None, 0, lambda: self.remove_child(preview_panel))
        preview_panel.add_child(close_btn)
        
        self.add_child(preview_panel)
    
    def generate_random(self):
        """ランダムキャラクターを生成"""
        # ランダムキャラクター生成
        unit = self.character_creator.generate_random_character((1, self.character_level))
        
        # 選択状態を更新
        self.selected_race = unit.race
        self.selected_faction = unit.faction
        self.selected_alignment = unit.alignment
        self.selected_class = unit.unit_class
        self.character_name = unit.name
        self.character_level = unit.level
        
        # UI表示更新
        self.name_input.set_text(self.character_name)
        self.level_value.set_text(str(self.character_level))
        
        # 情報パネル更新
        if self.selected_race in self.character_creator.races:
            self.race_info_panel.update_race(self.character_creator.races[self.selected_race])
        
        if self.selected_faction in self.character_creator.factions:
            self.faction_info_panel.update_faction(self.character_creator.factions[self.selected_faction])
        
        if self.selected_class in self.character_creator.classes:
            self.class_info_panel.update_class(self.character_creator.classes[self.selected_class])
        
        # 各選択肢の更新
        self.update_race_options()
        self.update_faction_options()
        self.update_alignment_options()
        self.update_class_options()
        
        # プレビュー更新
        self.preview_unit = unit
        if hasattr(self, 'preview_panel') and self.preview_panel:
            self.preview_panel.update_unit(self.preview_unit)
        
        # コスト更新
        self.update_cost()
    
    def create_character(self):
        """キャラクターを作成して雇用"""
        if not self.preview_unit:
            return
        
        # コスト計算
        base_cost = 1000
        level_cost = (self.character_level - 1) * 500
        
        # 種族による追加コスト
        race_cost = 0
        if self.selected_race:
            race = self.character_creator.races[self.selected_race]
            # 特殊能力を持つ種族は高価
            race_cost = len(race.special_skills) * 300
            
            # 稀少種族は高価
            if self.selected_race in ["獣人（鳥）", "妖精", "機械"]:
                race_cost += 500
        
        total_cost = base_cost + level_cost + race_cost
        
        # 所持金チェック
        if self.game_manager.player_gold < total_cost:
            return
        
        # 所持金から支払い
        self.game_manager.player_gold -= total_cost
        
        # 作成したキャラクターをユニットとして追加
        if self.on_create:
            self.on_create(self.preview_unit)
        
        # 作成履歴に追加
        self.character_creator.add_to_history(self.preview_unit)
        
        # プリセット保存の確認
        self.prompt_save_preset()
    
    def prompt_save_preset(self):
        """プリセット保存の確認"""
        # 実際のゲームでは確認ダイアログを表示
        # ここでは簡単のためプリセットとして保存
        if self.preview_unit:
            self.character_creator.save_character_preset(
                self.preview_unit,
                f"{self.preview_unit.name}のプリセット"
            )
        
        # ウィンドウを閉じる
        self.close_window()
    
    def load_preset(self, preset):
        """プリセットからキャラクターをロード"""
        if not preset:
            return
        
        # プリセットからキャラクターをロード
        unit = self.character_creator.load_character_preset(preset.name)
        if not unit:
            return
        
        # プレビューを更新
        if self.preview_panel:
            self.preview_panel.update_unit(unit)
        
        # 新規作成タブに切り替え
        self.change_tab("create")
        
        # 選択状態を更新
        self.selected_race = preset.race
        self.selected_faction = preset.faction
        self.selected_alignment = preset.alignment
        self.selected_class = preset.unit_class
        self.character_name = preset.name
        self.character_level = unit.level
        
        # UI表示更新
        self.name_input.set_text(self.character_name)
        self.level_value.set_text(str(self.character_level))
        
        # 情報パネル更新
        if self.selected_race in self.character_creator.races:
            self.race_info_panel.update_race(self.character_creator.races[self.selected_race])
        
        if self.selected_faction in self.character_creator.factions:
            self.faction_info_panel.update_faction(self.character_creator.factions[self.selected_faction])
        
        if self.selected_class in self.character_creator.classes:
            self.class_info_panel.update_class(self.character_creator.classes[self.selected_class])
        
        # 各選択肢の更新
        self.update_race_options()
        self.update_faction_options()
        self.update_alignment_options()
        self.update_class_options()
        
        # プレビュー更新
        self.preview_unit = unit
        
        # コスト更新
        self.update_cost()
    
    def load_from_history(self, unit):
        """履歴からキャラクターをロード"""
        if not unit:
            return
        
        # プレビューを更新
        if self.preview_panel:
            self.preview_panel.update_unit(unit)
        
        # 新規作成タブに切り替え
        self.change_tab("create")
        
        # 選択状態を更新
        self.selected_race = getattr(unit, 'race', None)
        self.selected_faction = getattr(unit, 'faction', None)
        self.selected_alignment = getattr(unit, 'alignment', None)
        self.selected_class = unit.unit_class
        self.character_name = unit.name
        self.character_level = unit.level
        
        # UI表示更新
        self.name_input.set_text(self.character_name)
        self.level_value.set_text(str(self.character_level))
        
        # 情報パネル更新
        if self.selected_race in self.character_creator.races:
            self.race_info_panel.update_race(self.character_creator.races[self.selected_race])
        
        if self.selected_faction in self.character_creator.factions:
            self.faction_info_panel.update_faction(self.character_creator.factions[self.selected_faction])
        
        if self.selected_class in self.character_creator.classes:
            self.class_info_panel.update_class(self.character_creator.classes[self.selected_class])
        
        # 各選択肢の更新
        self.update_race_options()
        self.update_faction_options()
        self.update_alignment_options()
        self.update_class_options()
        
        # プレビュー更新
        self.preview_unit = unit
        
        # コスト更新
        self.update_cost()
    
    def close_window(self):
        """ウィンドウを閉じる"""
        if self.on_close:
            self.on_close()

def integrate_character_creator(game_manager):
    """キャラクタークリエイターをゲームマネージャーに統合する"""
    from growth_system import GrowthSystem
    from skills import SkillManager
    from support_system import SupportSystem
    
    # 各システムを初期化
    skill_manager = SkillManager()
    growth_system = GrowthSystem()
    support_system = SupportSystem()
    
    # キャラクタークリエイターを初期化
    character_creator = EnhancedCharacterCreator(
        data_path="data/",
        skill_manager=skill_manager,
        support_system=support_system
    )
    
    # ゲームマネージャーに登録
    game_manager.character_creator = character_creator
    game_manager.skill_manager = skill_manager
    game_manager.growth_system = growth_system
    
    # コールバック登録
    game_manager.on_show_character_creator = lambda: show_character_creator(game_manager)
    
    return character_creator


def show_character_creator(game_manager):
    """キャラクタークリエイターUIを表示する"""
    import pygame
    from constants import SCREEN_WIDTH, SCREEN_HEIGHT
    
    # UIマネージャーの取得（ゲームマネージャーから）
    ui_manager = game_manager.ui_manager
    
    # キャラクタークリエイターウィンドウを作成
    creation_window = EnhancedCharacterCreationWindow(
        50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100,
        game_manager.character_creator, game_manager,
        on_create=lambda unit: game_manager.add_unit_to_party(unit),
        on_close=lambda: ui_manager.remove_window(creation_window)
    )
    
    # UIマネージャーに追加
    ui_manager.add_window(creation_window)
    
    return creation_window

class MapEditorCharacterPlacer(Panel):
    """マップエディタでのキャラクター配置パネル"""
    def __init__(self, x, y, width, height, character_creator, map_editor, on_close=None):
        super().__init__(x, y, width, height, (40, 40, 50), (255, 255, 255), 2, 230)
        self.character_creator = character_creator
        self.map_editor = map_editor
        self.on_close = on_close
        
        # 選択状態
        self.selected_faction = None
        self.selected_team = 0  # 0: プレイヤー, 1: 敵
        self.selected_unit = None
        
        # UIセットアップ
        self._setup_ui()
    
    def _setup_ui(self):
        """UIセットアップ"""
        # タイトル
        title_label = Label(self.width // 2, 20, "キャラクター配置", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # 閉じるボタン
        close_btn = Button(self.width - 80, 20, 60, 30, "閉じる", None, 20,
                         (100, 60, 60), (255, 255, 255), (150, 80, 80),
                         (0, 0, 0), 1, self.close_window)
        self.add_child(close_btn)
        
        # チーム選択
        team_label = Label(self.width // 4, 60, "チーム:", None, 24, (255, 255, 200), None, "center")
        self.add_child(team_label)
        
        player_btn = Button(self.width // 4 - 50, 90, 100, 30, "プレイヤー", None, 20,
                          (60, 60, 150), (255, 255, 255), (80, 80, 200),
                          (0, 0, 0), 1, lambda: self.select_team(0))
        self.add_child(player_btn)
        
        enemy_btn = Button(self.width // 4 + 60, 90, 100, 30, "敵", None, 20,
                         (150, 60, 60), (255, 255, 255), (200, 80, 80),
                         (0, 0, 0), 1, lambda: self.select_team(1))
        self.add_child(enemy_btn)
        
        # 所属選択（左側）
        faction_panel = ScrollPanel(20, 130, self.width // 3, self.height - 170, self.height, (50, 50, 60), (0, 0, 0), 1, 220)
        self.add_child(faction_panel)
        self.faction_panel = faction_panel
        
        faction_label = Label(self.width // 6 + 20, 130, "所属", None, 24, (255, 255, 200), None, "center")
        self.add_child(faction_label)
        
        # ユニット選択（右側）
        unit_panel = ScrollPanel(self.width // 3 + 30, 130, self.width * 2 // 3 - 50, self.height - 170, self.height, (50, 50, 60), (0, 0, 0), 1, 220)
        self.add_child(unit_panel)
        self.unit_panel = unit_panel
        
        unit_label = Label(self.width * 2 // 3, 130, "ユニット", None, 24, (255, 255, 200), None, "center")
        self.add_child(unit_label)
        
        # 所属リストの更新
        self.update_faction_list()
    
    def update_faction_list(self):
        """所属リストを更新"""
        self.faction_panel.clear_children()
        
        y_offset = 10
        for faction_name, faction in self.character_creator.factions.items():
            faction_btn = Button(10, y_offset, self.faction_panel.width - 20, 30, faction_name, None, 18,
                              (60, 60, 80), (255, 255, 255), (100, 100, 150),
                              (0, 0, 0), 1, lambda f=faction_name: self.select_faction(f))
            
            # 現在選択中の所属をハイライト
            if faction_name == self.selected_faction:
                faction_btn.color = (100, 100, 150)
            
            self.faction_panel.add_child(faction_btn)
            y_offset += 40
        
        self.faction_panel.update_content_height()
    
    def update_unit_list(self):
        """ユニットリストを更新"""
        self.unit_panel.clear_children()
        
        if not self.selected_faction:
            return
        
        # 選択した所属のユニットをプリセットから取得
        faction_units = []
        for name, preset in self.character_creator.presets.items():
            if preset.faction == self.selected_faction:
                faction_units.append(preset)
        
        # もしプリセットがなければサンプルユニットを生成
        if not faction_units:
            # 所属に対応する種族で最初のものを使用
            race_name = self.character_creator.factions[self.selected_faction].allowed_races[0]
            alignment = self.character_creator.factions[self.selected_faction].allowed_alignments[0]
            compatible_classes = self.character_creator.get_compatible_classes(race_name, self.selected_faction, alignment)
            
            if compatible_classes:
                # サンプルユニットを3種類生成
                for i in range(3):
                    class_name = compatible_classes[i % len(compatible_classes)]
                    name = self.character_creator.generate_random_name(race_name, self.selected_faction)
                    
                    unit = self.character_creator.create_character(
                        name=name,
                        race_name=race_name,
                        faction_name=self.selected_faction,
                        alignment=alignment,
                        class_name=class_name,
                        level=1
                    )
                    
                    # 装備を追加
                    self.character_creator.add_default_equipment(unit)
                    
                    # プリセットとして保存
                    self.character_creator.save_character_preset(
                        unit,
                        f"{unit.name}のプリセット"
                    )
                    
                    faction_units.append(self.character_creator.presets[unit.name])
        
        # ユニット一覧表示
        y_offset = 10
        for i, preset in enumerate(faction_units):
            unit_panel = Panel(10, y_offset, self.unit_panel.width - 20, 60, (60, 60, 70), (0, 0, 0), 1, 255)
            
            # ユニット名と職業
            unit_panel.add_child(Label(10, 10, preset.name, None, 20, (255, 255, 200)))
            unit_panel.add_child(Label(10, 35, f"{preset.race} / {preset.unit_class}", None, 18, (200, 200, 200)))
            
            # 配置ボタン
            place_btn = Button(unit_panel.width - 80, 15, 70, 30, "配置", None, 18,
                             (60, 100, 60), (255, 255, 255), (80, 150, 80),
                             (0, 0, 0), 1, lambda p=preset: self.select_unit_for_placement(p))
            unit_panel.add_child(place_btn)
            
            self.unit_panel.add_child(unit_panel)
            y_offset += 70
        
        self.unit_panel.update_content_height()
    
    def select_team(self, team):
        """チームを選択"""
        self.selected_team = team
    
    def select_faction(self, faction_name):
        """所属を選択"""
        self.selected_faction = faction_name
        
        # UI更新
        self.update_faction_list()
        self.update_unit_list()
    
    def select_unit_for_placement(self, preset):
        """配置用ユニットを選択"""
        # プリセットからユニットを生成
        unit = self.character_creator.load_character_preset(preset.name)
        if not unit:
            return
        
        # チーム設定
        unit.team = self.selected_team
        
        # マップエディターに配置用ユニットを設定
        self.map_editor.set_placement_unit(unit)
        
        # 自動的にウィンドウを閉じる
        self.close_window()
    
    def close_window(self):
        """ウィンドウを閉じる"""
        if self.on_close:
            self.on_close()
    


