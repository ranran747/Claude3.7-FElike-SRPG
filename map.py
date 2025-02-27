# map.py
import random
from typing import List, Tuple, Optional
from constants import TerrainType, TERRAIN_EFFECTS

class MapTile:
    def __init__(self, terrain_type: TerrainType):
        self.terrain_type = terrain_type
        self.unit = None

class GameMap:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.tiles = [[MapTile(TerrainType.PLAIN) for _ in range(cols)] for _ in range(rows)]
        self.units = []
    
    def generate_simple_map(self):
        # 簡単なマップを生成
        for row in range(self.rows):
            for col in range(self.cols):
                # 外周を壁にする
                if row == 0 or row == self.rows - 1 or col == 0 or col == self.cols - 1:
                    self.tiles[row][col].terrain_type = TerrainType.WALL
                # ランダムに森と山を配置
                elif random.random() < 0.1:
                    self.tiles[row][col].terrain_type = TerrainType.FOREST
                elif random.random() < 0.05:
                    self.tiles[row][col].terrain_type = TerrainType.MOUNTAIN
                elif random.random() < 0.02:
                    self.tiles[row][col].terrain_type = TerrainType.WATER

    def place_unit(self, unit, x: int, y: int) -> bool:
        if not self.is_valid_position(x, y) or self.tiles[y][x].unit is not None:
            return False
        
        unit.x = x
        unit.y = y
        self.tiles[y][x].unit = unit
        self.units.append(unit)
        return True

    def move_unit(self, unit, new_x: int, new_y: int) -> bool:
        if not self.is_valid_position(new_x, new_y) or self.tiles[new_y][new_x].unit is not None:
            return False
        
        # 現在の位置から単位を削除
        self.tiles[unit.y][unit.x].unit = None
        
        # 新しい位置に単位を配置
        unit.x = new_x
        unit.y = new_y
        self.tiles[new_y][new_x].unit = unit
        unit.has_moved = True
        return True

    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def get_move_cost(self, x: int, y: int) -> int:
        if not self.is_valid_position(x, y):
            return 999
        return TERRAIN_EFFECTS[self.tiles[y][x].terrain_type]["move_cost"]
    
    def get_terrain_dodge(self, x: int, y: int) -> int:
        if not self.is_valid_position(x, y):
            return 0
        return TERRAIN_EFFECTS[self.tiles[y][x].terrain_type]["dodge"]
    
    def get_terrain_defense(self, x: int, y: int) -> int:
        if not self.is_valid_position(x, y):
            return 0
        return TERRAIN_EFFECTS[self.tiles[y][x].terrain_type]["defense"]

    def get_unit_at(self, x: int, y: int) -> Optional:
        if not self.is_valid_position(x, y):
            return None
        return self.tiles[y][x].unit
    
    def calculate_movement_range(self, unit) -> List[Tuple[int, int]]:
        # ブレゼンハムのアルゴリズムを使用した移動範囲計算
        visited = {}
        queue = [(unit.x, unit.y, unit.movement)]
        
        while queue:
            x, y, remaining_move = queue.pop(0)
            
            # 既に訪れた位置で、より多くの移動ポイントを持っていた場合はスキップ
            if (x, y) in visited and visited[(x, y)] >= remaining_move:
                continue
                
            visited[(x, y)] = remaining_move
            
            # 移動ポイントが残っている場合、隣接するマスを探索
            if remaining_move > 0:
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if self.is_valid_position(nx, ny):
                        # ユニットがいる場合はスキップ（自分自身の場合を除く）
                        if self.get_unit_at(nx, ny) and (nx != unit.x or ny != unit.y):
                            continue
                            
                        # 地形の移動コスト
                        move_cost = self.get_move_cost(nx, ny)
                        new_remaining = remaining_move - move_cost
                        
                        if new_remaining >= 0:
                            queue.append((nx, ny, new_remaining))
        
        # 自分自身の位置を除外
        if (unit.x, unit.y) in visited:
            del visited[(unit.x, unit.y)]
            
        return list(visited.keys())
    
    def calculate_attack_range(self, unit, position: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        if not unit.equipped_weapon:
            return []
            
        x, y = position if position else (unit.x, unit.y)
        min_range = unit.equipped_weapon.range_min
        max_range = unit.equipped_weapon.range_max
        attack_positions = []
        
        for r in range(min_range, max_range + 1):
            for dx in range(-r, r + 1):
                dy_abs = r - abs(dx)
                for dy in [-dy_abs, dy_abs]:
                    if dy_abs == 0 and dx == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if self.is_valid_position(nx, ny):
                        attack_positions.append((nx, ny))
        
        return attack_positions
        
    def get_enemies_in_range(self, unit, attack_positions: List[Tuple[int, int]]) -> List:
        enemies = []
        for x, y in attack_positions:
            target = self.get_unit_at(x, y)
            if target and target.team != unit.team:
                enemies.append((target, x, y))
        return enemies
    
    def hide_unit(self, unit):
        """ユニットをマップから隠す（救出時など）"""
        if unit and unit.x >= 0 and unit.y >= 0:
            # タイルからユニットを削除
            self.tiles[unit.y][unit.x].unit = None
    
    def show_unit(self, unit, x, y):
        """ユニットをマップに表示する（降ろす時など）"""
        if unit:
            # 既にマップ上にいる場合は古い位置から削除
            if unit.x >= 0 and unit.y >= 0:
                self.tiles[unit.y][unit.x].unit = None
            
            # 新しい位置に配置
            unit.x = x
            unit.y = y
            self.tiles[y][x].unit = unit