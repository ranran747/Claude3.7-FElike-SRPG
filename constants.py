# constants.py
import pygame
from enum import Enum

# 定数
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRID_SIZE = 32
MAP_ROWS = 10
MAP_COLS = 15

# 色の定義
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)

# 地形タイプ
class TerrainType(Enum):
    PLAIN = 1
    FOREST = 2
    MOUNTAIN = 3
    WATER = 4
    WALL = 5

# 地形効果
TERRAIN_EFFECTS = {
    TerrainType.PLAIN: {"move_cost": 1, "dodge": 0, "defense": 0},
    TerrainType.FOREST: {"move_cost": 2, "dodge": 20, "defense": 1},
    TerrainType.MOUNTAIN: {"move_cost": 3, "dodge": 10, "defense": 2},
    TerrainType.WATER: {"move_cost": 4, "dodge": 0, "defense": 0},
    TerrainType.WALL: {"move_cost": 999, "dodge": 0, "defense": 0},
}

# 武器タイプ
class WeaponType(Enum):
    SWORD = 1
    LANCE = 2
    AXE = 3
    BOW = 4
    MAGIC = 5

# 武器相性
WEAPON_TRIANGLE = {
    WeaponType.SWORD: {WeaponType.AXE: 1, WeaponType.LANCE: -1},
    WeaponType.LANCE: {WeaponType.SWORD: 1, WeaponType.AXE: -1},
    WeaponType.AXE: {WeaponType.LANCE: 1, WeaponType.SWORD: -1},
}