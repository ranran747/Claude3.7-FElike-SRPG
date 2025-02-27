# town_screen.py
import pygame
import os
from typing import List, Dict, Tuple, Optional, Callable
from ui_system import Panel, Label, Button, ScrollPanel
from font_manager import get_font
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

# 各施設用のクラスをインポート
from adventurer_guild import AdventurerGuild, AdventurerGuildExtended
from church import Church
from weapon_shop import WeaponShop
from save_shop import SaveShop
from tavern import Tavern

class TownScreen(Panel):
    """冒険者の街画面"""
    def __init__(self, x, y, width, height, game_state_manager, on_leave_town=None):
        super().__init__(x, y, width, height)
        self.game_state_manager = game_state_manager
        self.on_leave_town = on_leave_town
        self.current_facility = None
        
        # 背景画像（実際のゲームでは適切な背景画像をロード）
        self.background = self._create_town_background()
        
        # UI設定
        self._setup_ui()
    
    def _create_town_background(self):
        """簡易的な街背景を作成"""
        bg = pygame.Surface((self.width, self.height))
        bg.fill((100, 150, 100))  # 草原色の背景
        
        # 簡易的な建物を描画
        buildings = [
            ((self.width // 4, self.height // 3), (200, 150), (150, 100, 50)),  # 冒険者ギルド
            ((self.width // 2, self.height // 4), (180, 120), (200, 180, 160)),  # 教会
            ((self.width * 3 // 4, self.height // 3), (160, 140), (120, 80, 60)),  # 武器屋
            ((self.width // 4, self.height * 2 // 3), (170, 130), (180, 100, 80)),  # 酒場
            ((self.width // 2, self.height * 3 // 4), (150, 110), (100, 100, 150)),  # セーブ屋
        ]
        
        for (x, y), (w, h), color in buildings:
            pygame.draw.rect(bg, color, (x - w // 2, y - h // 2, w, h))
            pygame.draw.rect(bg, (50, 50, 50), (x - w // 2, y - h // 2, w, h), 2)  # 輪郭
            
            # 屋根
            roof_points = [
                (x - w // 2, y - h // 2),
                (x, y - h // 2 - 40),
                (x + w // 2, y - h // 2)
            ]
            pygame.draw.polygon(bg, (180, 30, 30), roof_points)
            pygame.draw.polygon(bg, (50, 50, 50), roof_points, 2)  # 輪郭
        
        # 道路
        pygame.draw.line(bg, (150, 150, 150), (self.width // 2, 0), (self.width // 2, self.height), 30)
        pygame.draw.line(bg, (150, 150, 150), (0, self.height // 2), (self.width, self.height // 2), 30)
        
        return bg
    
    def _setup_ui(self):
        """UI要素をセットアップ"""
        # タイトル
        title_label = Label(self.width // 2, 30, "冒険者の街", None, 36, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # 所持金表示
        gold_label = Label(self.width - 20, 20, f"所持金: {self.game_state_manager.player_gold}G", None, 24, (255, 255, 0), None, "right")
        self.add_child(gold_label)
        self.gold_label = gold_label
        
        # 施設ボタン
        button_width = 180
        button_height = 60
        button_margin = 20
        
        facilities = [
            ("冒険者ギルド", self.show_adventurer_guild),
            ("教会", self.show_church),
            ("武器屋", self.show_weapon_shop),
            ("酒場", self.show_tavern),
            ("セーブ屋", self.show_save_shop),
        ]
        
        for i, (name, callback) in enumerate(facilities):
            x = self.width - button_width - button_margin
            y = 80 + i * (button_height + button_margin)
            
            facility_btn = Button(x, y, button_width, button_height, name, None, 24,
                              (60, 60, 100), (255, 255, 255), (80, 80, 150),
                              (0, 0, 0), 1, callback)
            self.add_child(facility_btn)
        
        # 街を出るボタン
        leave_btn = Button(self.width - button_width - button_margin, self.height - button_height - button_margin,
                         button_width, button_height, "街を出る", None, 24,
                         (100, 60, 60), (255, 255, 255), (150, 80, 80),
                         (0, 0, 0), 1, self.leave_town)
        self.add_child(leave_btn)
    
    def render(self, screen):
        """描画処理をオーバーライド"""
        # 背景表示
        screen.blit(self.background, (self.x, self.y))
        
        # UI要素描画
        for child in self.children:
            if child.visible:
                child.render(screen)
        
        # 現在表示している施設
        if self.current_facility:
            self.current_facility.render(screen)
    
    def update(self):
        """状態更新"""
        super().update()
        
        # 所持金表示の更新
        self.gold_label.set_text(f"所持金: {self.game_state_manager.player_gold}G")
        
        # 現在表示している施設の更新
        if self.current_facility:
            self.current_facility.update()
    
    def show_adventurer_guild(self):
        """冒険者ギルドを表示"""
        if self.current_facility:
            self.remove_child(self.current_facility)
        
        # 拡張版の冒険者ギルドを使用
        self.current_facility = AdventurerGuildExtended(
            50, 50, self.width - 100, self.height - 100,
            self.game_state_manager, 
            on_close=lambda: self.close_facility()
        )
        
        self.add_child(self.current_facility)
    
    def show_church(self):
        """教会を表示"""
        if self.current_facility:
            self.remove_child(self.current_facility)
        
        self.current_facility = Church(
            50, 50, self.width - 100, self.height - 100,
            self.game_state_manager, 
            on_close=lambda: self.close_facility()
        )
        
        self.add_child(self.current_facility)
    
    def show_weapon_shop(self):
        """武器屋を表示"""
        if self.current_facility:
            self.remove_child(self.current_facility)
        
        self.current_facility = WeaponShop(
            50, 50, self.width - 100, self.height - 100,
            self.game_state_manager, 
            on_close=lambda: self.close_facility()
        )
        
        self.add_child(self.current_facility)
    
    def show_tavern(self):
        """酒場を表示"""
        if self.current_facility:
            self.remove_child(self.current_facility)
        
        self.current_facility = Tavern(
            50, 50, self.width - 100, self.height - 100,
            self.game_state_manager, 
            on_close=lambda: self.close_facility()
        )
        
        self.add_child(self.current_facility)
    
    def show_save_shop(self):
        """セーブ屋を表示"""
        if self.current_facility:
            self.remove_child(self.current_facility)
        
        save_system = self.game_state_manager.save_system
        if not save_system:
            # ゲームマネージャーにセーブシステムがない場合は作成
            from save_system import SaveSystem
            save_system = SaveSystem()
            self.game_state_manager.save_system = save_system
        
        self.current_facility = SaveShop(
            50, 50, self.width - 100, self.height - 100,
            self.game_state_manager, 
            save_system,
            on_close=lambda: self.close_facility()
        )
        
        self.add_child(self.current_facility)
    
    def close_facility(self):
        """施設を閉じる"""
        if self.current_facility:
            self.remove_child(self.current_facility)
            self.current_facility = None
    
    def leave_town(self):
        """街を出る"""
        if self.on_leave_town:
            self.on_leave_town()
    
    def handle_event(self, event):
        """イベント処理"""
        # 現在表示している施設があればそちらを優先
        if self.current_facility and self.current_facility.handle_event(event):
            return True
        
        # 施設がないか処理されなかった場合は親クラスの処理
        return super().handle_event(event)