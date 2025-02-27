# level_sync.py
from typing import Dict, List, Optional, Tuple
import pandas as pd
import os
import copy

class LevelSyncSystem:
    """
    レベルシンクシステム: マップ難易度に合わせてユニットの強さを調整するシステム
    固定値成長に対応
    """
    def __init__(self, growth_system, data_path="data/"):
        self.growth_system = growth_system
        self.data_path = data_path
        
        # マップデータはgrowth_systemから取得
        self.map_data = growth_system.map_data
        
        # 難易度設定
        self.difficulty_settings = self._load_difficulty_settings()
        
        # デフォルト難易度
        self.current_difficulty = "normal"
        
        # 各ユニットの元のステータスを保存
        self.original_unit_stats = {}
    
    def _load_difficulty_settings(self) -> pd.DataFrame:
        """難易度設定をExcelから読み込む"""
        file_path = os.path.join(self.data_path, "difficulty_settings.xlsx")
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"難易度設定の読み込みエラー: {e}")
            # デフォルトの難易度設定
            return pd.DataFrame({
                "difficulty_name": ["easy", "normal", "hard", "lunatic"],
                "stat_multiplier": [0.9, 1.0, 1.1, 1.2],
                "exp_multiplier": [1.2, 1.0, 0.8, 0.6],
                "enemy_level_bonus": [0, 0, 1, 2]
            })
    
    def reload_data(self):
        """データを再読み込みする"""
        self.difficulty_settings = self._load_difficulty_settings()
        self.map_data = self.growth_system.map_data
    
    def set_difficulty(self, difficulty: str):
        """難易度を設定する"""
        difficulty_names = self.difficulty_settings['difficulty_name'].tolist()
        if difficulty in difficulty_names:
            self.current_difficulty = difficulty
    
    def get_map_info(self, map_id: str) -> Tuple[int, int]:
        """マップの推奨レベルとレベル上限を取得する"""
        map_row = self.map_data[self.map_data['map_id'] == map_id]
        if map_row.empty:
            # デフォルト値
            return 1, 20
        
        return (
            map_row.iloc[0].get('recommended_level', 1),
            map_row.iloc[0].get('level_cap', 20)
        )
    
    def get_difficulty_multiplier(self) -> float:
        """現在の難易度に対応するステータス倍率を取得する"""
        difficulty_row = self.difficulty_settings[self.difficulty_settings['difficulty_name'] == self.current_difficulty]
        if difficulty_row.empty:
            return 1.0
        
        return difficulty_row.iloc[0].get('stat_multiplier', 1.0)
    
    def store_original_stats(self, unit):
        """ユニットの元のステータスを保存する"""
        if unit.name not in self.original_unit_stats:
            self.original_unit_stats[unit.name] = {
                "level": unit.level,
                "max_hp": unit.max_hp,
                "current_hp": unit.current_hp,
                "hp_ratio": unit.current_hp / unit.max_hp if unit.max_hp > 0 else 1.0,
                "strength": unit.strength,
                "magic": unit.magic,
                "skill": unit.skill,
                "speed": unit.speed,
                "luck": unit.luck,
                "defense": unit.defense,
                "resistance": unit.resistance,
                "exp": unit.exp
            }
    
    def restore_original_stats(self, unit):
        """ユニットの元のステータスを復元する"""
        if unit.name in self.original_unit_stats:
            stats = self.original_unit_stats[unit.name]
            unit.level = stats["level"]
            unit.max_hp = stats["max_hp"]
            
            # HPの回復率を維持するか、保存した現在HPを使用
            if "current_hp" in stats:
                unit.current_hp = stats["current_hp"]
            else:
                unit.current_hp = int(unit.max_hp * stats["hp_ratio"])
            
            unit.strength = stats["strength"]
            unit.magic = stats["magic"]
            unit.skill = stats["skill"]
            unit.speed = stats["speed"]
            unit.luck = stats["luck"]
            unit.defense = stats["defense"]
            unit.resistance = stats["resistance"]
            unit.exp = stats.get("exp", 0)
    
    def apply_level_sync(self, unit, map_id: str) -> bool:
        """
        レベルシンクを適用してユニットのステータスを調整する
        
        Args:
            unit: 調整対象のユニット
            map_id: マップID
        
        Returns:
            bool: レベルシンクが適用されたかどうか
        """
        # 元のステータスを保存
        self.store_original_stats(unit)
        
        # マップの推奨レベルとレベル上限を取得
        recommended_level, level_cap = self.get_map_info(map_id)
        
        # ユニットのレベルがマップのレベル上限より高い場合
        if unit.level > level_cap:
            # 難易度による調整係数
            difficulty_multiplier = self.get_difficulty_multiplier()
            
            # レベル上限に合わせた期待ステータスを計算（固定成長値による）
            expected_stats = self.growth_system.calculate_expected_stats(
                unit.unit_class, unit.name, level_cap
            )
            
            # ステータスを調整（難易度に応じて）
            adjusted_stats = {}
            for stat, value in expected_stats.items():
                adjusted_value = int(value * difficulty_multiplier)
                adjusted_stats[stat] = adjusted_value
            
            # ユニットのステータスを調整
            unit.level = level_cap
            unit.max_hp = adjusted_stats["hp"]
            unit.strength = adjusted_stats["strength"]
            unit.magic = adjusted_stats["magic"]
            unit.skill = adjusted_stats["skill"]
            unit.speed = adjusted_stats["speed"]
            unit.luck = adjusted_stats["luck"]
            unit.defense = adjusted_stats["defense"]
            unit.resistance = adjusted_stats["resistance"]
            
            # 現在HPの調整（HPの割合を維持）
            hp_ratio = self.original_unit_stats[unit.name]["hp_ratio"]
            unit.current_hp = max(1, int(unit.max_hp * hp_ratio))
            
            # 経験値をリセット（次のレベルアップに備えて）
            unit.exp = 0
            
            return True  # レベルシンク適用
        
        return False  # レベルシンク不要
    
    def initialize_map(self, units, map_id: str) -> List[Tuple[str, Dict]]:
        """
        マップ開始時、全ユニットにレベルシンクを適用する
        
        Args:
            units: マップ上のユニットリスト
            map_id: マップID
        
        Returns:
            List[Tuple[str, Dict]]: レベルシンクが適用されたユニットのリストと変更内容
        """
        synced_units = []
        
        for unit in units:
            # プレイヤーユニットのみ調整
            if unit.team == 0:  # 0: プレイヤーチーム
                # 元のステータスを記録
                original_stats = {
                    "level": unit.level,
                    "max_hp": unit.max_hp,
                    "strength": unit.strength,
                    "magic": unit.magic,
                    "skill": unit.skill,
                    "speed": unit.speed,
                    "luck": unit.luck,
                    "defense": unit.defense,
                    "resistance": unit.resistance
                }
                
                # レベルシンク適用
                if self.apply_level_sync(unit, map_id):
                    # 変更後のステータス
                    new_stats = {
                        "level": unit.level,
                        "max_hp": unit.max_hp,
                        "strength": unit.strength,
                        "magic": unit.magic,
                        "skill": unit.skill,
                        "speed": unit.speed,
                        "luck": unit.luck,
                        "defense": unit.defense,
                        "resistance": unit.resistance
                    }
                    
                    # 変更があった場合のみ記録
                    changes = {}
                    for stat, value in new_stats.items():
                        if value != original_stats[stat]:
                            changes[stat] = (original_stats[stat], value)
                    
                    if changes:
                        synced_units.append((unit.name, changes))
        
        return synced_units
    
    def finalize_map(self, units):
        """
        マップ終了時、全ユニットの元のステータスを復元する
        
        Args:
            units: マップ上のユニットリスト
        """
        for unit in units:
            if unit.team == 0:  # プレイヤーチーム
                self.restore_original_stats(unit)