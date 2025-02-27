# growth_system.py
import random
from typing import Dict, List, Tuple, Optional
import pandas as pd
import os

class GrowthSystem:
    """
    成長システム: 固定値成長とレベルアップの管理を担当するクラス
    """
    def __init__(self, data_path="data/"):
        self.data_path = data_path
        
        # Excelファイルからデータを読み込む
        self.class_data = self._load_class_data()
        self.character_data = self._load_character_data()
        self.level_data = self._load_level_data()
        self.map_data = self._load_map_data()
        
        # 最大レベル
        self.max_level = 20
    
    def _load_class_data(self) -> pd.DataFrame:
        """職業データをExcelから読み込む"""
        file_path = os.path.join(self.data_path, "class_data.xlsx")
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"職業データの読み込みエラー: {e}")
            # 空のデータフレームを返す
            return pd.DataFrame(columns=[
                "class_id", "class_name", "base_hp", "base_strength", "base_magic", 
                "base_skill", "base_speed", "base_luck", "base_defense", "base_resistance",
                "growth_hp", "growth_strength", "growth_magic", "growth_skill", 
                "growth_speed", "growth_luck", "growth_defense", "growth_resistance",
                "max_hp", "max_strength", "max_magic", "max_skill", 
                "max_speed", "max_luck", "max_defense", "max_resistance"
            ])
    
    def _load_character_data(self) -> pd.DataFrame:
        """キャラクターデータをExcelから読み込む"""
        file_path = os.path.join(self.data_path, "character_data.xlsx")
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"キャラクターデータの読み込みエラー: {e}")
            # 空のデータフレームを返す
            return pd.DataFrame(columns=[
                "character_id", "character_name", "mod_hp", "mod_strength", "mod_magic", 
                "mod_skill", "mod_speed", "mod_luck", "mod_defense", "mod_resistance"
            ])
    
    def _load_level_data(self) -> pd.DataFrame:
        """レベルデータをExcelから読み込む"""
        file_path = os.path.join(self.data_path, "level_data.xlsx")
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"レベルデータの読み込みエラー: {e}")
            # 空のデータフレームを返す
            return pd.DataFrame({
                "level": list(range(1, 21)),
                "exp_required": [0, 100, 210, 330, 460, 600, 750, 910, 1080, 1260,
                                1450, 1650, 1860, 2080, 2310, 2550, 2800, 3060, 3330, 3610]
            })
    
    def _load_map_data(self) -> pd.DataFrame:
        """マップデータをExcelから読み込む"""
        file_path = os.path.join(self.data_path, "map_data.xlsx")
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"マップデータの読み込みエラー: {e}")
            # 空のデータフレームを返す
            return pd.DataFrame(columns=[
                "map_id", "map_name", "recommended_level", "level_cap", "difficulty_modifier"
            ])
    
    def reload_data(self):
        """データを再読み込みする"""
        self.class_data = self._load_class_data()
        self.character_data = self._load_character_data()
        self.level_data = self._load_level_data()
        self.map_data = self._load_map_data()
    
    def get_fixed_growth_values(self, unit) -> Dict[str, int]:
        """
        ユニットの固定成長値を取得する
        
        Args:
            unit: 対象ユニット
            
        Returns:
            Dict[str, int]: 各ステータスの固定成長値
        """
        # 職業の成長データを取得
        class_row = self.class_data[self.class_data['class_name'] == unit.unit_class]
        if class_row.empty:
            # 職業データが見つからない場合はデフォルト値
            return {
                "hp": 1, "strength": 0, "magic": 0, "skill": 0, 
                "speed": 0, "luck": 0, "defense": 0, "resistance": 0
            }
        
        # キャラクター固有の修正値を取得
        char_row = self.character_data[self.character_data['character_name'] == unit.name]
        char_mods = {
            "hp": 0, "strength": 0, "magic": 0, "skill": 0, 
            "speed": 0, "luck": 0, "defense": 0, "resistance": 0
        }
        
        if not char_row.empty:
            char_mods["hp"] = char_row.iloc[0].get('mod_hp', 0)
            char_mods["strength"] = char_row.iloc[0].get('mod_strength', 0)
            char_mods["magic"] = char_row.iloc[0].get('mod_magic', 0)
            char_mods["skill"] = char_row.iloc[0].get('mod_skill', 0)
            char_mods["speed"] = char_row.iloc[0].get('mod_speed', 0)
            char_mods["luck"] = char_row.iloc[0].get('mod_luck', 0)
            char_mods["defense"] = char_row.iloc[0].get('mod_defense', 0)
            char_mods["resistance"] = char_row.iloc[0].get('mod_resistance', 0)
        
        # 職業の基本成長値と修正値を合わせて返す
        growth_values = {
            "hp": max(0, class_row.iloc[0].get('growth_hp', 1) + char_mods["hp"]),
            "strength": max(0, class_row.iloc[0].get('growth_strength', 0) + char_mods["strength"]),
            "magic": max(0, class_row.iloc[0].get('growth_magic', 0) + char_mods["magic"]),
            "skill": max(0, class_row.iloc[0].get('growth_skill', 0) + char_mods["skill"]),
            "speed": max(0, class_row.iloc[0].get('growth_speed', 0) + char_mods["speed"]),
            "luck": max(0, class_row.iloc[0].get('growth_luck', 0) + char_mods["luck"]),
            "defense": max(0, class_row.iloc[0].get('growth_defense', 0) + char_mods["defense"]),
            "resistance": max(0, class_row.iloc[0].get('growth_resistance', 0) + char_mods["resistance"])
        }
        
        return growth_values
    
    def get_stat_caps(self, unit) -> Dict[str, int]:
        """ユニットのステータス上限を取得する"""
        class_row = self.class_data[self.class_data['class_name'] == unit.unit_class]
        if class_row.empty:
            # デフォルト値
            return {
                "hp": 60, "strength": 25, "magic": 25, "skill": 25, 
                "speed": 25, "luck": 30, "defense": 25, "resistance": 25
            }
        
        return {
            "hp": class_row.iloc[0].get('max_hp', 60),
            "strength": class_row.iloc[0].get('max_strength', 25),
            "magic": class_row.iloc[0].get('max_magic', 25),
            "skill": class_row.iloc[0].get('max_skill', 25),
            "speed": class_row.iloc[0].get('max_speed', 25),
            "luck": class_row.iloc[0].get('max_luck', 30),
            "defense": class_row.iloc[0].get('max_defense', 25),
            "resistance": class_row.iloc[0].get('max_resistance', 25)
        }
    
    def get_exp_threshold(self, level: int) -> int:
        """特定のレベルに必要な経験値を取得する"""
        if level <= 1 or level > self.max_level:
            return 0
            
        level_row = self.level_data[self.level_data['level'] == level]
        if level_row.empty:
            # デフォルト値
            default_thresholds = [0, 100, 210, 330, 460, 600, 750, 910, 1080, 1260,
                                 1450, 1650, 1860, 2080, 2310, 2550, 2800, 3060, 3330, 3610]
            return default_thresholds[level-1] if level <= len(default_thresholds) else 9999
        
        return level_row.iloc[0].get('exp_required', 100)
    
    def level_up(self, unit) -> Dict[str, int]:
        """
        固定成長値に基づいたレベルアップ処理
        
        Returns:
            Dict[str, int]: 上昇したステータスとその値
        """
        # 現在のレベルを確認
        if unit.level >= self.max_level:
            return {}  # 最大レベルに達している場合は上昇なし
        
        # 固定成長値を取得
        growth_values = self.get_fixed_growth_values(unit)
        stat_caps = self.get_stat_caps(unit)
        
        # 実際に適用する成長値（ステータス上限を考慮）
        applied_growth = {}
        
        # HPの上昇
        if unit.max_hp + growth_values["hp"] <= stat_caps["hp"]:
            applied_growth["hp"] = growth_values["hp"]
        else:
            applied_growth["hp"] = max(0, stat_caps["hp"] - unit.max_hp)
        
        # 力の上昇
        if unit.strength + growth_values["strength"] <= stat_caps["strength"]:
            applied_growth["strength"] = growth_values["strength"]
        else:
            applied_growth["strength"] = max(0, stat_caps["strength"] - unit.strength)
        
        # 魔力の上昇
        if unit.magic + growth_values["magic"] <= stat_caps["magic"]:
            applied_growth["magic"] = growth_values["magic"]
        else:
            applied_growth["magic"] = max(0, stat_caps["magic"] - unit.magic)
        
        # 技の上昇
        if unit.skill + growth_values["skill"] <= stat_caps["skill"]:
            applied_growth["skill"] = growth_values["skill"]
        else:
            applied_growth["skill"] = max(0, stat_caps["skill"] - unit.skill)
        
        # 速さの上昇
        if unit.speed + growth_values["speed"] <= stat_caps["speed"]:
            applied_growth["speed"] = growth_values["speed"]
        else:
            applied_growth["speed"] = max(0, stat_caps["speed"] - unit.speed)
        
        # 幸運の上昇
        if unit.luck + growth_values["luck"] <= stat_caps["luck"]:
            applied_growth["luck"] = growth_values["luck"]
        else:
            applied_growth["luck"] = max(0, stat_caps["luck"] - unit.luck)
        
        # 守備の上昇
        if unit.defense + growth_values["defense"] <= stat_caps["defense"]:
            applied_growth["defense"] = growth_values["defense"]
        else:
            applied_growth["defense"] = max(0, stat_caps["defense"] - unit.defense)
        
        # 魔防の上昇
        if unit.resistance + growth_values["resistance"] <= stat_caps["resistance"]:
            applied_growth["resistance"] = growth_values["resistance"]
        else:
            applied_growth["resistance"] = max(0, stat_caps["resistance"] - unit.resistance)
        
        # 実際にステータスを上昇させる
        unit.max_hp += applied_growth["hp"]
        unit.current_hp += applied_growth["hp"]  # 現在HPも上昇
        unit.strength += applied_growth["strength"]
        unit.magic += applied_growth["magic"]
        unit.skill += applied_growth["skill"]
        unit.speed += applied_growth["speed"]
        unit.luck += applied_growth["luck"]
        unit.defense += applied_growth["defense"]
        unit.resistance += applied_growth["resistance"]
        
        # レベルアップ
        unit.level += 1
        unit.exp = 0
        
        return applied_growth
    
    def award_exp(self, unit, exp_amount: int) -> Tuple[bool, Optional[Dict[str, int]]]:
        """
        ユニットに経験値を付与し、レベルアップした場合はステータス上昇を返す
        
        Args:
            unit: 経験値を獲得するユニット
            exp_amount: 獲得する経験値量
        
        Returns:
            Tuple[bool, Optional[Dict[str, int]]]: レベルアップしたかどうか、ステータス上昇量
        """
        if unit.level >= self.max_level:
            return False, None  # 最大レベルに達している場合は経験値獲得なし
        
        unit.exp += exp_amount
        
        # 次のレベルに必要な経験値を取得
        next_level_threshold = self.get_exp_threshold(unit.level + 1)
        
        if unit.exp >= next_level_threshold:
            # レベルアップ
            stat_gains = self.level_up(unit)
            return True, stat_gains
        
        return False, None
    
    def calculate_combat_exp(self, attacker, defender, combat_results) -> int:
        """戦闘結果から獲得経験値を計算する"""
        # 基本経験値
        base_exp = 10
        
        # レベル差による補正
        level_diff = defender.level - attacker.level
        level_modifier = max(0, min(20, level_diff * 2 + 10))
        
        # ダメージ量による補正
        damage_dealt = sum(r.get("damage", 0) for r in combat_results["attacker_results"])
        damage_percentage = min(100, int(damage_dealt / defender.max_hp * 100))
        damage_modifier = damage_percentage // 10
        
        # 敵を倒した場合のボーナス
        kill_bonus = 20 if defender.is_dead() else 0
        
        total_exp = base_exp + level_modifier + damage_modifier + kill_bonus
        
        # 最低保証と上限
        total_exp = max(1, min(100, total_exp))
        
        return total_exp
    
    def calculate_expected_stats(self, unit_class: str, character_name: str, target_level: int) -> Dict[str, int]:
        """
        特定のレベルで期待されるステータスを固定成長値に基づいて計算する
        
        Args:
            unit_class: ユニットのクラス
            character_name: キャラクター名
            target_level: 目標レベル
        
        Returns:
            Dict[str, int]: 期待されるステータス
        """
        # 職業の基本データを取得
        class_row = self.class_data[self.class_data['class_name'] == unit_class]
        if class_row.empty:
            # デフォルト値
            base_stats = {
                "hp": 18, "strength": 5, "magic": 1, "skill": 5, 
                "speed": 5, "luck": 5, "defense": 5, "resistance": 5
            }
        else:
            base_stats = {
                "hp": class_row.iloc[0].get('base_hp', 18),
                "strength": class_row.iloc[0].get('base_strength', 5),
                "magic": class_row.iloc[0].get('base_magic', 1),
                "skill": class_row.iloc[0].get('base_skill', 5),
                "speed": class_row.iloc[0].get('base_speed', 5),
                "luck": class_row.iloc[0].get('base_luck', 5),
                "defense": class_row.iloc[0].get('base_defense', 5),
                "resistance": class_row.iloc[0].get('base_resistance', 5)
            }
        
        # 固定成長値を取得
        temp_unit = type('obj', (object,), {
            'unit_class': unit_class,
            'name': character_name
        })
        growth_values = self.get_fixed_growth_values(temp_unit)
        
        # レベル1からtarget_levelまでの成長を計算
        expected_stats = base_stats.copy()
        for _ in range(1, target_level):
            for stat in expected_stats:
                expected_stats[stat] += growth_values[stat]
        
        # ステータス上限を適用
        stat_caps = self.get_stat_caps(temp_unit)
        for stat in expected_stats:
            expected_stats[stat] = min(expected_stats[stat], stat_caps[stat])
        
        return expected_stats