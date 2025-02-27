# game_manager.py
from typing import List, Tuple, Dict, Optional, Callable
import random
import os
from combat_integration import EnhancedCombatSystem
from support_system import SupportSystem, SupportLevel
from legendary_items import LegendaryItemGenerator, LegendaryWeapon, ItemRarity
from skills import SkillTriggerType, SkillEffectType

class GameManager:
    def __init__(self, game_map):
        # 基本システム
        self.game_map = game_map
        self.current_turn = 0
        self.turn_player = 0  # 0: プレイヤー, 1: 敵
        self.selected_unit = None
        self.move_targets = []
        self.attack_targets = []
        self.combat_results = None
        self.combat_animation_active = False
        self.phase = "select_unit"  # select_unit, move_unit, select_action, select_attack_target
        
        # 拡張システム
        self.support_system = SupportSystem("data/supports/")
        self.legendary_generator = LegendaryItemGenerator()
        
        # インベントリシステム
        self.inventory = []  # ユニットに所属しない共有アイテム
        
        # UI関連のコールバック
        self.on_support_level_up = None  # 支援レベルアップ時のコールバック
        self.on_item_drop = None  # アイテムドロップ時のコールバック
        self.on_level_up = None  # レベルアップ時のコールバック
        
        # デバッグ用のアイテム
        if os.path.exists("debug_mode"):
            self._add_debug_items()
        
        # 初期支援関係の設定
        self._setup_default_supports()
    
    def _add_debug_items(self):
        """デバッグ用の初期アイテム追加"""
        # 各レア度のテスト武器
        for rarity in [ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
            for _ in range(2):  # 各2つずつ
                weapon = self.legendary_generator.generate_legendary_weapon(rarity)
                self.inventory.append(weapon)
    
    def _setup_default_supports(self):
        """初期支援関係の設定"""
        # ユニットのリストを取得
        player_units = [unit for unit in self.game_map.units if unit.team == 0]
        
        # プレイヤーユニット間の支援関係を設定
        for i, unit1 in enumerate(player_units):
            for unit2 in player_units[i+1:]:
                # デフォルトではAランクまでの支援を設定
                self.support_system.register_support_pair(unit1.name, unit2.name, SupportLevel.A)
    
    def select_unit(self, x: int, y: int) -> bool:
        """ユニットを選択"""
        unit = self.game_map.get_unit_at(x, y)
        if unit and unit.team == self.turn_player and not unit.has_moved:
            self.selected_unit = unit
            self.move_targets = self.game_map.calculate_movement_range(unit)
            self.phase = "move_unit"
            return True
        return False
    
    def move_selected_unit(self, x: int, y: int) -> bool:
        """選択中のユニットを移動"""
        if not self.selected_unit or (x, y) not in self.move_targets:
            return False
        
        if self.game_map.move_unit(self.selected_unit, x, y):
            self.attack_targets = self.game_map.calculate_attack_range(self.selected_unit)
            enemies = self.game_map.get_enemies_in_range(self.selected_unit, self.attack_targets)
            
            if enemies and not self.selected_unit.has_attacked:
                self.phase = "select_action"
            else:
                self.end_unit_turn()
            return True
        return False
    
    def select_action(self, action: str) -> bool:
        """ユニットのアクションを選択"""
        if action == "attack":
            enemies = self.game_map.get_enemies_in_range(
                self.selected_unit, 
                self.game_map.calculate_attack_range(self.selected_unit)
            )
            if enemies:
                self.phase = "select_attack_target"
                return True
        elif action == "wait":
            self.end_unit_turn()
            return True
        elif action == "item":
            # アイテム使用機能（未実装）
            return False
        elif action == "support":
            # 支援会話表示（UIコールバックに委譲）
            # 表示可能な支援会話を取得
            available_supports = []
            for char1, char2, level in self.support_system.get_available_conversations():
                # 現在選択中のユニットが関わる支援のみ
                if self.selected_unit.name in [char1, char2]:
                    available_supports.append((char1, char2, level))
            
            # 支援会話が存在する場合
            if available_supports:
                # UIコールバックがあれば実行（支援会話リスト表示）
                if hasattr(self, "on_show_support_list") and self.on_show_support_list:
                    self.on_show_support_list(self.selected_unit.name)
                    return True
            return False
        return False
    
    def select_attack_target(self, x: int, y: int) -> bool:
        """攻撃対象を選択"""
        target = self.game_map.get_unit_at(x, y)
        if not target or target.team == self.selected_unit.team:
            return False
        
        attack_positions = self.game_map.calculate_attack_range(self.selected_unit)
        if (x, y) in attack_positions:
            # 拡張戦闘システムを使用
            self.combat_results = EnhancedCombatSystem.perform_combat(
                self.selected_unit, target, self.game_map, self.support_system
            )
            self.combat_animation_active = True
            self.selected_unit.has_attacked = True
            
            # 敵を倒した場合、アイテムドロップ判定
            if target.is_dead():
                self._check_item_drop(target)
                
                # 支援ポイント加算（キル時のボーナス）
                self._add_kill_support_points(self.selected_unit)
                
                # 経験値獲得
                self._award_experience(self.selected_unit, target)
            else:
                # 敵を倒せなかった場合も経験値獲得（少なめ）
                self._award_experience(self.selected_unit, target, defeated=False)
            
            self.end_unit_turn()
            return True
        return False
    
    def _award_experience(self, attacker, defender, defeated=True):
        """経験値の付与とレベルアップ処理"""
        from growth_system import GrowthSystem
        growth_system = GrowthSystem()
        
        # 戦闘から経験値を計算
        exp_amount = growth_system.calculate_combat_exp(attacker, defender, self.combat_results)
        
        # 経験値を増加（倒せなかった場合は半減）
        if not defeated:
            exp_amount = max(1, exp_amount // 2)
        
        # 経験値を付与し、レベルアップ判定
        level_up, stat_gains = growth_system.award_exp(attacker, exp_amount)
        
        # レベルアップした場合
        if level_up:
            # UIコールバックがあれば実行
            if self.on_level_up:
                self.on_level_up(attacker, stat_gains)
    
    def _check_item_drop(self, defeated_unit):
        """敵を倒した時のアイテムドロップ判定"""
        legendary_weapon = EnhancedCombatSystem.generate_reward_weapon(
            defeated_unit, self.combat_results
        )
        
        if legendary_weapon:
            if self.on_item_drop:
                # UIコールバックを呼び出し
                self.on_item_drop(legendary_weapon)
            else:
                # UI機能がなければ自動的にインベントリに追加
                self.inventory.append(legendary_weapon)
    
    def _add_kill_support_points(self, unit):
        """ユニットが敵を倒した時に支援ポイントを加算"""
        # ユニットと、3マス以内の味方全員で支援ポイント追加
        for other_unit in self.game_map.units:
            if other_unit.team == unit.team and other_unit != unit and not other_unit.is_dead():
                distance = abs(unit.x - other_unit.x) + abs(unit.y - other_unit.y)
                if distance <= 3:
                    # キルボーナスとして支援ポイント追加
                    level_up, new_level = self.support_system.add_support_points(
                        unit.name, other_unit.name, 10  # キルボーナス10ポイント
                    )
                    
                    # 支援レベルアップ通知
                    if level_up and self.on_support_level_up:
                        self.on_support_level_up(unit.name, other_unit.name, new_level)
    
    def end_unit_turn(self):
        """ユニットのターン終了"""
        self.selected_unit = None
        self.move_targets = []
        self.attack_targets = []
        self.phase = "select_unit"
    
    def end_player_turn(self):
        """プレイヤーのターン終了"""
        # 隣接しているユニットの支援ポイント処理
        self._process_adjacent_units_support()
        
        # 通常のターン終了処理
        for unit in self.game_map.units:
            if unit.team == self.turn_player:
                unit.end_turn()
        
        self.turn_player = 1 - self.turn_player
        if self.turn_player == 0:
            self.current_turn += 1
        
        self.phase = "select_unit"
    
    def _process_adjacent_units_support(self):
        """ターン終了時、隣接するユニット間の支援ポイント処理"""
        processed_pairs = set()
        
        # すべてのプレイヤーユニットをチェック
        player_units = [unit for unit in self.game_map.units if unit.team == 0 and not unit.is_dead()]
        
        for unit1 in player_units:
            for unit2 in player_units:
                if unit1 == unit2:
                    continue
                
                # 既に処理したペアはスキップ
                pair_key = tuple(sorted([unit1.name, unit2.name]))
                if pair_key in processed_pairs:
                    continue
                
                # 隣接するユニット間の支援ポイント
                distance = abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
                if distance == 1:  # 隣接している場合
                    # 支援ポイント付与
                    level_up, new_level = self.support_system.record_adjacent_turns(unit1.name, unit2.name)
                    
                    # 支援レベルアップ通知
                    if level_up and self.on_support_level_up:
                        self.on_support_level_up(unit1.name, unit2.name, new_level)
                
                processed_pairs.add(pair_key)
    
    def execute_ai_turn(self):
        """AIのターン実行"""
        if self.turn_player != 1:
            return
        
        for unit in self.game_map.units:
            if unit.team != 1 or unit.has_moved or unit.is_dead():
                continue
            
            # 移動範囲の計算
            move_positions = self.game_map.calculate_movement_range(unit)
            
            # 各移動位置から攻撃可能な敵をチェック
            best_target = None
            best_damage = -1
            best_position = None
            
            for pos_x, pos_y in move_positions:
                attack_positions = self.game_map.calculate_attack_range(unit, (pos_x, pos_y))
                for attack_x, attack_y in attack_positions:
                    target = self.game_map.get_unit_at(attack_x, attack_y)
                    if target and target.team != unit.team:
                        damage = EnhancedCombatSystem.calculate_damage(unit, target, self.game_map, self.support_system)
                        hit_chance = EnhancedCombatSystem.calculate_hit_chance(unit, target, self.game_map, self.support_system)
                        expected_damage = damage * hit_chance / 100
                        
                        if expected_damage > best_damage:
                            best_damage = expected_damage
                            best_target = target
                            best_position = (pos_x, pos_y)
            
            # 最適な行動を実行
            if best_target and best_position:
                self.game_map.move_unit(unit, best_position[0], best_position[1])
                unit.has_moved = True
                
                # 攻撃実行
                combat_results = EnhancedCombatSystem.perform_combat(unit, best_target, self.game_map, self.support_system)
                unit.has_attacked = True
                
                # プレイヤーユニットが倒された場合の経験値処理（AIにはレベルアップなし）
                if best_target.is_dead() and best_target.team == 0:
                    # プレイヤーユニットは復活するが、経験値やドロップはなし
                    best_target.current_hp = 1  # 仮の処理：戦線離脱ではなく復活
        
        self.end_player_turn()
    
    def equip_weapon(self, unit, weapon):
        """ユニットに武器を装備"""
        if not unit or not weapon:
            return False
        
        # 装備可能か確認
        if isinstance(weapon, LegendaryWeapon) and not weapon.can_equip(unit):
            return False
        
        # 現在装備中の武器をインベントリに戻す（あれば）
        if unit.equipped_weapon:
            self.inventory.append(unit.equipped_weapon)
        
        # 新しい武器を装備
        unit.equipped_weapon = weapon
        
        # インベントリから削除
        if weapon in self.inventory:
            self.inventory.remove(weapon)
        
        return True
    
    def add_item_to_inventory(self, item):
        """アイテムをインベントリに追加"""
        self.inventory.append(item)
    
    def remove_item_from_inventory(self, item):
        """インベントリからアイテムを削除"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def get_available_support_conversations(self, unit_name=None):
        """閲覧可能な支援会話のリストを取得"""
        available = self.support_system.get_available_conversations()
        
        # 特定ユニットに絞り込み
        if unit_name:
            available = [(char1, char2, level) for char1, char2, level in available
                         if char1 == unit_name or char2 == unit_name]
        
        return available
    
    def view_support_conversation(self, char1, char2, level=None):
        """支援会話を表示"""
        conversation = self.support_system.get_conversation(char1, char2, level)
        if conversation:
            # 会話を既読にする
            self.support_system.mark_conversation_viewed(char1, char2, level)
            return conversation
        return None
    
    def save_game_data(self):
        """ゲームデータのセーブ処理"""
        # 支援データの保存
        self.support_system.save_support_data()
        
        # その他のデータ保存（未実装）
    
    def get_unit_stats_with_equipment(self, unit):
        """装備品の効果を含めたユニットの能力値を取得"""
        stats = {
            "strength": unit.strength,
            "magic": unit.magic,
            "skill": unit.skill,
            "speed": unit.speed,
            "luck": unit.luck,
            "defense": unit.defense,
            "resistance": unit.resistance
        }
        
        # 装備武器の効果を適用
        if unit.equipped_weapon and isinstance(unit.equipped_weapon, LegendaryWeapon):
            for effect in unit.equipped_weapon.effects:
                if effect.effect_type == "stat_boost":
                    for stat, value in effect.effect_value.get("stats", {}).items():
                        if stat in stats:
                            stats[stat] += value
        
        return stats
    
    def add_unit_to_party(self, unit):
        """新しいユニットをパーティーに追加"""
        # ユニットをマップに追加（実際のゲーム進行では適切な位置調整が必要）
        self.game_map.units.append(unit)
        
        # 支援関係の初期化（既存ユニットとの支援関係を設定）
        for existing_unit in self.game_map.units:
            if existing_unit != unit and existing_unit.team == unit.team:
                self.support_system.register_support_pair(unit.name, existing_unit.name)

    def remove_unit_from_party(self, unit):
        """ユニットをパーティーから削除"""
        if unit in self.game_map.units:
            self.game_map.units.remove(unit)
            
            # マップタイルからの削除
            if hasattr(unit, 'x') and hasattr(unit, 'y'):
                tile = self.game_map.tiles[unit.y][unit.x]
                if tile.unit == unit:
                    tile.unit = None

    def get_dead_units(self):
        """戦死したユニットのリストを取得"""
        # 実際のゲームでは戦死ユニットの管理方法に応じて実装
        return []  # 仮の実装

    def revive_unit(self, unit):
        """ユニットを復活させる"""
        # 戦死状態をリセット
        unit.current_hp = 1
        unit.death_status = None
        
        # パーティーに再追加
        self.add_unit_to_party(unit)

    def get_shop_weapons(self):
        """販売中の武器リストを取得"""
        # 実際のゲームでは街や進行状況に応じた武器リストを返す
        from weapon import Weapon
        from constants import WeaponType
        
        # 仮の武器リスト
        weapons = [
            Weapon("鉄の剣", WeaponType.SWORD, 5, 90, 0, 5, 1, 1, 45),
            Weapon("鋼の剣", WeaponType.SWORD, 8, 85, 0, 8, 1, 1, 35),
            Weapon("鉄の槍", WeaponType.LANCE, 6, 80, 0, 7, 1, 1, 45),
            Weapon("鋼の槍", WeaponType.LANCE, 9, 75, 0, 9, 1, 1, 35),
            Weapon("鉄の斧", WeaponType.AXE, 8, 70, 0, 10, 1, 1, 45),
            Weapon("鋼の斧", WeaponType.AXE, 11, 65, 0, 12, 1, 1, 35),
            Weapon("鉄の弓", WeaponType.BOW, 6, 85, 0, 5, 2, 2, 45),
            Weapon("鋼の弓", WeaponType.BOW, 9, 80, 0, 7, 2, 2, 35),
            Weapon("ファイアー", WeaponType.MAGIC, 5, 90, 0, 4, 1, 2, 40),
            Weapon("サンダー", WeaponType.MAGIC, 8, 80, 5, 6, 1, 2, 35)
        ]
        
        # 価格情報の追加（実際のWeaponクラスに価格属性がない場合）
        for weapon in weapons:
            weapon.price = weapon.might * 200 + 500
        
        return weapons

    def prepare_save_data(self):
        """セーブ用のゲームデータを準備"""
        # セーブに必要なデータを収集
        save_data = {
            "save_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "play_time": 0,  # プレイ時間（実際のゲームでは計測）
            "gold": self.player_gold,
            "party": [],  # ユニットデータ
            "inventory": [],  # アイテムデータ
            "current_scenario": "",  # 現在のシナリオ
            "completed_maps": [],  # クリア済みマップ
            "progress": {}  # その他の進行状況
        }
        
        # ユニットデータの保存
        for unit in self.game_map.units:
            if unit.team == 0:  # プレイヤーユニットのみ
                unit_data = {
                    "name": unit.name,
                    "class": unit.unit_class,
                    "level": unit.level,
                    "exp": unit.exp,
                    "hp": unit.max_hp,
                    "current_hp": unit.current_hp,
                    "strength": unit.strength,
                    "magic": unit.magic,
                    "skill": unit.skill,
                    "speed": unit.speed,
                    "luck": unit.luck,
                    "defense": unit.defense,
                    "resistance": unit.resistance,
                    "movement": unit.movement,
                    "skills": [skill.name for skill in unit.skills],
                    "weapons": []  # 武器データ
                }
                
                # 武器データの保存
                for weapon in unit.weapons:
                    weapon_data = {
                        "name": weapon.name,
                        "type": weapon.weapon_type.name,
                        "durability": weapon.durability
                    }
                    
                    # レジェンダリー武器の場合は追加データ
                    if hasattr(weapon, 'rarity'):
                        weapon_data["legendary"] = True
                        weapon_data["rarity"] = weapon.rarity.name
                    
                    unit_data["weapons"].append(weapon_data)
                
                save_data["party"].append(unit_data)
        
        # インベントリデータの保存
        for item in self.inventory:
            item_data = {
                "name": item.name,
                "type": "weapon" if hasattr(item, "weapon_type") else "item"
            }
            
            if item_data["type"] == "weapon":
                item_data["weapon_type"] = item.weapon_type.name
                item_data["durability"] = item.durability
                
                # レジェンダリー武器の場合は追加データ
                if hasattr(item, 'rarity'):
                    item_data["legendary"] = True
                    item_data["rarity"] = item.rarity.name
            
            save_data["inventory"].append(item_data)
        
        # 支援関係データの保存
        self.support_system.save_support_data()
        
        return save_data

    def load_game_data(self, save_data):
        """セーブデータをロード"""
        # 基本情報の復元
        self.player_gold = save_data.get("gold", 0)
        
        # ユニットの復元
        # インベントリの復元
        # 進行状況の復元
        # （実際のゲームではより複雑な処理が必要）
        
        # 支援データの復元
        self.support_system.load_support_data()