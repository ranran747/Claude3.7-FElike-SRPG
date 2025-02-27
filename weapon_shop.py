# weapon_shop.py
import pygame
from ui_system import Panel, Label, Button, ScrollPanel

class WeaponShop(Panel):
    def __init__(self, x, y, width, height, game_manager, on_close=None):
        super().__init__(x, y, width, height)
        self.game_manager = game_manager
        self.on_close = on_close
        self.inventory = []  # 販売アイテムリスト
        self.selected_weapon = None
        self.selected_unit = None
        
        # ショップタイトル
        title_label = Label(width // 2, 20, "武器屋", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # 所持金表示
        gold_label = Label(width - 20, 20, f"所持金: {game_manager.player_gold}G", None, 24, (255, 255, 0), None, "right")
        self.add_child(gold_label)
        self.gold_label = gold_label
        
        # 武器リスト（左側）
        weapons_panel = ScrollPanel(20, 70, width // 2 - 30, height - 150, height, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(weapons_panel)
        self.weapons_panel = weapons_panel
        
        # ユニットリスト（右上）
        units_panel = ScrollPanel(width // 2 + 10, 70, width // 2 - 30, height // 2 - 40, height, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(units_panel)
        self.units_panel = units_panel
        
        # 装備詳細（右下）
        details_panel = Panel(width // 2 + 10, height // 2 + 40, width // 2 - 30, height // 2 - 110, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(details_panel)
        self.details_panel = details_panel
        
        # ボタン類
        buy_btn = Button(width // 4 - 50, height - 60, 100, 40, "購入", None, 24,
                        (60, 100, 60), (255, 255, 255), (80, 150, 80),
                        (0, 0, 0), 1, self.buy_weapon)
        self.add_child(buy_btn)
        self.buy_btn = buy_btn
        
        equip_btn = Button(width // 4 * 3 - 50, height - 60, 100, 40, "装備", None, 24,
                          (60, 60, 100), (255, 255, 255), (80, 80, 150),
                          (0, 0, 0), 1, self.equip_weapon)
        self.add_child(equip_btn)
        self.equip_btn = equip_btn
        
        close_btn = Button(width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close_shop)
        self.add_child(close_btn)
        
        # 武器とユニットのリストを更新
        self.update_weapon_list()
        self.update_unit_list()
        
        # ボタンの初期状態
        self.buy_btn.set_active(False)
        self.equip_btn.set_active(False)
    
    def update_weapon_list(self):
        """販売武器リストを更新"""
        self.weapons_panel.clear_children()
        
        # 販売武器のデータ取得（実際はゲームマネージャーから取得）
        self.inventory = self.game_manager.get_shop_weapons()
        
        for i, weapon in enumerate(self.inventory):
            weapon_panel = Panel(10, i * 70 + 10, self.weapons_panel.width - 30, 60, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # 武器名
            weapon_panel.add_child(Label(10, 10, weapon.name, None, 20, (255, 255, 255)))
            
            # 武器性能
            stats_text = f"威力:{weapon.might} 命中:{weapon.hit} 重さ:{weapon.weight}"
            weapon_panel.add_child(Label(10, 35, stats_text, None, 16, (200, 200, 200)))
            
            # 価格
            price_text = f"{weapon.price}G"
            weapon_panel.add_child(Label(weapon_panel.width - 70, 10, price_text, None, 18, (255, 255, 0), None, "right"))
            
            # クリックハンドラを設定
            weapon_index = i
            
            def make_handler(idx):
                return lambda: self.select_weapon(self.inventory[idx])
            
            weapon_panel.handle_event = make_handler(weapon_index)
            
            self.weapons_panel.add_child(weapon_panel)
        
        # コンテンツ高さを更新
        self.weapons_panel.update_content_height()
    
    def update_unit_list(self):
        """ユニットリストを更新"""
        self.units_panel.clear_children()
        
        # プレイヤーユニットの取得
        units = [unit for unit in self.game_manager.game_map.units if unit.team == 0]
        
        for i, unit in enumerate(units):
            unit_panel = Panel(10, i * 60 + 10, self.units_panel.width - 30, 50, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # ユニット名と職業
            unit_panel.add_child(Label(10, 10, f"{unit.name} (Lv.{unit.level} {unit.unit_class})", None, 18, (255, 255, 255)))
            
            # 装備中の武器
            equipped_text = f"装備: {unit.equipped_weapon.name if unit.equipped_weapon else '無し'}"
            unit_panel.add_child(Label(10, 30, equipped_text, None, 16, (200, 200, 200)))
            
            # クリックハンドラを設定
            unit_index = i
            
            def make_handler(idx):
                return lambda: self.select_unit(units[idx])
            
            unit_panel.handle_event = make_handler(unit_index)
            
            self.units_panel.add_child(unit_panel)
        
        # コンテンツ高さを更新
        self.units_panel.update_content_height()
    
    def select_weapon(self, weapon):
        """武器を選択"""
        self.selected_weapon = weapon
        self.update_details()
        
        # 購入ボタンの有効化
        self.buy_btn.set_active(True)
        
        # 装備ボタンの有効化（ユニットと武器の両方が選択されている場合）
        self.equip_btn.set_active(self.selected_unit is not None)
    
    def select_unit(self, unit):
        """ユニットを選択"""
        self.selected_unit = unit
        self.update_details()
        
        # 装備ボタンの有効化（ユニットと武器の両方が選択されている場合）
        self.equip_btn.set_active(self.selected_weapon is not None)
    
    # weapon_shop.py の続き
    def update_details(self):
        """詳細パネルを更新"""
        self.details_panel.clear_children()
        
        if not self.selected_weapon:
            return
        
        # 武器詳細
        self.details_panel.add_child(Label(10, 10, f"名前: {self.selected_weapon.name}", None, 18, (255, 255, 255)))
        self.details_panel.add_child(Label(10, 30, f"種類: {self.selected_weapon.weapon_type.name}", None, 16, (200, 200, 200)))
        self.details_panel.add_child(Label(10, 50, f"威力: {self.selected_weapon.might}", None, 16, (200, 200, 200)))
        self.details_panel.add_child(Label(10, 70, f"命中: {self.selected_weapon.hit}", None, 16, (200, 200, 200)))
        self.details_panel.add_child(Label(10, 90, f"必殺: {self.selected_weapon.crit}", None, 16, (200, 200, 200)))
        self.details_panel.add_child(Label(10, 110, f"重さ: {self.selected_weapon.weight}", None, 16, (200, 200, 200)))
        self.details_panel.add_child(Label(10, 130, f"射程: {self.selected_weapon.range_min}-{self.selected_weapon.range_max}", None, 16, (200, 200, 200)))
        self.details_panel.add_child(Label(10, 150, f"価格: {self.selected_weapon.price}G", None, 16, (255, 255, 0)))
        
        # 選択中のユニットとの相性を表示
        if self.selected_unit:
            # 背景枠
            compatibility_panel = Panel(self.details_panel.width // 2, 10, self.details_panel.width // 2 - 20, 160, (60, 60, 70), (0, 0, 0), 1, 200)
            self.details_panel.add_child(compatibility_panel)
            
            # ユニット名
            compatibility_panel.add_child(Label(10, 10, self.selected_unit.name, None, 18, (255, 255, 255)))
            
            # 武器との相性チェック
            can_equip = True  # デフォルトでは装備可能
            
            # レジェンダリー武器の場合は特別なチェック
            if hasattr(self.selected_weapon, 'can_equip'):
                can_equip = self.selected_weapon.can_equip(self.selected_unit)
            
            # 装備可能かどうかを表示
            equip_text = "装備可能" if can_equip else "装備不可"
            equip_color = (100, 255, 100) if can_equip else (255, 100, 100)
            compatibility_panel.add_child(Label(10, 30, equip_text, None, 16, equip_color))
            
            # 現在の装備と比較
            if self.selected_unit.equipped_weapon:
                current = self.selected_unit.equipped_weapon
                compatibility_panel.add_child(Label(10, 50, "現在装備中:", None, 16, (200, 200, 200)))
                compatibility_panel.add_child(Label(10, 70, current.name, None, 16, (180, 180, 230)))
                
                # 簡易ステータス比較
                might_diff = self.selected_weapon.might - current.might
                hit_diff = self.selected_weapon.hit - current.hit
                crit_diff = self.selected_weapon.crit - current.crit
                
                might_color = (100, 255, 100) if might_diff > 0 else (255, 100, 100) if might_diff < 0 else (200, 200, 200)
                hit_color = (100, 255, 100) if hit_diff > 0 else (255, 100, 100) if hit_diff < 0 else (200, 200, 200)
                crit_color = (100, 255, 100) if crit_diff > 0 else (255, 100, 100) if crit_diff < 0 else (200, 200, 200)
                
                compatibility_panel.add_child(Label(10, 90, f"威力: {might_diff:+d}", None, 16, might_color))
                compatibility_panel.add_child(Label(10, 110, f"命中: {hit_diff:+d}", None, 16, hit_color))
                compatibility_panel.add_child(Label(10, 130, f"必殺: {crit_diff:+d}", None, 16, crit_color))
    
    def buy_weapon(self):
        """武器を購入"""
        if not self.selected_weapon:
            return
        
        # 所持金チェック
        if self.game_manager.player_gold < self.selected_weapon.price:
            # お金が足りないメッセージ
            return
        
        # 購入処理
        self.game_manager.player_gold -= self.selected_weapon.price
        self.game_manager.add_item_to_inventory(self.selected_weapon)
        
        # 所持金表示の更新
        self.gold_label.set_text(f"所持金: {self.game_manager.player_gold}G")
        
        # 即座に装備するかどうかの確認（未実装）
    
    def equip_weapon(self):
        """武器を装備"""
        if not self.selected_weapon or not self.selected_unit:
            return
        
        # インベントリに武器があるか確認
        if self.selected_weapon not in self.game_manager.inventory:
            # 購入が必要なメッセージ
            return
        
        # 装備処理
        self.game_manager.equip_weapon(self.selected_unit, self.selected_weapon)
        
        # ユニットリストを更新
        self.update_unit_list()
    
    def close_shop(self):
        """ショップを閉じる"""
        if self.on_close:
            self.on_close()