# level_up_window.py
import pygame
import random
from typing import Dict, List, Tuple
from ui_system import Panel, Label, Button
from constants import COLOR_BLACK, COLOR_WHITE, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW

class LevelUpWindow(Panel):
    """レベルアップウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 unit=None, stat_gains: Dict[str, int] = None,
                 on_close=None,
                 color: Tuple[int, int, int] = (40, 40, 40),
                 border_color: Tuple[int, int, int] = COLOR_YELLOW,
                 border_width: int = 2,
                 alpha: int = 230):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.unit = unit
        self.stat_gains = stat_gains or {}
        self.on_close = on_close
        
        # フォント
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # アニメーション用変数
        self.animation_active = True
        self.animation_timer = 0
        self.animation_speed = 5  # フレーム数
        self.current_stat_index = -1
        self.stats_to_show = []
        
        # 表示する順番でステータスを配置
        self.stat_order = [
            ("hp", "HP"),
            ("strength", "力"),
            ("magic", "魔力"),
            ("skill", "技"),
            ("speed", "速さ"),
            ("luck", "幸運"),
            ("defense", "守備"),
            ("resistance", "魔防")
        ]
        
        # アニメーションするステータスの順番を設定
        self.stats_to_show = []
        for stat_key, _ in self.stat_order:
            if stat_key in self.stat_gains and self.stat_gains[stat_key] > 0:
                self.stats_to_show.append(stat_key)
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        if not self.unit:
            return
        
        # タイトル
        title_label = Label(self.width // 2, 20, "レベルアップ!", self.title_font, 32, COLOR_YELLOW, None, "center")
        self.add_child(title_label)
        
        # ユニット名と新しいレベル
        name_label = Label(self.width // 2, 55, f"{self.unit.name} Lv {self.unit.level}", self.font, 24, COLOR_WHITE, None, "center")
        self.add_child(name_label)
        
        # ステータス表示用のラベルを準備
        self.stat_labels = {}
        self.value_labels = {}
        self.gain_labels = {}
        
        y_offset = 90
        for i, (stat_key, stat_name) in enumerate(self.stat_order):
            # ステータス名
            stat_label = Label(30, y_offset + i * 30, stat_name, self.font, 24, COLOR_WHITE)
            self.add_child(stat_label)
            self.stat_labels[stat_key] = stat_label
            
            # 現在の値 (初期表示は全部？に)
            original_value = getattr(self.unit, stat_key) - self.stat_gains.get(stat_key, 0)
            value_label = Label(120, y_offset + i * 30, str(original_value), self.font, 24, COLOR_WHITE)
            self.add_child(value_label)
            self.value_labels[stat_key] = value_label
            
            # 上昇値（+X）（初期表示は空白）
            gain = self.stat_gains.get(stat_key, 0)
            gain_text = f"+{gain}" if gain > 0 else ""
            gain_color = COLOR_GREEN if gain > 0 else COLOR_WHITE
            gain_label = Label(170, y_offset + i * 30, gain_text, self.font, 24, gain_color)
            gain_label.visible = False  # アニメーション用に初期非表示
            self.add_child(gain_label)
            self.gain_labels[stat_key] = gain_label
        
        # 閉じるボタン（アニメーション終了後に表示）
        close_button = Button(self.width // 2 - 50, self.height - 45, 100, 30, "閉じる",
                             self.font, 24, (80, 80, 80), COLOR_WHITE, (150, 150, 150),
                             COLOR_BLACK, 1, self.close)
        close_button.visible = False
        self.add_child(close_button)
        self.close_button = close_button
    
    def update(self):
        """アニメーション更新"""
        super().update()
        
        if not self.animation_active:
            return
        
        self.animation_timer += 1
        
        # 次のステータスを表示するタイミング
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_stat_index += 1
            
            # すべてのステータスを表示し終わったらアニメーション終了
            if self.current_stat_index >= len(self.stats_to_show):
                self.animation_active = False
                self.close_button.visible = True
                return
            
            # 現在のステータスを表示
            current_stat = self.stats_to_show[self.current_stat_index]
            self.gain_labels[current_stat].visible = True
            
            # SE再生など
            self._play_level_up_sound()
    
    def render(self, screen):
        """描画処理（オーバーライド）"""
        super().render(screen)
        
        # アニメーション用の追加演出
        if self.animation_active and self.current_stat_index >= 0 and self.current_stat_index < len(self.stats_to_show):
            current_stat = self.stats_to_show[self.current_stat_index]
            label = self.gain_labels[current_stat]
            
            # 点滅エフェクトなど
            if self.animation_timer % 2 == 0:
                pygame.draw.rect(screen, (255, 255, 150), 
                                (label.x - 5, label.y - 2, label.width + 10, label.height + 4), 2)
    
    def _play_level_up_sound(self):
        """レベルアップ用SE再生（未実装）"""
        # pygame.mixer.Sound("level_up.wav").play()
        pass
    
    def close(self):
        """ウィンドウを閉じる"""
        self.visible = False
        if self.on_close:
            self.on_close()