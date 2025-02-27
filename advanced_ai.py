# advanced_ai.py
from typing import List, Dict, Tuple, Set, Optional
import random
import math
from constants import TerrainType
from movement_system import MovementType

class TacticalAction:
    """AIが実行する戦術的行動を表すクラス"""
    def __init__(self, 
                 action_type: str,            # 'move', 'attack', 'use_item', 'wait', etc.
                 priority: int,               # 行動の優先度（高いほど優先）
                 unit = None,                 # 実行するユニット
                 target_position: Tuple = None,  # 対象位置 (x, y)
                 target_unit = None,          # 対象ユニット（攻撃対象など）
                 item = None,                 # 使用するアイテム
                 expected_damage: int = 0,    # 期待される与ダメージ
                 expected_risk: int = 0):     # 期待されるリスク（被ダメージなど）
        self.action_type = action_type
        self.priority = priority
        self.unit = unit
        self.target_position = target_position
        self.target_unit = target_unit
        self.item = item
        self.expected_damage = expected_damage
        self.expected_risk = expected_risk
    
    def __str__(self):
        """デバッグ用の文字列表現"""
        return (
            f"{self.action_type.upper()} | "
            f"Priority: {self.priority} | "
            f"Unit: {self.unit.name if self.unit else 'None'} | "
            f"Target Pos: {self.target_position} | "
            f"Target Unit: {self.target_unit.name if self.target_unit else 'None'} | "
            f"Expected Damage: {self.expected_damage} | "
            f"Expected Risk: {self.expected_risk}"
        )


class AIRole:
    """AIユニットの役割定義"""
    ATTACKER = "attacker"       # 攻撃重視
    DEFENDER = "defender"       # 防御重視
    HEALER = "healer"           # 回復役
    SUPPORT = "support"         # バフ/デバフ役
    ASSASSIN = "assassin"       # 高機動・高火力
    TANK = "tank"               # 壁役（タンク）


class AdvancedAI:
    """強化されたAIシステム"""
    def __init__(self, game_manager, movement_system=None):
        self.game_manager = game_manager
        self.movement_system = movement_system
        
        # ユニットごとの役割
        self.unit_roles = {}
        
        # 撤退判断に使うHP閾値
        self.retreat_threshold = 0.3  # HPが最大の30%以下で撤退を検討
        
        # 記憶（ターン間でのAI判断を改善するための情報）
        self.memory = {
            'player_targeting': {},  # プレイヤーの標的になりやすいユニット
            'player_damage_dealt': {},  # プレイヤーの与ダメージ量
            'player_tendencies': {
                'aggressive': 0,     # 積極的な攻撃傾向
                'defensive': 0,      # 守備的な傾向
                'focus_weak': 0,     # 弱いユニットを集中攻撃する傾向
                'focus_strong': 0,   # 強いユニットを優先する傾向
            },
            'terrain_preference': {},  # 地形の選好傾向
        }
        
        # 危険地帯（プレイヤーの攻撃範囲）
        self.danger_map = []
        
        # 初期セットアップ
        self._initialize()
    
    def _initialize(self):
        """初期セットアップ"""
        # 役割の自動割り当て
        self._assign_roles()
    
    def _assign_roles(self):
        """AIユニットに役割を割り当てる"""
        ai_units = [unit for unit in self.game_manager.game_map.units if unit.team == 1]
        
        # ユニットごとに役割を判断
        for unit in ai_units:
            if hasattr(unit, "ai_role") and unit.ai_role:
                # 既に役割が設定されている場合はそれを使用
                self.unit_roles[unit.name] = unit.ai_role
                continue
            
            # 自動的に役割を割り当て
            role = self._determine_role(unit)
            self.unit_roles[unit.name] = role
    
    def _determine_role(self, unit) -> str:
        """ユニットに適した役割を判断"""
        # 回復役の判定
        if any(weapon.name.lower() in ['heal', 'heal staff', 'mend', 'recover', '回復', 'ヒール'] 
               for weapon in unit.weapons if weapon):
            return AIRole.HEALER
        
        # 役割の判定基準
        if unit.current_hp >= 40 and unit.defense >= 10:
            return AIRole.TANK
        elif unit.speed >= 10 and unit.skill >= 10:
            return AIRole.ASSASSIN
        elif unit.defense >= 8 and unit.resistance >= 8:
            return AIRole.DEFENDER
        elif hasattr(unit, 'is_support') and unit.is_support:
            return AIRole.SUPPORT
        else:
            return AIRole.ATTACKER
    
    def update_danger_map(self):
        """プレイヤーユニットの攻撃可能範囲を計算してマップ化"""
        game_map = self.game_manager.game_map
        rows, cols = game_map.rows, game_map.cols
        
        # 危険度マップを初期化（0 = 安全, 数値が大きいほど危険）
        self.danger_map = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # プレイヤーユニットの攻撃可能範囲を計算
        player_units = [unit for unit in game_map.units if unit.team == 0 and not unit.is_dead()]
        
        for unit in player_units:
            # ユニットの移動可能範囲を計算
            move_positions = game_map.calculate_movement_range(unit)
            
            # 各移動位置から攻撃可能な範囲を計算
            for pos_x, pos_y in move_positions:
                attack_positions = game_map.calculate_attack_range(unit, (pos_x, pos_y))
                
                # 攻撃範囲の各マスの危険度を上げる
                for attack_x, attack_y in attack_positions:
                    if 0 <= attack_x < cols and 0 <= attack_y < rows:
                        # 危険度に攻撃力を加味する
                        attack_power = unit.get_attack_power()
                        self.danger_map[attack_y][attack_x] += attack_power
    
    def execute_turn(self) -> bool:
        """AIターンを実行する"""
        if self.game_manager.turn_player != 1:  # AIは1番のチーム
            return False
        
        # 危険マップを更新
        self.update_danger_map()
        
        # AIユニットのリスト
        ai_units = [unit for unit in self.game_manager.game_map.units 
                    if unit.team == 1 and not unit.has_moved and not unit.is_dead()]
        
        # 役割に応じて行動順を調整
        ai_units.sort(key=lambda unit: self._get_action_priority(unit))
        
        # 各ユニットの行動を決定して実行
        for unit in ai_units:
            # 行動可能な最適なアクションを決定
            action = self._decide_best_action(unit)
            
            # アクションを実行
            if action:
                self._execute_action(action)
        
        # ターン終了
        self.game_manager.end_player_turn()
        return True
    
    def _get_action_priority(self, unit) -> int:
        """ユニットの行動優先順位を決定"""
        role = self.unit_roles.get(unit.name, AIRole.ATTACKER)
        
        # 役割ごとの優先度
        priorities = {
            AIRole.HEALER: 1,      # 回復役が最初に行動
            AIRole.SUPPORT: 2,     # 次にサポート役
            AIRole.TANK: 3,        # その次に壁役
            AIRole.DEFENDER: 4,
            AIRole.ATTACKER: 5,
            AIRole.ASSASSIN: 6,    # 攻撃役は後半
        }
        
        # 基本優先度
        priority = priorities.get(role, 5)
        
        # HP残量が少ないユニットは優先的に行動
        hp_ratio = unit.current_hp / unit.max_hp
        if hp_ratio < self.retreat_threshold:
            priority -= 3  # 撤退が必要なユニットは最優先
        
        return priority
    
    def _decide_best_action(self, unit) -> Optional[TacticalAction]:
        """ユニットの最適な行動を決定"""
        # 役割に応じた行動生成
        role = self.unit_roles.get(unit.name, AIRole.ATTACKER)
        
        actions = []
        
        # HP残量に応じた行動生成
        hp_ratio = unit.current_hp / unit.max_hp
        if hp_ratio < self.retreat_threshold:
            # 撤退アクション
            retreat_action = self._generate_retreat_action(unit)
            if retreat_action:
                actions.append(retreat_action)
        
        # 役割に応じたアクション生成
        if role == AIRole.HEALER:
            actions.extend(self._generate_healer_actions(unit))
        elif role == AIRole.SUPPORT:
            actions.extend(self._generate_support_actions(unit))
        elif role == AIRole.TANK:
            actions.extend(self._generate_tank_actions(unit))
        elif role == AIRole.ASSASSIN:
            actions.extend(self._generate_assassin_actions(unit))
        elif role == AIRole.DEFENDER:
            actions.extend(self._generate_defender_actions(unit))
        else:  # ATTACKER またはその他
            actions.extend(self._generate_attacker_actions(unit))
        
        # 待機アクションを追加（他に選択肢がない場合のフォールバック）
        actions.append(TacticalAction(
            action_type='wait',
            priority=0,
            unit=unit,
            target_position=(unit.x, unit.y)
        ))
        
        # 優先度でソート
        actions.sort(key=lambda action: action.priority, reverse=True)
        
        # 最も優先度の高い行動を選択
        return actions[0] if actions else None
    
    def _generate_healer_actions(self, unit) -> List[TacticalAction]:
        """回復役の行動を生成"""
        actions = []
        game_map = self.game_manager.game_map
        
        # 回復アイテムや杖を持っているか確認
        heal_weapons = [weapon for weapon in unit.weapons 
                        if weapon and weapon.name.lower() in ['heal', 'heal staff', 'mend', 'recover', '回復', 'ヒール']]
        
        if heal_weapons:
            heal_weapon = heal_weapons[0]
            unit.equipped_weapon = heal_weapon
            
            # 移動可能範囲
            move_positions = game_map.calculate_movement_range(unit)
            
            for pos_x, pos_y in move_positions:
                # この位置から回復可能なマスを計算
                heal_range = heal_weapon.range_max
                potential_heal_targets = []
                
                # 同じチームの負傷したユニットを探す
                for ally in game_map.units:
                    if ally.team == unit.team and not ally.is_dead() and ally != unit:
                        # HPが最大値より少ないユニットのみ
                        if ally.current_hp < ally.max_hp:
                            distance = abs(pos_x - ally.x) + abs(pos_y - ally.y)
                            if distance <= heal_range:
                                # 回復量を計算（実際のゲームロジックに合わせて調整）
                                heal_amount = min(ally.max_hp - ally.current_hp, unit.magic + 5)
                                potential_heal_targets.append((ally, heal_amount))
                
                # 潜在的な回復対象があれば行動を追加
                for target, heal_amount in potential_heal_targets:
                    # 優先度は回復量と対象ユニットの重要度で決定
                    priority = heal_amount * 2
                    
                    # 対象が重要なユニット（タンクなど）なら優先度上げ
                    target_role = self.unit_roles.get(target.name, "")
                    if target_role in [AIRole.TANK, AIRole.HEALER]:
                        priority += 20
                    
                    # HPが低いほど優先
                    target_hp_ratio = target.current_hp / target.max_hp
                    priority += int((1 - target_hp_ratio) * 50)
                    
                    actions.append(TacticalAction(
                        action_type='heal',
                        priority=priority,
                        unit=unit,
                        target_position=(pos_x, pos_y),
                        target_unit=target,
                        item=heal_weapon,
                        expected_damage=-heal_amount  # 負の値は回復量
                    ))
        
        # 回復手段がなければ、他のユニットをサポートする行動を生成
        if not actions:
            actions.extend(self._generate_support_actions(unit))
        
        return actions
    
    def _generate_retreat_action(self, unit) -> Optional[TacticalAction]:
        """撤退アクションを生成"""
        game_map = self.game_manager.game_map
        
        # 移動可能範囲
        move_positions = game_map.calculate_movement_range(unit)
        
        best_retreat_pos = None
        lowest_danger = float('inf')
        
        for pos_x, pos_y in move_positions:
            # 危険度を確認
            danger_level = self.danger_map[pos_y][pos_x]
            
            # 最も安全な位置を選択
            if danger_level < lowest_danger:
                lowest_danger = danger_level
                best_retreat_pos = (pos_x, pos_y)
        
        if best_retreat_pos:
            return TacticalAction(
                action_type='move',
                priority=100,  # 撤退は高優先度
                unit=unit,
                target_position=best_retreat_pos,
                expected_risk=lowest_danger
            )
        
        return None
    
    def _generate_support_actions(self, unit) -> List[TacticalAction]:
        """サポート役の行動を生成"""
        actions = []
        game_map = self.game_manager.game_map
        
        # バフを付与できる武器/アイテムをチェック（実際のゲームロジックに合わせて調整）
        buff_items = [weapon for weapon in unit.weapons 
                      if weapon and hasattr(weapon, 'effect_type') and 'buff' in weapon.effect_type]
        
        if buff_items:
            buff_item = buff_items[0]
            unit.equipped_weapon = buff_item
            
            # 移動可能範囲
            move_positions = game_map.calculate_movement_range(unit)
            
            for pos_x, pos_y in move_positions:
                # この位置からバフを付与可能なマスを計算
                buff_range = buff_item.range_max if hasattr(buff_item, 'range_max') else 1
                
                # 同じチームのユニットを探す
                for ally in game_map.units:
                    if ally.team == unit.team and not ally.is_dead() and ally != unit:
                        distance = abs(pos_x - ally.x) + abs(pos_y - ally.y)
                        if distance <= buff_range:
                            # 優先度はユニットの役割などで決定
                            priority = 30
                            
                            # 重要なユニットならより高い優先度
                            ally_role = self.unit_roles.get(ally.name, "")
                            if ally_role in [AIRole.ATTACKER, AIRole.ASSASSIN]:
                                priority += 20
                            
                            actions.append(TacticalAction(
                                action_type='buff',
                                priority=priority,
                                unit=unit,
                                target_position=(pos_x, pos_y),
                                target_unit=ally,
                                item=buff_item
                            ))
        
        # バフアイテムがなければ、安全な位置に移動する行動を生成
        if not actions:
            # 移動可能範囲
            move_positions = game_map.calculate_movement_range(unit)
            
            for pos_x, pos_y in move_positions:
                # 危険度を確認
                danger_level = self.danger_map[pos_y][pos_x]
                
                # 安全な位置ほど優先度高
                safety = 100 - min(100, danger_level)
                
                actions.append(TacticalAction(
                    action_type='move',
                    priority=safety // 10,
                    unit=unit,
                    target_position=(pos_x, pos_y),
                    expected_risk=danger_level
                ))
        
        return actions
    
    def _generate_tank_actions(self, unit) -> List[TacticalAction]:
        """タンク役（壁役）の行動を生成"""
        actions = []
        game_map = self.game_manager.game_map
        
        # 移動可能範囲
        move_positions = game_map.calculate_movement_range(unit)
        
        # プレイヤーユニットを守るための位置を探す
        player_units = [u for u in game_map.units if u.team == 0 and not u.is_dead()]
        ally_units = [u for u in game_map.units if u.team == 1 and not u.is_dead() and u != unit]
        
        for pos_x, pos_y in move_positions:
            # この位置から攻撃可能なユニットを探す
            attack_positions = []
            if unit.equipped_weapon:
                attack_positions = game_map.calculate_attack_range(unit, (pos_x, pos_y))
            
            # 攻撃可能なプレイヤーユニット
            attackable_enemies = []
            for attack_x, attack_y in attack_positions:
                enemy = game_map.get_unit_at(attack_x, attack_y)
                if enemy and enemy.team == 0:
                    attackable_enemies.append(enemy)
            
            # 防御位置の評価
            defense_score = 0
            
            # 他の味方ユニットを守れる位置
            for ally in ally_units:
                if ally.current_hp / ally.max_hp < 0.5:  # HPが半分以下の仲間を優先
                    distance = abs(pos_x - ally.x) + abs(pos_y - ally.y)
                    if distance <= 2:  # 近くにいる仲間
                        # 仲間と敵の間に立つ位置なら良い
                        for enemy in player_units:
                            enemy_to_ally = abs(enemy.x - ally.x) + abs(enemy.y - ally.y)
                            enemy_to_pos = abs(enemy.x - pos_x) + abs(enemy.y - pos_y)
                            if enemy_to_pos < enemy_to_ally:
                                defense_score += 30
            
            # 地形の防御性能も考慮
            terrain = game_map.tiles[pos_y][pos_x].terrain_type
            if terrain == TerrainType.FOREST:
                defense_score += 15
            elif terrain == TerrainType.MOUNTAIN:
                defense_score += 20
            
            # 攻撃可能な敵がいれば攻撃行動を追加
            for enemy in attackable_enemies:
                expected_damage = self._calculate_expected_damage(unit, enemy)
                counter_damage = self._calculate_expected_damage(enemy, unit, is_counter=True)
                
                # タンクは自身の被ダメージを気にしない
                priority = defense_score + expected_damage - counter_damage / 3
                
                actions.append(TacticalAction(
                    action_type='attack',
                    priority=int(priority),
                    unit=unit,
                    target_position=(pos_x, pos_y),
                    target_unit=enemy,
                    expected_damage=expected_damage,
                    expected_risk=counter_damage
                ))
            
            # 攻撃できなくても守備位置として評価
            if not attackable_enemies and defense_score > 0:
                actions.append(TacticalAction(
                    action_type='move',
                    priority=defense_score // 5,
                    unit=unit,
                    target_position=(pos_x, pos_y),
                    expected_risk=self.danger_map[pos_y][pos_x]
                ))
        
        return actions
    
    def _generate_assassin_actions(self, unit) -> List[TacticalAction]:
        """暗殺者（高機動・高火力）の行動を生成"""
        actions = []
        game_map = self.game_manager.game_map
        
        # 移動可能範囲
        move_positions = game_map.calculate_movement_range(unit)
        
        for pos_x, pos_y in move_positions:
            # この位置から攻撃可能なユニットを探す
            attack_positions = []
            if unit.equipped_weapon:
                attack_positions = game_map.calculate_attack_range(unit, (pos_x, pos_y))
            
            # 攻撃可能なプレイヤーユニット
            attackable_enemies = []
            for attack_x, attack_y in attack_positions:
                enemy = game_map.get_unit_at(attack_x, attack_y)
                if enemy and enemy.team == 0:
                    attackable_enemies.append(enemy)
            
            for enemy in attackable_enemies:
                expected_damage = self._calculate_expected_damage(unit, enemy)
                counter_damage = self._calculate_expected_damage(enemy, unit, is_counter=True)
                
                # 敵を倒せるかどうか
                can_kill = expected_damage >= enemy.current_hp
                
                # 反撃で自分が死なないか
                risk_of_death = counter_damage >= unit.current_hp
                
                # 優先度計算
                priority = expected_damage * 2
                
                # 敵を倒せるなら大幅に優先度上昇
                if can_kill:
                    priority += 100
                
                # 反撃で死ぬリスクが高いなら優先度下げる
                if risk_of_death:
                    priority -= 150
                
                # 敵が回復役なら優先
                if hasattr(enemy, 'unit_class') and enemy.unit_class.lower() in ['healer', 'priest', 'cleric', '僧侶', '神官']:
                    priority += 50
                
                # 敵が魔法使いで自分の耐性が低いなら優先度下げる
                if (hasattr(enemy, 'unit_class') and enemy.unit_class.lower() in ['mage', 'sage', 'wizard', '魔道士']):
                    if unit.resistance < 5:
                        priority -= 40
                
                actions.append(TacticalAction(
                    action_type='attack',
                    priority=priority,
                    unit=unit,
                    target_position=(pos_x, pos_y),
                    target_unit=enemy,
                    expected_damage=expected_damage,
                    expected_risk=counter_damage
                ))
            
            # 攻撃できなくても、次ターンの位置取りとして評価
            if not attackable_enemies:
                # 危険度確認
                danger_level = self.danger_map[pos_y][pos_x]
                
                # プレイヤーユニットへの接近度
                closest_distance = float('inf')
                for enemy in game_map.units:
                    if enemy.team == 0 and not enemy.is_dead():
                        distance = abs(pos_x - enemy.x) + abs(pos_y - enemy.y)
                        if distance < closest_distance:
                            closest_distance = distance
                
                # 危険度が低く、敵に近い位置を優先
                if danger_level < 10 and closest_distance <= 5:
                    priority = 20 - closest_distance * 2
                    actions.append(TacticalAction(
                        action_type='move',
                        priority=int(priority),
                        unit=unit,
                        target_position=(pos_x, pos_y),
                        expected_risk=danger_level
                    ))
        
        return actions
    
    def _generate_defender_actions(self, unit) -> List[TacticalAction]:
        """防御役の行動を生成"""
        actions = []
        game_map = self.game_manager.game_map
        
        # 移動可能範囲
        move_positions = game_map.calculate_movement_range(unit)
        
        for pos_x, pos_y in move_positions:
            # この位置から攻撃可能なユニットを探す
            attack_positions = []
            if unit.equipped_weapon:
                attack_positions = game_map.calculate_attack_range(unit, (pos_x, pos_y))
            
            # 攻撃可能なプレイヤーユニット
            attackable_enemies = []
            for attack_x, attack_y in attack_positions:
                enemy = game_map.get_unit_at(attack_x, attack_y)
                if enemy and enemy.team == 0:
                    attackable_enemies.append(enemy)
            
            # 防御者は自軍の重要ユニットを守る
            defense_score = 0
            for ally in game_map.units:
                if ally.team == 1 and not ally.is_dead() and ally != unit:
                    ally_role = self.unit_roles.get(ally.name, "")
                    
                    # 回復役や重要ユニットを守る
                    if ally_role in [AIRole.HEALER, AIRole.SUPPORT]:
                        distance = abs(pos_x - ally.x) + abs(pos_y - ally.y)
                        if distance <= 2:
                            defense_score += 30
            
            # 攻撃行動の生成
            for enemy in attackable_enemies:
                expected_damage = self._calculate_expected_damage(unit, enemy)
                counter_damage = self._calculate_expected_damage(enemy, unit, is_counter=True)
                
                # 攻撃優先度計算（防御者は反撃ダメージを重視）
                damage_ratio = expected_damage / (counter_damage + 1)  # ゼロ除算回避
                priority = int(expected_damage + defense_score * 2 + damage_ratio * 10)
                
                actions.append(TacticalAction(
                    action_type='attack',
                    priority=priority,
                    unit=unit,
                    target_position=(pos_x, pos_y),
                    target_unit=enemy,
                    expected_damage=expected_damage,
                    expected_risk=counter_damage
                ))
            
            # 防御位置としての評価
            if defense_score > 0:
                # 危険度確認
                danger_level = self.danger_map[pos_y][pos_x]
                
                actions.append(TacticalAction(
                    action_type='move',
                    priority=defense_score - danger_level // 5,
                    unit=unit,
                    target_position=(pos_x, pos_y),
                    expected_risk=danger_level
                ))
        
        return actions
    
    def _generate_attacker_actions(self, unit) -> List[TacticalAction]:
        """攻撃役の行動を生成"""
        actions = []
        game_map = self.game_manager.game_map
        
        # 移動可能範囲
        move_positions = game_map.calculate_movement_range(unit)
        
        for pos_x, pos_y in move_positions:
            # この位置から攻撃可能なユニットを探す
            attack_positions = []
            if unit.equipped_weapon:
                attack_positions = game_map.calculate_attack_range(unit, (pos_x, pos_y))
            
            # 攻撃可能なプレイヤーユニット
            attackable_enemies = []
            for attack_x, attack_y in attack_positions:
                enemy = game_map.get_unit_at(attack_x, attack_y)
                if enemy and enemy.team == 0:
                    attackable_enemies.append(enemy)
            
            for enemy in attackable_enemies:
                expected_damage = self._calculate_expected_damage(unit, enemy)
                counter_damage = self._calculate_expected_damage(enemy, unit, is_counter=True)
                
                # 敵を倒せるかどうか
                can_kill = expected_damage >= enemy.current_hp
                
                # 反撃で自分が死なないか
                risk_of_death = counter_damage >= unit.current_hp
                
                # 攻撃者の優先度計算
                priority = expected_damage * 2 - counter_damage
                
                # 敵を倒せるなら大幅に優先度上昇
                if can_kill:
                    priority += 80
                
                # 反撃で死ぬリスクが高いなら優先度下げる
                if risk_of_death:
                    priority -= 100
                
                actions.append(TacticalAction(
                    action_type='attack',
                    priority=int(priority),
                    unit=unit,
                    target_position=(pos_x, pos_y),
                    target_unit=enemy,
                    expected_damage=expected_damage,
                    expected_risk=counter_damage
                ))
            
            # 攻撃できなくても、敵への接近を評価
            if not attackable_enemies:
                # 敵への接近評価
                closest_distance = float('inf')
                for enemy in game_map.units:
                    if enemy.team == 0 and not enemy.is_dead():
                        distance = abs(pos_x - enemy.x) + abs(pos_y - enemy.y)
                        if distance < closest_distance:
                            closest_distance = distance
                
                # 危険度確認
                danger_level = self.danger_map[pos_y][pos_x]
                
                # 敵に接近するが危険すぎない位置を選択
                if closest_distance < 6 and danger_level < 20:
                    priority = 15 - closest_distance
                    actions.append(TacticalAction(
                        action_type='move',
                        priority=int(priority),
                        unit=unit,
                        target_position=(pos_x, pos_y),
                        expected_risk=danger_level
                    ))
        
        return actions
    
    def _calculate_expected_damage(self, attacker, defender, is_counter=False) -> int:
        """予想される与ダメージを計算"""
        if not attacker.equipped_weapon:
            return 0
        
        # 実際のダメージ計算はゲームシステムを使用
        if hasattr(self.game_manager, 'combat_system'):
            damage = self.game_manager.combat_system.calculate_damage(
                attacker, defender, self.game_manager.game_map
            )
            hit_chance = self.game_manager.combat_system.calculate_hit_chance(
                attacker, defender, self.game_manager.game_map
            )
            crit_chance = self.game_manager.combat_system.calculate_crit_chance(
                attacker, defender
            )
        else:
            # 簡易的なダメージ計算（実際のゲームロジックに合わせて調整）
            attack_power = attacker.get_attack_power()
            is_magic = attacker.equipped_weapon and hasattr(attacker.equipped_weapon, 'weapon_type') and \
                       attacker.equipped_weapon.weapon_type.name == 'MAGIC'
            
            defense_stat = defender.resistance if is_magic else defender.defense
            damage = max(0, attack_power - defense_stat)
            
            # 命中率・必殺率（簡易計算）
            hit_chance = min(100, max(0, attacker.get_hit_rate() - defender.get_avoid()))
            crit_chance = max(0, attacker.get_critical_rate() - defender.luck)
        
        # 期待値として、命中率とクリティカル率を考慮
        normal_damage = damage * (hit_chance / 100) * (1 - crit_chance / 100)
        crit_damage = damage * 3 * (hit_chance / 100) * (crit_chance / 100)
        
        expected_damage = int(normal_damage + crit_damage)
        
        # 反撃の場合、命中率などに補正をかける
        if is_counter:
            # 反撃不可能な場合
            if not defender.equipped_weapon:
                return 0
                
            # 射程外なら反撃不可
            range_check = False
            if hasattr(defender.equipped_weapon, 'range_min') and hasattr(defender.equipped_weapon, 'range_max'):
                distance = abs(attacker.x - defender.x) + abs(attacker.y - defender.y)
                range_check = defender.equipped_weapon.range_min <= distance <= defender.equipped_weapon.range_max
            
            if not range_check:
                return 0
        
        return expected_damage
    
    def _execute_action(self, action: TacticalAction) -> bool:
        """AIの行動を実行"""
        if action.action_type == 'attack':
            return self._execute_attack_action(action)
        elif action.action_type == 'move':
            return self._execute_move_action(action)
        elif action.action_type == 'heal':
            return self._execute_heal_action(action)
        elif action.action_type == 'buff':
            return self._execute_buff_action(action)
        elif action.action_type == 'wait':
            return self._execute_wait_action(action)
        else:
            return False
    
    def _execute_attack_action(self, action: TacticalAction) -> bool:
        """攻撃行動を実行"""
        unit = action.unit
        target_pos = action.target_position
        target_unit = action.target_unit
        
        if not unit or not target_pos or not target_unit:
            return False
        
        # ユニットを移動
        self.game_manager.game_map.move_unit(unit, target_pos[0], target_pos[1])
        unit.has_moved = True
        
        # 攻撃実行
        combat_results = self.game_manager.combat_system.perform_combat(
            unit, target_unit, self.game_manager.game_map, self.game_manager.support_system
        )
        unit.has_attacked = True
        
        return True
    
    def _execute_move_action(self, action: TacticalAction) -> bool:
        """移動行動を実行"""
        unit = action.unit
        target_pos = action.target_position
        
        if not unit or not target_pos:
            return False
        
        # ユニットを移動
        self.game_manager.game_map.move_unit(unit, target_pos[0], target_pos[1])
        unit.has_moved = True
        unit.has_attacked = True  # 他の行動を取らない
        
        return True
    
    def _execute_heal_action(self, action: TacticalAction) -> bool:
        """回復行動を実行"""
        unit = action.unit
        target_pos = action.target_position
        target_unit = action.target_unit
        
        if not unit or not target_pos or not target_unit:
            return False
        
        # ユニットを移動
        self.game_manager.game_map.move_unit(unit, target_pos[0], target_pos[1])
        unit.has_moved = True
        
        # 実際のゲームで回復を実行するロジックをここに
        # 仮の実装：回復量を予測値から取得
        heal_amount = -action.expected_damage  # 負の値は回復量として使用
        target_unit.current_hp = min(target_unit.max_hp, target_unit.current_hp + heal_amount)
        
        unit.has_attacked = True
        
        return True
    
    def _execute_buff_action(self, action: TacticalAction) -> bool:
        """バフ付与行動を実行"""
        unit = action.unit
        target_pos = action.target_position
        
        if not unit or not target_pos:
            return False
        
        # ユニットを移動
        self.game_manager.game_map.move_unit(unit, target_pos[0], target_pos[1])
        unit.has_moved = True
        
        # 実際のゲームでバフを付与するロジックをここに
        # （実際のゲームシステムに合わせて実装）
        
        unit.has_attacked = True
        
        return True
    
    def _execute_wait_action(self, action: TacticalAction) -> bool:
        """待機行動を実行"""
        unit = action.unit
        
        if not unit:
            return False
        
        # 現在の位置で待機
        unit.has_moved = True
        unit.has_attacked = True
        
        return True