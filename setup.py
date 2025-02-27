# setup.py
from unit import Unit
from weapon import Weapon
from constants import WeaponType
from skills import create_sample_skills
from movement_system import MovementType

def create_weapons():
    """サンプルの武器を作成する"""
    iron_sword = Weapon("Iron Sword", WeaponType.SWORD, 5, 90, 0, 5, 1, 1, 45)
    iron_lance = Weapon("Iron Lance", WeaponType.LANCE, 6, 80, 0, 7, 1, 1, 45)
    iron_axe = Weapon("Iron Axe", WeaponType.AXE, 8, 70, 0, 10, 1, 1, 45)
    iron_bow = Weapon("Iron Bow", WeaponType.BOW, 6, 85, 0, 5, 2, 2, 45)
    fire = Weapon("Fire", WeaponType.MAGIC, 5, 90, 0, 4, 1, 2, 40)
    
    return {
        "iron_sword": iron_sword,
        "iron_lance": iron_lance,
        "iron_axe": iron_axe,
        "iron_bow": iron_bow,
        "fire": fire
    }

def create_units(weapons):
    """ユニットを作成する"""
    # プレイヤーユニット
    marth = Unit("Marth", "Lord", 1, 20, 5, 0, 7, 9, 7, 5, 0, 5, 0, [weapons["iron_sword"]])
    roy = Unit("Roy", "Knight", 1, 24, 8, 0, 5, 4, 3, 9, 2, 4, 0, [weapons["iron_lance"]])
    lyn = Unit("Lyn", "Myrmidon", 1, 18, 4, 0, 9, 10, 8, 3, 2, 6, 0, [weapons["iron_sword"]])
    hector = Unit("Hector", "Fighter", 1, 26, 9, 0, 4, 5, 2, 8, 1, 4, 0, [weapons["iron_axe"]])
    robin = Unit("Robin", "Mage", 1, 16, 2, 7, 6, 6, 5, 2, 6, 5, 0, [weapons["fire"]])
    
    # 敵ユニット
    bandit1 = Unit("Bandit", "Fighter", 1, 22, 7, 0, 3, 4, 1, 6, 0, 4, 1, [weapons["iron_axe"]])
    bandit2 = Unit("Archer", "Archer", 1, 18, 5, 0, 7, 5, 2, 4, 0, 5, 1, [weapons["iron_bow"]])
    bandit3 = Unit("Soldier", "Soldier", 1, 20, 6, 0, 5, 5, 2, 5, 1, 4, 1, [weapons["iron_lance"]])
    bandit4 = Unit("Mage", "Mage", 1, 16, 1, 6, 6, 6, 3, 2, 5, 5, 1, [weapons["fire"]])
    
    player_units = [marth, roy, lyn, hector, robin]
    enemy_units = [bandit1, bandit2, bandit3, bandit4]
    
    return player_units, enemy_units

def add_skills_to_units(game_map):
    """ユニットにスキルを割り当てる"""
    skills = create_sample_skills()
    
    # スキルの割り当て例
    for unit in game_map.units:
        # 職業やキャラクターに応じたスキルの割り当て
        if unit.name == "Marth":
            unit.add_skill(skills[0])  # 連続攻撃
            unit.add_skill(skills[7])  # 太陽
        elif unit.name == "Roy":
            unit.add_skill(skills[3])  # 大盾
            unit.add_skill(skills[9])  # 斧殺し
        elif unit.name == "Lyn":
            unit.add_skill(skills[2])  # 連撃
            unit.add_skill(skills[5])  # 先制攻撃
        elif unit.name == "Hector":
            unit.add_skill(skills[6])  # 怒り
            unit.add_skill(skills[8])  # 剣の達人
        elif unit.name == "Robin":
            unit.add_skill(skills[1])  # 月光
            unit.add_skill(skills[4])  # 聖盾
        elif unit.name == "Bandit":
            unit.add_skill(skills[6])  # 怒り
        elif unit.name == "Archer":
            unit.add_skill(skills[2])  # 連撃
        elif unit.name == "Soldier":
            unit.add_skill(skills[3])  # 大盾
        elif unit.name == "Mage":
            unit.add_skill(skills[1])  # 月光

def setup_game(game_map):
    """ゲームの初期設定を行う"""
    # マップ生成
    game_map.generate_simple_map()
    
    # 武器とユニットの作成
    weapons = create_weapons()
    player_units, enemy_units = create_units(weapons)
    
    # プレイヤーユニットの配置と設定
    placement_positions = [
        (2, 2), (1, 3), (3, 3), (2, 4), (4, 2)
    ]
    
    for unit, (x, y) in zip(player_units, placement_positions):
        game_map.place_unit(unit, x, y)
        
        # 主人公の設定 - Marthを主人公に指定
        if unit.name == "Marth":
            unit.is_hero = True
            unit.is_important = True
    
    # 敵ユニットの配置と設定
    enemy_positions = [
        (12, 7), (10, 8), (11, 6), (9, 7)
    ]
    
    for i, (unit, (x, y)) in enumerate(zip(enemy_units, enemy_positions)):
        game_map.place_unit(unit, x, y)
        
        # AI役割の設定 - 敵ユニットに役割を割り当て
        if i == 0:  # bandit1
            unit.ai_role = "attacker"  # 攻撃役
        elif i == 1:  # bandit2
            unit.ai_role = "assassin"  # 暗殺者
        elif i == 2:  # bandit3
            unit.ai_role = "tank"      # タンク役
        elif i == 3:  # bandit4
            unit.ai_role = "healer"    # 回復役
    
    # スキルの割り当て
    add_skills_to_units(game_map)
    
    # 移動タイプの調整（必要に応じて）
    for unit in game_map.units:
        if unit.name == "Marth":
            unit.movement_type = MovementType.INFANTRY
        elif unit.name == "Hector":
            unit.movement_type = MovementType.ARMORED
        elif unit.name == "Roy":
            unit.movement_type = MovementType.CAVALRY
        elif unit.name == "Robin":
            unit.movement_type = MovementType.MAGE

def create_units(weapons):
    """ユニットを作成する"""
    # 既存のコード
    # プレイヤーユニット
    marth = Unit("Marth", "Lord", 1, 20, 5, 0, 7, 9, 7, 5, 0, 5, 0, [weapons["iron_sword"]])
    roy = Unit("Roy", "Knight", 1, 24, 8, 0, 5, 4, 3, 9, 2, 4, 0, [weapons["iron_lance"]])
    lyn = Unit("Lyn", "Myrmidon", 1, 18, 4, 0, 9, 10, 8, 3, 2, 6, 0, [weapons["iron_sword"]])
    hector = Unit("Hector", "Fighter", 1, 26, 9, 0, 4, 5, 2, 8, 1, 4, 0, [weapons["iron_axe"]])
    robin = Unit("Robin", "Mage", 1, 16, 2, 7, 6, 6, 5, 2, 6, 5, 0, [weapons["fire"]])
    
    # 移動タイプを明示的に設定（オプション）
    marth.movement_type = MovementType.INFANTRY
    roy.movement_type = MovementType.CAVALRY  
    lyn.movement_type = MovementType.INFANTRY
    hector.movement_type = MovementType.ARMORED
    robin.movement_type = MovementType.MAGE
    
    # 敵ユニット
    bandit1 = Unit("Bandit", "Fighter", 1, 22, 7, 0, 3, 4, 1, 6, 0, 4, 1, [weapons["iron_axe"]])
    bandit2 = Unit("Archer", "Archer", 1, 18, 5, 0, 7, 5, 2, 4, 0, 5, 1, [weapons["iron_bow"]])
    bandit3 = Unit("Soldier", "Soldier", 1, 20, 6, 0, 5, 5, 2, 5, 1, 4, 1, [weapons["iron_lance"]])
    bandit4 = Unit("Mage", "Mage", 1, 16, 1, 6, 6, 6, 3, 2, 5, 5, 1, [weapons["fire"]])
    
    player_units = [marth, roy, lyn, hector, robin]
    enemy_units = [bandit1, bandit2, bandit3, bandit4]
    
    return player_units, enemy_units

    