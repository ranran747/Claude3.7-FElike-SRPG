# unit.py
from typing import List, Dict, Optional
from constants import WeaponType
from weapon import Weapon
from skills import SkillTriggerType
from movement_system import MovementType  # 新たにインポート

class Unit:
    def __init__(self, name, unit_class, level, hp, strength, magic, skill, 
                 speed, luck, defense, resistance, movement, team, weapons=None, movement_type=MovementType.INFANTRY):  # 移動タイプを引数に追加):
        self.name = name
        self.unit_class = unit_class
        self.level = level
        self.max_hp = hp
        self.current_hp = hp
        self.strength = strength
        self.magic = magic
        self.skill = skill
        self.speed = speed
        self.luck = luck
        self.defense = defense
        self.resistance = resistance
        self.movement = movement
        self.team = team  # 0: プレイヤー, 1: 敵
        self.weapons = weapons or []
        self.equipped_weapon = weapons[0] if weapons else None
        self.x = 0
        self.y = 0
        self.has_moved = False
        self.has_attacked = False
        self.is_hero = False
        
        # 移動タイプを設定 - 新規追加
        self.movement_type = movement_type
        self._determine_movement_type_from_class()  # クラスに基づいて自動設定

        # スキル関連のフィールド
        self.skills = []
        self.temp_stat_modifiers = {}
        self.active_skills = []

        # 救出関連の属性を追加
        self.build = self._calculate_build()  # 体格（救出の判定に使用）
        self.is_mounted = "騎馬" in unit_class or "ペガサス" in unit_class or "ワイバーン" in unit_class
        self.is_flying = "ペガサス" in unit_class or "ワイバーン" in unit_class
        
        # 重要キャラフラグ（解雇不可キャラ用）- 新規追加
        self.is_important = False

        # 救出状態の管理
        self.rescuing = None  # 救出しているユニット
        self.rescued_by = None  # 救出されているユニット
        
        # アイテムボックス機能
        self.has_item_box_access = False  # アイテムボックスへのアクセス権

        # 特定の名前や条件の場合に主人公としてマーク
        if name == "Marth" or name == "主人公の名前":  # ゲームの主人公名に合わせて調整
            self.is_hero = True

        # AIの役割（敵ユニット用）
        self.ai_role = None  # "attacker", "defender", "healer", "support", "assassin", "tank"

    def _determine_movement_type_from_class(self):
        """ユニットクラスに基づいて移動タイプを自動設定"""
        # 職業名から移動タイプを推測
        class_name = self.unit_class.lower() if self.unit_class else ""
        
        # 自動判定ロジック
        if "ペガサス" in class_name or "pegasus" in class_name or "飛行" in class_name or "falcon" in class_name:
            self.movement_type = MovementType.FLYING
        elif "アーマー" in class_name or "armor" in class_name or "重騎士" in class_name or "general" in class_name:
            self.movement_type = MovementType.ARMORED
        elif "騎馬" in class_name or "paladin" in class_name or "cavalier" in class_name or "ソシアル" in class_name:
            self.movement_type = MovementType.CAVALRY
        elif "忍者" in class_name or "ninja" in class_name or "シーフ" in class_name or "thief" in class_name:
            self.movement_type = MovementType.NINJA
        elif "魔道" in class_name or "mage" in class_name or "sage" in class_name or "魔法" in class_name:
            self.movement_type = MovementType.MAGE
        elif "山賊" in class_name or "斧" in class_name or "berserker" in class_name:
            self.movement_type = MovementType.MOUNTAIN
        elif "海賊" in class_name or "sailor" in class_name or "海" in class_name:
            self.movement_type = MovementType.AQUATIC
        elif "森" in class_name or "猟兵" in class_name or "ranger" in class_name:
            self.movement_type = MovementType.FOREST
        elif "砂漠" in class_name or "desert" in class_name:
            self.movement_type = MovementType.DESERT
        elif "幽霊" in class_name or "ghost" in class_name or "亡霊" in class_name:
            self.movement_type = MovementType.GHOST
        else:
            # デフォルトは歩兵
            self.movement_type = MovementType.INFANTRY

    def get_attack_power(self) -> int:
        if not self.equipped_weapon:
            return 0
        if self.equipped_weapon.weapon_type == WeaponType.MAGIC:
            return self.magic + self.equipped_weapon.might
        return self.strength + self.equipped_weapon.might

    def get_hit_rate(self) -> int:
        if not self.equipped_weapon:
            return 0
        return self.equipped_weapon.hit + (self.skill * 2) + (self.luck // 2)

    def get_avoid(self) -> int:
        return (self.speed * 2) + self.luck

    def get_critical_rate(self) -> int:
        if not self.equipped_weapon:
            return 0
        return self.equipped_weapon.crit + (self.skill // 2)

    def get_attack_speed(self) -> int:
        if not self.equipped_weapon:
            return self.speed
        return max(0, self.speed - max(0, self.equipped_weapon.weight - (self.strength // 5)))
    
    def can_double_attack(self, target) -> bool:
        return self.get_attack_speed() >= target.get_attack_speed() + 4

    def is_dead(self) -> bool:
        return self.current_hp <= 0

    def end_turn(self):
        self.has_moved = False
        self.has_attacked = False
        
    # スキル関連のメソッド
    def add_skill(self, skill):
        """ユニットにスキルを追加する"""
        self.skills.append(skill)
        
    def remove_skill(self, skill_name):
        """ユニットからスキルを削除する"""
        self.skills = [s for s in self.skills if s.name != skill_name]
        self.active_skills = [s for s in self.active_skills if s.name != skill_name]
        
    def activate_skills(self, trigger_type, combat_data=None):
        """特定のトリガーに基づいてスキルをアクティブにする"""
        activated_skills = []
        for skill in self.skills:
            if skill.trigger_type == trigger_type:
                if skill.check_trigger(self, combat_data):
                    skill.is_active = True
                    self.active_skills.append(skill)
                    effect_result = skill.apply_effect(self, combat_data.get("target") if combat_data else None, combat_data)
                    activated_skills.append((skill, effect_result))
        return activated_skills
        
    def deactivate_skills(self):
        """アクティブなスキルを非アクティブにする"""
        for skill in self.active_skills:
            skill.is_active = False
        self.active_skills = []
        self.temp_stat_modifiers = {}
    
    def _calculate_build(self):
        """ユニットの体格を計算（救出判定用）"""
        # 体格の基本値（職業によって異なる）
        base_build = {
            "ロード": 5,
            "ソードマスター": 7,
            "ヒーロー": 8,
            "戦士": 9,
            "傭兵": 6,
            "アーマー": 13,
            "ナイト": 11,
            "ペガサスナイト": 5,
            "ワイバーンナイト": 9,
            "ソシアルナイト": 8,
            "魔道士": 5,
            "僧侶": 5,
            "シーフ": 6
        }
        
        # 基本値 + (力 / 5) を体格とする
        class_build = base_build.get(self.unit_class, 7)  # デフォルト値は7
        return class_build + (self.strength // 5)
    
    def can_rescue(self, target):
        """対象ユニットを救出できるかどうか判定"""
        # 自分が救出中または救出されている場合は不可
        if self.rescuing or self.rescued_by:
            return False
        
        # 対象が救出中または救出されている場合は不可
        if target.rescuing or target.rescued_by:
            return False
        
        # 敵ユニットは通常の救出不可（捕獲・投降用メソッドを別に用意）
        if self.team != target.team:
            return False
        
        # 騎馬・飛行ユニットは救出できない（捕獲例外あり）
        if self.is_mounted:
            return False
        
        # 体格チェック：救出側 > 被救出側
        # return self.build >= target.build
        
        # 全ての条件を満たした場合
        return True
    
    def rescue(self, target):
        """ユニットを救出する"""
        if not self.can_rescue(target):
            return False
        
        # 救出状態を設定
        self.rescuing = target
        target.rescued_by = self
        
        # ステータス修正（技・速さ半減）
        self.apply_rescue_penalty()
        
        return True
    
    def can_drop(self, x, y, game_map):
        """救出したユニットを指定マスに下ろせるか判定"""
        if not self.rescuing:
            return False
        
        # 指定マスが地形的に進入可能かチェック
        tile = game_map.tiles[y][x]
        if not self.rescuing.can_enter_terrain(tile.terrain_type):
            return False
        
        # 指定マスに他のユニットがいないかチェック
        if game_map.get_unit_at(x, y):
            return False
        
        # 指定マスが隣接しているかチェック
        if abs(self.x - x) + abs(self.y - y) != 1:
            return False
        
        return True
    
    def drop(self, x, y, game_map):
        """救出したユニットを指定マスに下ろす"""
        if not self.can_drop(x, y, game_map):
            return False
        
        dropped_unit = self.rescuing
        
        # 救出状態を解除
        self.rescuing = None
        dropped_unit.rescued_by = None
        
        # ステータス修正を元に戻す
        self.remove_rescue_penalty()
        
        # ユニットをマップに配置
        game_map.place_unit(dropped_unit, x, y)
        dropped_unit.has_moved = True  # そのターン行動済みにする
        
        return True
    
    def apply_rescue_penalty(self):
        """救出によるステータス修正を適用"""
        # 技・速さの半減
        self.skill = self.skill // 2
        self.speed = self.speed // 2
        
        # 歩兵は移動力も半減
        if not self.is_mounted:
            self.movement = max(1, self.movement // 2)
    
    def remove_rescue_penalty(self):
        """救出によるステータス修正を元に戻す"""
        # 元のステータスに戻す（元の値を保存しておく必要あり）
        # 実際の実装では、元の値を保存しておく仕組みが必要
        pass
    
    def can_capture(self, target):
        """対象ユニットを捕獲できるかどうか判定"""
        # 自分が救出中の場合は不可
        if self.rescuing:
            return False
        
        # 対象が敵ユニットでない場合は不可
        if self.team == target.team:
            return False
        
        # 対象が救出されている場合は不可
        if target.rescued_by:
            return False
        
        # 体格チェックは不要（捕獲は特殊な救出）
        
        return True
    
    def can_capture_without_battle(self, target):
        """対象ユニットを戦闘なしで捕獲（投降）できるかどうか判定"""
        # 通常の捕獲条件を満たしているか
        if not self.can_capture(target):
            return False
        
        # 対象のHPが1桁かチェック
        return target.current_hp < 10
    
    def get_capture_battle_stats(self):
        """捕獲時の戦闘ステータスを取得（技・速さ半減）"""
        # 技・速さが半減した一時的なステータスを返す
        stats = {
            "skill": self.skill // 2,
            "speed": self.speed // 2
        }
        return stats