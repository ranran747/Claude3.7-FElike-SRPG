# town_screen.py
import pygame
from ui_system import Panel, Label, Button, ScrollPanel

class TownScreen(Panel):
    def __init__(self, x, y, width, height, game_manager, on_leave_town=None):
        super().__init__(x, y, width, height)
        self.game_manager = game_manager
        self.on_leave_town = on_leave_town
        
        # 街の名前
        town_label = Label(width // 2, 20, "冒険者の街", None, 30, (255, 255, 200), None, "center")
        self.add_child(town_label)
        
        # 施設ボタン
        facility_y = 80
        facility_spacing = 60
        
        weapon_shop = Button(width // 2 - 100, facility_y, 200, 40, "武器屋", None, 24,
                            (80, 80, 100), (255, 255, 255), (100, 100, 150),
                            (0, 0, 0), 1, self.open_weapon_shop)
        self.add_child(weapon_shop)
        
        item_shop = Button(width // 2 - 100, facility_y + facility_spacing, 200, 40, "アイテム屋", None, 24,
                          (80, 100, 80), (255, 255, 255), (100, 150, 100),
                          (0, 0, 0), 1, self.open_item_shop)
        self.add_child(item_shop)
        
        tavern = Button(width // 2 - 100, facility_y + facility_spacing * 2, 200, 40, "酒場", None, 24,
                       (100, 80, 60), (255, 255, 255), (150, 100, 80),
                       (0, 0, 0), 1, self.open_tavern)
        self.add_child(tavern)
        
        guild = Button(width // 2 - 100, facility_y + facility_spacing * 3, 200, 40, "冒険者ギルド", None, 24,
                      (60, 80, 100), (255, 255, 255), (80, 100, 150),
                      (0, 0, 0), 1, self.open_guild)
        self.add_child(guild)
        
        church = Button(width // 2 - 100, facility_y + facility_spacing * 4, 200, 40, "教会", None, 24,
                       (100, 60, 100), (255, 255, 255), (150, 80, 150),
                       (0, 0, 0), 1, self.open_church)
        self.add_child(church)
        
        save_shop = Button(width // 2 - 100, facility_y + facility_spacing * 5, 200, 40, "セーブ屋", None, 24,
                          (100, 100, 60), (255, 255, 255), (150, 150, 80),
                          (0, 0, 0), 1, self.open_save_shop)
        self.add_child(save_shop)
        
        leave_town = Button(width // 2 - 100, height - 60, 200, 40, "街を出る", None, 24,
                           (150, 60, 60), (255, 255, 255), (200, 80, 80),
                           (0, 0, 0), 1, self.leave_town)
        self.add_child(leave_town)
    
    def open_weapon_shop(self):
        # 武器屋画面を開く処理
        pass
    
    def open_item_shop(self):
        # アイテム屋画面を開く処理
        pass
    
    def open_tavern(self):
        # 酒場画面を開く処理
        pass
    
    def open_guild(self):
        # ギルド画面を開く処理
        pass
    
    def open_church(self):
        # 教会画面を開く処理
        pass
    
    def open_save_shop(self):
        # セーブ屋画面を開く処理
        pass
    
    def leave_town(self):
        if self.on_leave_town:
            self.on_leave_town()