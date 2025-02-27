# item_storage_ui.py
import pygame
from ui_system import Panel, Label, Button, ScrollPanel

class ItemStorageWindow(Panel):
    def __init__(self, x, y, width, height, game_manager, unit=None, on_close=None):
        super().__init__(x, y, width, height)
        self.game_manager = game_manager
        self.unit = unit
        self.on_close = on_close
        
        # タイトル
        title_label = Label(width // 2, 20, "輸送隊", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # 閉じるボタン
        close_btn = Button(width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close_storage)
        self.add_child(close_btn)
        
        # 左側：ユニットのアイテム
        unit_item_label = Label(width // 4, 50, "ユニットのアイテム", None, 24, (255, 255, 255), None, "center")
        self.add_child(unit_item_label)
        
        unit_items_panel = ScrollPanel(10, 80, width // 2 - 20, height - 120,
                                      height, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(unit_items_panel)
        self.unit_items_panel = unit_items_panel
        
        # 右側：輸送隊のアイテム
        storage_label = Label(width * 3 // 4, 50, "輸送隊のアイテム", None, 24, (255, 255, 255), None, "center")
        self.add_child(storage_label)
        
        storage_items_panel = ScrollPanel(width // 2 + 10, 80, width // 2 - 20, height - 120,
                                        height, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(storage_items_panel)
        self.storage_items_panel = storage_items_panel
        
        # 転送ボタン
        transfer_to_storage_btn = Button(width // 2 - 15, height // 2 - 40, 30, 30, "→", None, 20,
                                        (60, 60, 100), (255, 255, 255), (80, 80, 150),
                                        (0, 0, 0), 1, self.transfer_to_storage)
        self.add_child(transfer_to_storage_btn)
        
        transfer_to_unit_btn = Button(width // 2 - 15, height // 2 + 10, 30, 30, "←", None, 20,
                                     (60, 60, 100), (255, 255, 255), (80, 80, 150),
                                     (0, 0, 0), 1, self.transfer_to_unit)
        self.add_child(transfer_to_unit_btn)
        
        # 選択状態
        self.selected_unit_item = None
        self.selected_storage_item = None
        
        # アイテムリストの更新
        self.update_item_lists()
    
    def update_item_lists(self):
        """アイテムリストを更新"""
        self.update_unit_items()
        self.update_storage_items()
    
    def update_unit_items(self):
        """ユニットのアイテムリストを更新"""
        self.unit_items_panel.clear_children()
        
        if not self.unit:
            self.unit_items_panel.add_child(Label(
                self.unit_items_panel.width // 2, 30,
                "ユニットが選択されていません",
                None, 18, (200, 200, 200), None, "center"
            ))
            return
        
        if not self.unit.weapons:
            self.unit_items_panel.add_child(Label(
                self.unit_items_panel.width // 2, 30,
                "アイテムがありません",
                None, 18, (200, 200, 200), None, "center"
            ))
            return
        
        for i, item in enumerate(self.unit.weapons):
            item_panel = Panel(10, i * 60 + 10, self.unit_items_panel.width - 20, 50, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # アイテム名
            equipped_text = " (装備中)" if item == self.unit.equipped_weapon else ""
            item_panel.add_child(Label(10, 10, f"{item.name}{equipped_text}", None, 18, (255, 255, 255)))
            
            # アイテム情報
            if hasattr(item, 'durability'):
                item_panel.add_child(Label(10, 30, f"耐久: {item.durability}/{item.max_durability}", None, 14, (200, 200, 200)))
            
            # クリックハンドラ
            item_index = i
            
            def make_handler(idx):
                return lambda: self.select_unit_item(self.unit.weapons[idx])
            
            item_panel.handle_event = make_handler(item_index)
            
            # 選択中のアイテムは色を変える
            if item == self.selected_unit_item:
                item_panel.color = (80, 80, 120)
            
            self.unit_items_panel.add_child(item_panel)
        
        self.unit_items_panel.update_content_height()
    
    def update_storage_items(self):
        """輸送隊のアイテムリストを更新"""
        self.storage_items_panel.clear_children()
        
        if not self.game_manager.item_storage:
            self.storage_items_panel.add_child(Label(
                self.storage_items_panel.width // 2, 30,
                "アイテムがありません",
                None, 18, (200, 200, 200), None, "center"
            ))
            return
        
        for i, item in enumerate(self.game_manager.item_storage):
            item_panel = Panel(10, i * 60 + 10, self.storage_items_panel.width - 20, 50, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # アイテム名
            item_panel.add_child(Label(10, 10, item.name, None, 18, (255, 255, 255)))
            
            # アイテム情報
            if hasattr(item, 'durability'):
                item_panel.add_child(Label(10, 30, f"耐久: {item.durability}/{item.max_durability}", None, 14, (200, 200, 200)))
            
            # クリックハンドラ
            item_index = i
            
            def make_handler(idx):
                return lambda: self.select_storage_item(self.game_manager.item_storage[idx])
            
            item_panel.handle_event = make_handler(item_index)
            
            # 選択中のアイテムは色を変える
            if item == self.selected_storage_item:
                item_panel.color = (80, 80, 120)
            
            self.storage_items_panel.add_child(item_panel)
        
        self.storage_items_panel.update_content_height()
    
    def select_unit_item(self, item):
        """ユニットのアイテムを選択"""
        self.selected_unit_item = item
        self.selected_storage_item = None
        self.update_item_lists()
    
    def select_storage_item(self, item):
        """輸送隊のアイテムを選択"""
        self.selected_storage_item = item
        self.selected_unit_item = None
        self.update_item_lists()
    
    def transfer_to_storage(self):
        """選択中のアイテムをユニットから輸送隊に移動"""
        if not self.selected_unit_item or not self.unit:
            return
        
        # 装備中のアイテムは移動できない
        if self.selected_unit_item == self.unit.equipped_weapon:
            # 警告メッセージ（未実装）
            return
        
        # アイテムの移動
        self.game_manager.item_storage.append(self.selected_unit_item)
        self.unit.weapons.remove(self.selected_unit_item)
        
        # 選択状態をリセット
        self.selected_unit_item = None
        
        # アイテムリストの更新
        self.update_item_lists()
    
    def transfer_to_unit(self):
        """選択中のアイテムを輸送隊からユニットに移動"""
        if not self.selected_storage_item or not self.unit:
            return
        
        # ユニットのアイテム所持数上限チェック（例：5個まで）
        if len(self.unit.weapons) >= 5:
            # 警告メッセージ（未実装）
            return
        
        # アイテムの移動
        self.unit.weapons.append(self.selected_storage_item)
        self.game_manager.item_storage.remove(self.selected_storage_item)
        
        # 選択状態をリセット
        self.selected_storage_item = None
        
        # アイテムリストの更新
        self.update_item_lists()
    
    def close_storage(self):
        """輸送隊画面を閉じる"""
        if self.on_close:
            self.on_close()