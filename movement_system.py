# movement_system.py
from enum import Enum
import pandas as pd
import os
from constants import TerrainType

class MovementType(Enum):
    INFANTRY = 1      # 歩兵
    ARMORED = 2       # 重騎士
    MAGE = 3          # 魔法使い
    CAVALRY = 4       # 騎馬兵
    FLYING = 5        # 飛行兵
    NINJA = 6         # 忍者
    GHOST = 7         # 壁抜け
    MOUNTAIN = 8      # 山地適応
    AQUATIC = 9       # 水地適応
    FOREST = 10       # 森林適応
    DESERT = 11       # 砂地適応
    DAMAGE_FLOOR = 12 # ダメ床適応

class MovementSystem:
    """ユニットの移動タイプと地形効果を管理するクラス"""
    def __init__(self, data_path="data/"):
        self.data_path = data_path
        
        # 移動タイプデータの読み込み
        self.movement_data = self._load_movement_data()
        
        # カスタム移動コスト（特殊スキルや状態による一時的な修正用）
        self.custom_move_costs = {}
    
    def _load_movement_data(self) -> pd.DataFrame:
        """移動タイプデータをExcelから読み込む"""
        file_path = os.path.join(self.data_path, "movement_types.xlsx")
        try:
            df = pd.read_excel(file_path)
            # 読み込んだデータを加工して使いやすい形に変換
            movement_data = {}
            
            for _, row in df.iterrows():
                move_type_id = row.get('id')
                move_type_name = row.get('name', '')
                
                # 各地形タイプに対するコスト
                terrain_costs = {}
                for terrain in TerrainType:
                    cost_col = f'cost_{terrain.name.lower()}'
                    if cost_col in row:
                        terrain_costs[terrain] = row[cost_col]
                    else:
                        # デフォルトコスト
                        terrain_costs[terrain] = self._get_default_cost(move_type_id, terrain)
                
                # 移動タイプの特徴（地形ダメージ無効など）
                features = {}
                feature_cols = [col for col in row.index if col.startswith('feature_')]
                for col in feature_cols:
                    feature_name = col[8:]  # "feature_" を除去
                    features[feature_name] = bool(row[col])
                
                movement_data[MovementType(move_type_id)] = {
                    'name': move_type_name,
                    'terrain_costs': terrain_costs,
                    'features': features
                }
            
            return movement_data
            
        except Exception as e:
            print(f"移動タイプデータの読み込みエラー: {e}")
            # デフォルトの移動コストを返す
            return self._create_default_movement_data()
    
    def _create_default_movement_data(self) -> dict:
        """デフォルトの移動タイプデータを作成"""
        default_data = {}
        
        # 歩兵（標準）
        infantry_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 2,
            TerrainType.MOUNTAIN: 4,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.INFANTRY] = {
            'name': '歩兵',
            'terrain_costs': infantry_costs,
            'features': {}
        }
        
        # 重騎士
        armored_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 3,
            TerrainType.MOUNTAIN: 999,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.ARMORED] = {
            'name': '重騎士',
            'terrain_costs': armored_costs,
            'features': {'defense_bonus': True}
        }
        
        # 魔法使い
        mage_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 2,
            TerrainType.MOUNTAIN: 4,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.MAGE] = {
            'name': '魔法使い',
            'terrain_costs': mage_costs,
            'features': {}
        }
        
        # 騎馬兵
        cavalry_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 3,
            TerrainType.MOUNTAIN: 999,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.CAVALRY] = {
            'name': '騎馬兵',
            'terrain_costs': cavalry_costs,
            'features': {'move_bonus': True}
        }
        
        # 飛行兵
        flying_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 1,
            TerrainType.MOUNTAIN: 1,
            TerrainType.WATER: 1,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.FLYING] = {
            'name': '飛行兵',
            'terrain_costs': flying_costs,
            'features': {'flying': True}
        }
        
        # 忍者
        ninja_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 1,
            TerrainType.MOUNTAIN: 2,
            TerrainType.WATER: 2,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.NINJA] = {
            'name': '忍者',
            'terrain_costs': ninja_costs,
            'features': {'stealth': True}
        }
        
        # 壁抜け
        ghost_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 1,
            TerrainType.MOUNTAIN: 2,
            TerrainType.WATER: 2,
            TerrainType.WALL: 2,
        }
        default_data[MovementType.GHOST] = {
            'name': '壁抜け',
            'terrain_costs': ghost_costs,
            'features': {'pass_walls': True}
        }
        
        # 山地適応
        mountain_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 1,
            TerrainType.MOUNTAIN: 1,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.MOUNTAIN] = {
            'name': '山地適応',
            'terrain_costs': mountain_costs,
            'features': {'mountain_bonus': True}
        }
        
        # 水地適応
        aquatic_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 2,
            TerrainType.MOUNTAIN: 999,
            TerrainType.WATER: 1,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.AQUATIC] = {
            'name': '水地適応',
            'terrain_costs': aquatic_costs,
            'features': {'water_bonus': True}
        }
        
        # 森林適応
        forest_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 1,
            TerrainType.MOUNTAIN: 3,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.FOREST] = {
            'name': '森林適応',
            'terrain_costs': forest_costs,
            'features': {'forest_bonus': True}
        }
        
        # 砂地適応
        desert_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 2,
            TerrainType.MOUNTAIN: 3,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.DESERT] = {
            'name': '砂地適応',
            'terrain_costs': desert_costs,
            'features': {'desert_bonus': True}
        }
        
        # ダメ床適応
        damage_floor_costs = {
            TerrainType.PLAIN: 1,
            TerrainType.FOREST: 2,
            TerrainType.MOUNTAIN: 4,
            TerrainType.WATER: 999,
            TerrainType.WALL: 999,
        }
        default_data[MovementType.DAMAGE_FLOOR] = {
            'name': 'ダメ床適応',
            'terrain_costs': damage_floor_costs,
            'features': {'damage_floor_immunity': True}
        }
        
        return default_data
    
    def _get_default_cost(self, move_type_id: int, terrain: TerrainType) -> int:
        """デフォルトの移動コストを取得"""
        # 移動タイプごとの基本コスト
        if move_type_id == MovementType.FLYING.value:
            return 1 if terrain != TerrainType.WALL else 999
        elif move_type_id == MovementType.GHOST.value:
            return 2 if terrain == TerrainType.WALL else 1
        elif move_type_id == MovementType.MOUNTAIN.value and terrain == TerrainType.MOUNTAIN:
            return 1
        elif move_type_id == MovementType.AQUATIC.value and terrain == TerrainType.WATER:
            return 1
        elif move_type_id == MovementType.FOREST.value and terrain == TerrainType.FOREST:
            return 1
        elif terrain == TerrainType.PLAIN:
            return 1
        elif terrain == TerrainType.FOREST:
            return 2
        elif terrain == TerrainType.MOUNTAIN:
            return 4 if move_type_id != MovementType.ARMORED.value else 999
        elif terrain == TerrainType.WATER:
            return 999
        elif terrain == TerrainType.WALL:
            return 999
        else:
            return 999
    
    def get_move_cost(self, unit, terrain: TerrainType) -> int:
        """ユニットの移動タイプと地形に基づいた移動コストを取得"""
        # ユニットからMovementTypeを取得
        move_type = unit.movement_type if hasattr(unit, 'movement_type') else MovementType.INFANTRY
        
        # カスタム移動コストがあればそれを優先
        unit_id = id(unit)
        if unit_id in self.custom_move_costs and terrain in self.custom_move_costs[unit_id]:
            return self.custom_move_costs[unit_id][terrain]
        
        # 移動タイプのデータを取得
        type_data = self.movement_data.get(move_type, self.movement_data.get(MovementType.INFANTRY))
        
        # 地形ごとの移動コストを取得
        terrain_costs = type_data.get('terrain_costs', {})
        
        # 特殊な移動特性を適用
        features = type_data.get('features', {})
        
        # 特殊状態の処理
        if terrain == TerrainType.WALL and features.get('pass_walls', False):
            return 2
        
        return terrain_costs.get(terrain, 999)
    
    def set_custom_move_cost(self, unit, terrain: TerrainType, cost: int):
        """ユニット個別の一時的な移動コスト修正を設定"""
        unit_id = id(unit)
        if unit_id not in self.custom_move_costs:
            self.custom_move_costs[unit_id] = {}
        self.custom_move_costs[unit_id][terrain] = cost
    
    def clear_custom_move_costs(self, unit=None):
        """カスタム移動コストをクリア"""
        if unit:
            unit_id = id(unit)
            if unit_id in self.custom_move_costs:
                del self.custom_move_costs[unit_id]
        else:
            self.custom_move_costs.clear()
    
    def get_terrain_features(self, unit, terrain: TerrainType) -> dict:
        """ユニットの移動タイプに基づいた地形の特殊効果を取得"""
        move_type = unit.movement_type if hasattr(unit, 'movement_type') else MovementType.INFANTRY
        type_data = self.movement_data.get(move_type, self.movement_data.get(MovementType.INFANTRY))
        features = type_data.get('features', {})
        
        result = {}
        
        # 地形ごとの特殊効果
        if terrain == TerrainType.FOREST and features.get('forest_bonus', False):
            result['dodge_bonus'] = 20
            result['defense_bonus'] = 2
        elif terrain == TerrainType.MOUNTAIN and features.get('mountain_bonus', False):
            result['dodge_bonus'] = 15
            result['defense_bonus'] = 3
        elif terrain == TerrainType.WATER and features.get('water_bonus', False):
            result['dodge_bonus'] = 10
            
        # その他の特殊効果
        if features.get('stealth', False):
            result['visibility_range'] = -1  # 視認距離の減少
        
        return result