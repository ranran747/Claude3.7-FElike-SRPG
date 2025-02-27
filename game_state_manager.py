# game_state_manager.py
from enum import Enum

class GameState(Enum):
    TITLE = 0
    TOWN = 1
    SCENARIO_SELECT = 2
    LEVEL_SYNC = 3
    PRE_MAP_DIALOGUE = 4
    MAP = 5
    POST_MAP_DIALOGUE = 6
    LEVEL_UP_PROCESSING = 7
    SAVE = 8
    
class GameStateManager:
    def __init__(self):
        self.current_state = GameState.TITLE
        self.previous_state = None
        self.game_data = {}  # ゲーム進行に関するデータ
        self.town_data = {}  # 街の情報
        self.scenario_data = {}  # シナリオデータ
        self.current_scenario = None
        self.current_map = None
        self.item_storage = []  # 輸送隊のアイテムリスト
        
    def change_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state
        
    def load_game_data(self, save_file):
        # セーブデータのロード処理
        pass
        
    def save_game_data(self, save_file):
        # セーブ処理
        pass
        
    def initialize_new_game(self):
        # 新規ゲーム開始時の初期化
        pass

    def rescue_unit(self, rescuer, target):
        """ユニットの救出処理"""
        if not rescuer.can_rescue(target):
            return False
        
        # 救出処理
        rescuer.rescue(target)
        
        # マップ上から被救出ユニットを隠す
        self.game_map.hide_unit(target)
        
        return True
    
    def drop_unit(self, rescuer, x, y):
        """救出したユニットを下ろす処理"""
        if not rescuer.rescuing:
            return False
        
        target = rescuer.rescuing
        
        # 敵ユニットを下ろす場合（捕獲後）
        if target.team != rescuer.team:
            # インベントリからアイテムを取得（必要に応じて）
            # 敵ユニットをマップから消去
            rescuer.rescuing = None
            target.rescued_by = None
            # ステータス修正を元に戻す
            rescuer.remove_rescue_penalty()
            return True
        
        # 味方ユニットを下ろす場合
        return rescuer.drop(x, y, self.game_map)
    
    def capture_unit_in_battle(self, attacker, defender):
        """戦闘による捕獲処理"""
        # 戦闘後に敵のHPが0になった場合
        if defender.current_hp <= 0 and attacker.can_capture(defender):
            # 捕獲処理
            defender.current_hp = 1  # 捕獲したユニットのHPを1に回復
            attacker.rescuing = defender
            defender.rescued_by = attacker
            
            # マップ上から被捕獲ユニットを隠す
            self.game_map.hide_unit(defender)
            
            # ステータス修正を適用
            attacker.apply_rescue_penalty()
            
            return True
        
        return False
    
    def capture_unit_without_battle(self, captor, target):
        """戦闘なしでの捕獲（投降）処理"""
        if not captor.can_capture_without_battle(target):
            return False
        
        # 捕獲処理
        captor.rescuing = target
        target.rescued_by = captor
        
        # マップ上から被捕獲ユニットを隠す
        self.game_map.hide_unit(target)
        
        # ステータス修正を適用
        captor.apply_rescue_penalty()
        
        return True
    
    def exchange_items(self, unit1, unit2):
        """ユニット間のアイテム交換処理"""
        # アイテム選択UIの表示などは別途実装
        pass
    
    def send_items_to_storage(self, unit):
        """ユニットのアイテムを全て輸送隊に送る"""
        if not unit.weapons:
            return False
        
        # 装備中の武器を除く全てのアイテムを輸送隊に送る
        equipped_weapon = unit.equipped_weapon
        
        for weapon in unit.weapons[:]:  # コピーをループ
            if weapon != equipped_weapon:
                self.item_storage.append(weapon)
                unit.weapons.remove(weapon)
        
        return True
    
    def access_item_storage(self, unit):
        """輸送隊のアイテムアクセス処理"""
        if not unit.has_item_box_access:
            return False
        
        # アイテムボックスUIの表示などは別途実装
        return True