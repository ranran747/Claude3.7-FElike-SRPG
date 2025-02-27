# ui_system.py
import pygame
from typing import List, Dict, Tuple, Callable, Optional
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, COLOR_BLACK, COLOR_WHITE, COLOR_BLUE, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_GRAY
from font_manager import get_font

class UIElement:
    """UIの基本クラス"""
    def __init__(self, x: int, y: int, width: int, height: int, visible: bool = True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = visible
        self.active = True
        self.parent = None
    
    def render(self, screen):
        """画面に描画する"""
        pass
    
    def handle_event(self, event) -> bool:
        """イベントを処理する。処理した場合はTrueを返す"""
        return False
    
    def update(self):
        """状態を更新する"""
        pass
    
    def set_position(self, x: int, y: int):
        """位置を設定する"""
        self.x = x
        self.y = y
    
    def set_size(self, width: int, height: int):
        """サイズを設定する"""
        self.width = width
        self.height = height
    
    def set_visible(self, visible: bool):
        """表示/非表示を設定する"""
        self.visible = visible
    
    def set_active(self, active: bool):
        """アクティブ/非アクティブを設定する"""
        self.active = active
    
    def contains_point(self, x: int, y: int) -> bool:
        """指定された座標がこの要素内にあるかどうかを判定"""
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height


class Panel(UIElement):
    """パネル（コンテナ）クラス"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 color: Tuple[int, int, int] = COLOR_GRAY, 
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 1,
                 alpha: int = 200):
        super().__init__(x, y, width, height)
        self.color = color
        self.border_color = border_color
        self.border_width = border_width
        self.alpha = alpha
        self.children = []
    
    def render(self, screen):
        if not self.visible:
            return
        
        # 半透明のパネルを描画
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((self.color[0], self.color[1], self.color[2], self.alpha))
        screen.blit(s, (self.x, self.y))
        
        # 枠線を描画
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, 
                             (self.x, self.y, self.width, self.height), 
                             self.border_width)
        
        # 子要素を描画
        for child in self.children:
            if child.visible:
                child.render(screen)
    
    def handle_event(self, event) -> bool:
        if not self.visible or not self.active:
            return False
        
        # 子要素にイベントを伝播
        for child in reversed(self.children):  # 描画順と逆順に処理（前面の要素が優先）
            if child.active and child.handle_event(event):
                return True
        
        return False
    
    def update(self):
        if not self.visible or not self.active:
            return
        
        # 子要素を更新
        for child in self.children:
            child.update()
    
    def add_child(self, child):
        """子要素を追加"""
        self.children.append(child)
        child.parent = self
        return child
    
    def remove_child(self, child):
        """子要素を削除"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def clear_children(self):
        """すべての子要素を削除"""
        for child in self.children:
            child.parent = None
        self.children.clear()


class Label(UIElement):
    """テキストラベル"""
    def __init__(self, x: int, y: int, text: str, font=None, font_size: int = 24, 
                 color: Tuple[int, int, int] = COLOR_WHITE, 
                 background_color: Optional[Tuple[int, int, int]] = None,
                 align: str = "left"):  # left, center, right
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font = font if font else get_font(font_size)  # フォントマネージャーを使用
        self.font_size = font_size
        self.color = color
        self.background_color = background_color
        self.align = align
        self._update_size()
    
    def _update_size(self):
        """テキストサイズに基づいてサイズを更新"""
        text_surface = self.font.render(self.text, True, self.color)
        self.width = text_surface.get_width()
        self.height = text_surface.get_height()
    
    def render(self, screen):
        if not self.visible or not self.text:
            return
        
        # テキストをレンダリング
        text_surface = self.font.render(self.text, True, self.color)
        
        # 背景を描画（指定されている場合）
        if self.background_color:
            pygame.draw.rect(screen, self.background_color, 
                             (self.x, self.y, self.width, self.height))
        
        # アライメントに応じて位置を調整
        x_pos = self.x
        if self.align == "center":
            x_pos = self.x - self.width // 2
        elif self.align == "right":
            x_pos = self.x - self.width
        
        # テキストを描画
        screen.blit(text_surface, (x_pos, self.y))
    
    def set_text(self, text: str):
        """テキストを設定し、サイズを更新"""
        self.text = text
        self._update_size()


class Button(UIElement):
    """ボタン"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, font=None, font_size: int = 24,
                 color: Tuple[int, int, int] = COLOR_GRAY,
                 text_color: Tuple[int, int, int] = COLOR_BLACK,
                 hover_color: Tuple[int, int, int] = COLOR_WHITE,
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 1,
                 callback: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font if font else get_font(font_size)  # フォントマネージャーを使用
        self.font_size = font_size
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_width = border_width
        self.callback = callback
        self.hovered = False
        self.pressed = False
    
    def render(self, screen):
        if not self.visible:
            return
        
        # ボタンの背景
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, current_color, (self.x, self.y, self.width, self.height))
        
        # 枠線
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, 
                             (self.x, self.y, self.width, self.height), 
                             self.border_width)
        
        # テキスト
        text_surface = self.font.render(self.text, True, self.text_color)
        text_x = self.x + (self.width - text_surface.get_width()) // 2
        text_y = self.y + (self.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def handle_event(self, event) -> bool:
        if not self.visible or not self.active:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.contains_point(*event.pos)
            return self.hovered
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(*event.pos):
                self.pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.contains_point(*event.pos) and self.callback:
                self.callback()
                return True
        
        return False


class ImageButton(Button):
    """画像ボタン"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 image, hover_image=None,
                 text: str = "", font=None, font_size: int = 24,
                 text_color: Tuple[int, int, int] = COLOR_BLACK,
                 border_color: Optional[Tuple[int, int, int]] = None,
                 border_width: int = 1,
                 callback: Optional[Callable] = None):
        super().__init__(x, y, width, height, text, font, font_size,
                         COLOR_GRAY, text_color, COLOR_GRAY,
                         border_color, border_width, callback)
        self.image = image
        self.hover_image = hover_image or image
    
    def render(self, screen):
        if not self.visible:
            return
        
        # 画像の描画
        current_image = self.hover_image if self.hovered else self.image
        # 画像をボタンのサイズに合わせる
        scaled_image = pygame.transform.scale(current_image, (self.width, self.height))
        screen.blit(scaled_image, (self.x, self.y))
        
        # 枠線
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, 
                             (self.x, self.y, self.width, self.height), 
                             self.border_width)
        
        # テキスト
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_x = self.x + (self.width - text_surface.get_width()) // 2
            text_y = self.y + (self.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))


class ProgressBar(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int,
                 value: float = 1.0, max_value: float = 1.0,
                 color: Tuple[int, int, int] = COLOR_GREEN,
                 background_color: Tuple[int, int, int] = COLOR_GRAY,
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 1,
                 show_text: bool = False,
                 font=None, font_size: int = 18):
        super().__init__(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.background_color = background_color
        self.border_color = border_color
        self.border_width = border_width
        self.show_text = show_text
        self.font = font if font else get_font(font_size)  # フォントマネージャーを使用
        self.font_size = font_size
    
    def render(self, screen):
        if not self.visible:
            return
        
        # 背景
        pygame.draw.rect(screen, self.background_color, 
                         (self.x, self.y, self.width, self.height))
        
        # プログレスバー
        progress_width = int(self.width * (self.value / self.max_value)) if self.max_value > 0 else 0
        if progress_width > 0:
            pygame.draw.rect(screen, self.color, 
                             (self.x, self.y, progress_width, self.height))
        
        # 枠線
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, 
                             (self.x, self.y, self.width, self.height), 
                             self.border_width)
        
        # テキスト
        if self.show_text:
            text = f"{int(self.value)}/{int(self.max_value)}"
            text_surface = self.font.render(text, True, COLOR_BLACK)
            text_x = self.x + (self.width - text_surface.get_width()) // 2
            text_y = self.y + (self.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
    
    def set_value(self, value: float):
        """値を設定"""
        self.value = max(0, min(value, self.max_value))
    
    def set_max_value(self, max_value: float):
        """最大値を設定"""
        self.max_value = max(0.1, max_value)
        self.value = min(self.value, self.max_value)


class ScrollPanel(Panel):
    """スクロール可能なパネル"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 content_height: int,
                 color: Tuple[int, int, int] = COLOR_GRAY, 
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 1,
                 alpha: int = 200):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        self.content_height = max(content_height, height)
        self.scroll_y = 0
        self.max_scroll = max(0, content_height - height)
        self.dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0
    
    def render(self, screen):
        if not self.visible:
            return
        
        # パネル自体を描画
        super().render(screen)
        
        # スクロールバーを描画
        if self.content_height > self.height:
            bar_height = max(20, int(self.height * (self.height / self.content_height)))
            bar_y = self.y + int(self.scroll_y / self.max_scroll * (self.height - bar_height))
            
            pygame.draw.rect(screen, COLOR_BLACK, 
                             (self.x + self.width - 10, self.y, 10, self.height))
            pygame.draw.rect(screen, COLOR_WHITE, 
                             (self.x + self.width - 8, bar_y, 6, bar_height))
    
    def handle_event(self, event) -> bool:
        if not self.visible or not self.active:
            return False
        
        # スクロールイベント
        if event.type == pygame.MOUSEBUTTONDOWN and self.contains_point(*event.pos):
            if event.button == 4:  # マウスホイール上回転
                self.scroll_y = max(0, self.scroll_y - 20)
                return True
            elif event.button == 5:  # マウスホイール下回転
                self.scroll_y = min(self.max_scroll, self.scroll_y + 20)
                return True
            elif event.button == 1:  # 左クリック
                # スクロールバー領域をクリックした場合はドラッグ開始
                if self.contains_point(*event.pos) and event.pos[0] > self.x + self.width - 10:
                    self.dragging = True
                    self.drag_start_y = event.pos[1]
                    self.drag_start_scroll = self.scroll_y
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # スクロールバーのドラッグ
            drag_distance = event.pos[1] - self.drag_start_y
            self.scroll_y = max(0, min(self.max_scroll,
                                     self.drag_start_scroll + drag_distance * self.max_scroll / self.height))
            return True
        
        # 子要素のイベント処理
        for child in reversed(self.children):  # 描画順と逆順に処理
            if child.active and child.handle_event(event):
                return True
        
        return False
    
    def add_child(self, child):
        """子要素を追加し、コンテンツ高さを更新"""
        super().add_child(child)
        child_bottom = child.y + child.height
        if child_bottom > self.content_height:
            self.content_height = child_bottom
            self.max_scroll = max(0, self.content_height - self.height)
        return child
    
    def update_content_height(self):
        """子要素に基づいてコンテンツ高さを更新"""
        max_height = 0
        for child in self.children:
            child_bottom = child.y + child.height
            if child_bottom > max_height:
                max_height = child_bottom
        
        self.content_height = max(max_height, self.height)
        self.max_scroll = max(0, self.content_height - self.height)


class Menu(Panel):
    """メニュー（選択肢リスト）"""
    def __init__(self, x: int, y: int, width: int, item_height: int,
                 items: List[str], 
                 callbacks: List[Callable] = None,
                 color: Tuple[int, int, int] = COLOR_GRAY,
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 1,
                 alpha: int = 230,
                 font=None, font_size: int = 24):
        height = item_height * len(items)
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.items = items
        self.callbacks = callbacks or [None] * len(items)
        self.item_height = item_height
        self.selected_index = -1
        self.font_size = font_size  # font_size を保存
        
        # font_manager からフォントを取得
        from font_manager import get_font
        self.font = font if font else get_font(font_size)
        
        # ボタンの生成
        self.setup_buttons()
    
    def render(self, screen):
        if not self.visible:
            return
            
        super().render(screen)
    
    def handle_event(self, event) -> bool:
        if not self.visible or not self.active:
            return False
            
        return super().handle_event(event)

    def clear_children(self):
        """子要素をクリア"""
        super().clear_children()

class Dialog(Panel):
    """ダイアログ（メッセージウィンドウなど）"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 title: str = "",
                 color: Tuple[int, int, int] = COLOR_GRAY,
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 2,
                 alpha: int = 230,
                 font=None, font_size: int = 24,
                 close_button: bool = True):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.title = title
        self.font = font or pygame.font.Font(None, font_size)
        
        # タイトルバー
        if title:
            title_height = 30
            self.title_bar = Panel(0, 0, width, title_height, (80, 80, 80), None, 0)
            self.add_child(self.title_bar)
            
            # タイトルテキスト
            title_label = Label(10, 5, title, self.font, font_size, COLOR_WHITE)
            self.title_bar.add_child(title_label)
            
            # 閉じるボタン
            if close_button:
                close_btn = Button(width - 30, 5, 20, 20, "×", None, 20,
                                  (200, 50, 50), COLOR_WHITE, (255, 100, 100),
                                  None, 0, self.close)
                self.title_bar.add_child(close_btn)
        
    def close(self):
        """ダイアログを閉じる"""
        self.visible = False


class BattleForecast(Panel):
    """戦闘予測ウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 attacker=None, defender=None,
                 color: Tuple[int, int, int] = COLOR_GRAY,
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 2,
                 alpha: int = 230,
                 font=None, font_size: int = 24):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.attacker = attacker
        self.defender = defender
        self.font = font or pygame.font.Font(None, font_size)
        self.small_font = pygame.font.Font(None, 20)
        
        # タイトル
        title_label = Label(width//2, 10, "戦闘予測", self.font, font_size, COLOR_WHITE, None, "center")
        self.add_child(title_label)
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        if not self.attacker or not self.defender:
            return
            
        # 左側（攻撃側）
        left_x = 20
        self.add_child(Label(left_x, 50, self.attacker.name, self.font, 28, COLOR_BLUE))
        self.add_child(Label(left_x, 80, f"HP: {self.attacker.current_hp}/{self.attacker.max_hp}", self.small_font))
        
        if self.attacker.equipped_weapon:
            weapon_name = self.attacker.equipped_weapon.name
            self.add_child(Label(left_x, 100, f"武器: {weapon_name}", self.small_font))
        
        # 攻撃力・命中・必殺
        self.add_child(Label(left_x, 120, f"攻撃力: {self.attacker.get_attack_power()}", self.small_font))
        hit_rate = min(100, max(0, self.attacker.get_hit_rate() - self.defender.get_avoid()))
        self.add_child(Label(left_x, 140, f"命中率: {hit_rate}%", self.small_font))
        crit_rate = max(0, self.attacker.get_critical_rate() - self.defender.luck)
        self.add_child(Label(left_x, 160, f"必殺率: {crit_rate}%", self.small_font))
        
        # 右側（防御側）
        right_x = self.width - 150
        self.add_child(Label(right_x, 50, self.defender.name, self.font, 28, COLOR_RED))
        self.add_child(Label(right_x, 80, f"HP: {self.defender.current_hp}/{self.defender.max_hp}", self.small_font))
        
        if self.defender.equipped_weapon:
            weapon_name = self.defender.equipped_weapon.name
            self.add_child(Label(right_x, 100, f"武器: {weapon_name}", self.small_font))
        
        # 防御側の反撃
        counter_text = "反撃あり" if self.can_counter() else "反撃なし"
        self.add_child(Label(right_x, 120, counter_text, self.small_font))
        
        if self.can_counter():
            # 攻撃力・命中・必殺（防御側）
            self.add_child(Label(right_x, 140, f"攻撃力: {self.defender.get_attack_power()}", self.small_font))
            hit_rate = min(100, max(0, self.defender.get_hit_rate() - self.attacker.get_avoid()))
            self.add_child(Label(right_x, 160, f"命中率: {hit_rate}%", self.small_font))
            crit_rate = max(0, self.defender.get_critical_rate() - self.attacker.luck)
            self.add_child(Label(right_x, 180, f"必殺率: {crit_rate}%", self.small_font))
            
        # 攻撃回数
        attacker_hits = "2回" if self.attacker.can_double_attack(self.defender) else "1回"
        defender_hits = "2回" if self.can_counter() and self.defender.can_double_attack(self.attacker) else "1回" if self.can_counter() else "0回"
        
        center_x = self.width // 2
        self.add_child(Label(center_x, 130, "攻撃回数", self.small_font, COLOR_WHITE, None, "center"))
        self.add_child(Label(center_x - 40, 150, attacker_hits, self.small_font, COLOR_BLUE, None, "center"))
        self.add_child(Label(center_x + 40, 150, defender_hits, self.small_font, COLOR_RED, None, "center"))
        
        # 装飾
        pygame.draw.line(screen, COLOR_WHITE, (center_x, 145), (center_x, 165), 1)
    
    def can_counter(self):
        """防御側が反撃可能か判定"""
        if not self.defender or not self.defender.equipped_weapon:
            return False
            
        range_diff = abs(self.attacker.x - self.defender.x) + abs(self.attacker.y - self.defender.y)
        return self.defender.equipped_weapon.range_min <= range_diff <= self.defender.equipped_weapon.range_max
    
    def update_forecast(self, attacker, defender):
        """戦闘予測を更新"""
        self.attacker = attacker
        self.defender = defender
        self.clear_children()
        self.setup_ui()


class StatusWindow(Panel):
    """ステータスウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 unit=None,
                 color: Tuple[int, int, int] = COLOR_GRAY,
                 border_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                 border_width: int = 2,
                 alpha: int = 230,
                 font=None, font_size: int = 24):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.unit = unit
        self.font = font or pygame.font.Font(None, font_size)
        self.title_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        if not self.unit:
            self.add_child(Label(self.width//2, 10, "ユニット未選択", self.font, 24, COLOR_WHITE, None, "center"))
            return
            
        # ユニット名と職業
        self.add_child(Label(self.width//2, 10, self.unit.name, self.title_font, 28, COLOR_WHITE, None, "center"))
        self.add_child(Label(self.width//2, 40, f"Lv {self.unit.level} {self.unit.unit_class}", self.font, 24, COLOR_WHITE, None, "center"))
        
        # HP表示
        hp_bar = ProgressBar(20, 70, self.width - 40, 20, 
                            self.unit.current_hp, self.unit.max_hp,
                            COLOR_GREEN, COLOR_GRAY, COLOR_BLACK, 1, True)
        self.add_child(hp_bar)
        
        # 主要ステータス
        stats_x1 = 20
        stats_x2 = self.width // 2 + 10
        stats_y = 100
        
        # 左側のステータス
        self.add_child(Label(stats_x1, stats_y, f"力: {self.unit.strength}", self.small_font))
        self.add_child(Label(stats_x1, stats_y + 20, f"魔力: {self.unit.magic}", self.small_font))
        self.add_child(Label(stats_x1, stats_y + 40, f"技: {self.unit.skill}", self.small_font))
        self.add_child(Label(stats_x1, stats_y + 60, f"速さ: {self.unit.speed}", self.small_font))
        
        # 右側のステータス
        self.add_child(Label(stats_x2, stats_y, f"幸運: {self.unit.luck}", self.small_font))
        self.add_child(Label(stats_x2, stats_y + 20, f"守備: {self.unit.defense}", self.small_font))
        self.add_child(Label(stats_x2, stats_y + 40, f"魔防: {self.unit.resistance}", self.small_font))
        self.add_child(Label(stats_x2, stats_y + 60, f"移動: {self.unit.movement}", self.small_font))
        
        # 戦闘関連ステータス
        battle_y = stats_y + 90
        if self.unit.equipped_weapon:
            self.add_child(Label(stats_x1, battle_y, f"武器: {self.unit.equipped_weapon.name}", self.small_font))
            self.add_child(Label(stats_x1, battle_y + 20, f"攻撃力: {self.unit.get_attack_power()}", self.small_font))
            self.add_child(Label(stats_x1, battle_y + 40, f"命中率: {self.unit.get_hit_rate()}", self.small_font))
            self.add_child(Label(stats_x2, battle_y + 20, f"回避率: {self.unit.get_avoid()}", self.small_font))
            self.add_child(Label(stats_x2, battle_y + 40, f"必殺率: {self.unit.get_critical_rate()}", self.small_font))
        
        # スキル表示
        skill_y = battle_y + 70
        self.add_child(Label(self.width // 2, skill_y, "スキル", self.font, 24, COLOR_WHITE, None, "center"))
        
        if self.unit.skills:
            skill_list_y = skill_y + 30
            for i, skill in enumerate(self.unit.skills):
                self.add_child(Label(stats_x1, skill_list_y + i * 20, f"・{skill.name}", self.small_font))
                # スキル説明文（長い場合は省略）
                desc = skill.description
                if len(desc) > 30:
                    desc = desc[:27] + "..."
                self.add_child(Label(stats_x1 + 100, skill_list_y + i * 20, desc, self.small_font))
        else:
            self.add_child(Label(self.width // 2, skill_y + 30, "なし", self.small_font, 20, COLOR_WHITE, None, "center"))
    
    def update_unit(self, unit):
        """ユニット情報を更新"""
        self.unit = unit
        self.clear_children()
        self.setup_ui()


class ActionMenu(Menu):
    """行動選択メニュー"""
    def __init__(self, x: int, y: int, width: int = 100, item_height: int = 30,
                 game_manager = None):
        # 基本的な行動メニュー項目
        actions = ["攻撃", "待機", "アイテム", "キャンセル"]
        
        # ゲームマネージャー参照を保持
        self.game_manager = game_manager

        # 救出関連の行動を追加
        self.rescue_actions = ["救出", "降ろす", "捕獲", "捕虜", "交換"]

        # コールバック関数の設定
        callbacks = [
            lambda: self.on_action_selected("attack"),
            lambda: self.on_action_selected("wait"),
            lambda: self.on_action_selected("item"),
            lambda: self.on_action_selected("cancel")
        ]
        
        # フォントとして None を渡す (Menu クラスでは get_font で日本語フォントが使われる)
        super().__init__(x, y, width, item_height, actions, callbacks, font=None, font_size=24)
    
    def on_action_selected(self, action):
        """行動が選択されたときの処理"""
        if not self.game_manager:
            return
            
        if action == "attack":
            self.game_manager.select_action("attack")
        elif action == "wait":
            self.game_manager.select_action("wait")
        elif action == "item":
            # アイテム選択画面の表示（未実装）
            pass
        elif action == "cancel":
            # 移動をキャンセル
            if self.game_manager.selected_unit:
                # 元の位置に戻す処理が必要
                pass
        
        # メニューを閉じる
        self.visible = False

    def setup_buttons(self):
        """ボタンを設定する際にフォントを明示的に指定しない"""
        # Menu クラスの setup_buttons をオーバーライド
        self.clear_children()
        
        from font_manager import get_font
        
        for i, (item, callback) in enumerate(zip(self.items, self.callbacks)):
            # フォントを明示的に指定しない (get_font(font_size) が使われる)
            button = Button(0, i * self.item_height, self.width, self.item_height,
                           item, None, self.font_size,  # None を渡してデフォルトフォントを使う
                           self.color, COLOR_BLACK, (220, 220, 220),
                           None, 0, callback)
            self.add_child(button)

    def update_actions(self, unit):
        """ユニットの状態に応じて行動リストを更新"""
        actions = ["攻撃", "待機", "アイテム"]
        
        # 救出可能なユニットが隣接しているかチェック
        can_rescue = False
        adjacent_units = self.game_manager.get_adjacent_units(unit)
        for adj_unit in adjacent_units:
            if unit.can_rescue(adj_unit):
                can_rescue = True
                break
        
        # 救出中のユニットがいる場合
        if unit.rescuing:
            actions.insert(0, "降ろす")
            actions.insert(1, "交換")
        
        # 救出可能なユニットがいる場合
        elif can_rescue:
            actions.insert(0, "救出")
        
        # 捕獲可能な敵ユニットがいる場合
        can_capture = False
        can_persuade = False
        for adj_unit in adjacent_units:
            if adj_unit.team != unit.team:
                can_capture = True
                if adj_unit.current_hp < 10:
                    can_persuade = True
                break
        
        if can_capture:
            actions.insert(0, "捕獲")
        
        if can_persuade:
            actions.insert(0, "捕虜")
        
        # キャンセルオプションは常に最後
        actions.append("キャンセル")
        
        # アクションをセット
        self.items = actions
        self.setup_buttons()

class UnitMenu(ScrollPanel):
    """ユニット一覧メニュー"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 units=None, on_unit_selected=None):
        super().__init__(x, y, width, height, height)
        
        self.units = units or []
        self.on_unit_selected = on_unit_selected
        self.unit_height = 60  # 各ユニット表示の高さ
        
        # フォントマネージャーは明示的に指定せず、親クラスのメソッドで自動的に使われる
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        # タイトル - フォント指定なし（デフォルトでget_fontを使用）
        title_label = Label(self.width // 2, 10, "ユニット一覧", None, 28, COLOR_WHITE, None, "center")
        self.add_child(title_label)
        
        # ユニットリスト
        for i, unit in enumerate(self.units):
            unit_panel = Panel(10, 40 + i * self.unit_height, self.width - 20, self.unit_height - 5,
                            (60, 60, 60) if unit.team == 0 else (80, 40, 40))
            
            # ユニット名とHP - フォント指定なし
            unit_panel.add_child(Label(10, 5, unit.name, None, 20, COLOR_WHITE))
            unit_panel.add_child(Label(10, 25, f"Lv {unit.level} {unit.unit_class}", None, 16, COLOR_WHITE))
            
            # HPバー
            hp_bar = ProgressBar(100, 7, self.width - 150, 15, 
                                unit.current_hp, unit.max_hp, 
                                COLOR_GREEN, COLOR_GRAY, COLOR_BLACK, 1, True,
                                None, 16)  # フォント指定なし
            unit_panel.add_child(hp_bar)
            
            # クリックハンドラ設定
            unit_index = i  # クロージャのためにインデックスを保存
            
            def make_handler(idx):
                # イベント引数を受け取るように修正
                return lambda event=None: self.handle_unit_selection(idx)
                    
            unit_panel.handle_event = make_handler(unit_index)
            
            self.add_child(unit_panel)
        
        # コンテンツ高さの更新
        self.update_content_height()
    
    def handle_unit_selection(self, index):
        """ユニットが選択されたときの処理"""
        if self.on_unit_selected and 0 <= index < len(self.units):
            self.on_unit_selected(self.units[index])
            return True
        return False
    
    def update_units(self, units):
        """ユニットリストを更新"""
        self.units = units
        self.clear_children()
        self.setup_ui()

class MapController:
    """マップコントロール（移動・攻撃などのマップ操作を担当）"""
    def __init__(self, game_manager, ui_manager):
        self.game_manager = game_manager
        self.ui_manager = ui_manager
        
        # 移動と攻撃の範囲を視覚的に表示するためのサーフェス
        self.move_surface = None
        self.attack_surface = None
        
        # ユニット選択・移動など状態関連
        self.hover_x = -1
        self.hover_y = -1
    
    def update(self):
        """状態の更新"""
        # マウス位置の更新
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hover_x = mouse_x // GRID_SIZE
        self.hover_y = mouse_y // GRID_SIZE
    
    def render(self, screen):
        """マップコントロールの描画"""
        # 移動範囲の描画
        if self.game_manager.phase == "move_unit" and self.game_manager.move_targets:
            if not self.move_surface:
                self._create_move_surface()
            screen.blit(self.move_surface, (0, 0))
        else:
            self.move_surface = None
        
        # 攻撃範囲の描画
        if self.game_manager.phase == "select_attack_target" and self.game_manager.attack_targets:
            if not self.attack_surface:
                self._create_attack_surface()
            screen.blit(self.attack_surface, (0, 0))
        else:
            self.attack_surface = None
        
        # ホバー位置のハイライト
        if self._is_valid_hover_position():
            hover_rect = pygame.Rect(self.hover_x * GRID_SIZE, self.hover_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, COLOR_YELLOW, hover_rect, 2)
    
    def _create_move_surface(self):
        """移動範囲表示用のサーフェスを作成"""
        self.move_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x, y in self.game_manager.move_targets:
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.move_surface, (0, 0, 255, 128), rect)
    
    def _create_attack_surface(self):
        """攻撃範囲表示用のサーフェスを作成"""
        self.attack_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x, y in self.game_manager.attack_targets:
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.attack_surface, (255, 0, 0, 128), rect)
    
    def _is_valid_hover_position(self):
        """現在のホバー位置が有効かどうかをチェック"""
        return (0 <= self.hover_x < self.game_manager.game_map.cols and 
                0 <= self.hover_y < self.game_manager.game_map.rows)
    
    def handle_click(self, x, y):
        """マップ上のクリックを処理"""
        # 現在のフェーズに応じた処理
        if self.game_manager.phase == "select_unit":
            self.game_manager.select_unit(x, y)
        elif self.game_manager.phase == "move_unit":
            if self.game_manager.move_selected_unit(x, y):
                # 移動が成功した場合
                # 攻撃対象がいるかチェック
                enemies = self.game_manager.game_map.get_enemies_in_range(
                    self.game_manager.selected_unit,
                    self.game_manager.attack_targets
                )
                
                if enemies:
                    # 行動メニューを表示
                    self.ui_manager.show_action_menu(x * GRID_SIZE, y * GRID_SIZE)
                else:
                    # 敵がいない場合は自動的に待機
                    self.game_manager.select_action("wait")
            else:
                # 移動先に別のユニットがいるか、移動範囲外の場合
                target_unit = self.game_manager.game_map.get_unit_at(x, y)
                if target_unit:
                    if target_unit.team == self.game_manager.turn_player:
                        # 味方ユニットの場合は選択し直し
                        self.game_manager.select_unit(x, y)
                    else:
                        # 敵ユニットの場合は情報表示
                        self.ui_manager.show_unit_info(target_unit)
        
        elif self.game_manager.phase == "select_attack_target":
            self.game_manager.select_attack_target(x, y)


class UIManager:
    """UI管理クラス（ゲーム全体のUI要素を管理）"""
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.game_manager = game_manager
        
        # フォント初期化 - font_managerを使用
        from font_manager import get_font
        self.font = get_font(24)
        self.small_font = get_font(20)
        self.large_font = get_font(28)
        
        # UI要素
        self.ui_elements = []
        
        # マップコントローラー
        self.map_controller = MapController(game_manager, self)
        
        # UI要素の初期化
        self._init_ui()
    
    def _init_ui(self):
        """UI要素の初期化"""
        # ステータスバー（画面上部）
        status_bar = Panel(0, 0, SCREEN_WIDTH, 30, (30, 30, 30), None, 0)
        
        # ターン表示
        turn_label = Label(10, 5, "", None, 24, COLOR_WHITE)
        status_bar.add_child(turn_label)
        self.turn_label = turn_label
        
        # フェーズ表示
        phase_label = Label(SCREEN_WIDTH - 10, 5, "", None, 24, COLOR_WHITE, None, "right")
        status_bar.add_child(phase_label)
        self.phase_label = phase_label
        
        self.ui_elements.append(status_bar)
        
        # 行動メニュー（初期状態は非表示）
        action_menu = ActionMenu(0, 0, 120, 30, self.game_manager)
        action_menu.visible = False
        self.ui_elements.append(action_menu)
        self.action_menu = action_menu
        
        # 戦闘予測ウィンドウ（初期状態は非表示）
        battle_forecast = BattleForecast(SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 - 100, 350, 200)
        battle_forecast.visible = False
        self.ui_elements.append(battle_forecast)
        self.battle_forecast = battle_forecast
        
        # ユニット情報ウィンドウ（初期状態は非表示）
        unit_info = StatusWindow(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150, 300, 300)
        unit_info.visible = False
        self.ui_elements.append(unit_info)
        self.unit_info = unit_info
        
        # ユニット一覧ボタン - フォント指定なし（デフォルトでget_fontを使用）
        unit_list_btn = Button(SCREEN_WIDTH - 110, 40, 100, 30, "ユニット一覧", None, 20,
                              COLOR_GRAY, COLOR_BLACK, COLOR_WHITE, COLOR_BLACK, 1,
                              self.toggle_unit_list)
        self.ui_elements.append(unit_list_btn)
        
        # ユニット一覧（初期状態は非表示）
        unit_list = UnitMenu(SCREEN_WIDTH - 220, 80, 210, 180, [], self.on_unit_list_selection)
        unit_list.visible = False
        self.ui_elements.append(unit_list)
        self.unit_list = unit_list
        
        # エンドターンボタン - フォント指定なし（デフォルトでget_fontを使用）
        end_turn_btn = Button(SCREEN_WIDTH - 110, SCREEN_HEIGHT - 40, 100, 30, "ターン終了", None, 20,
                             COLOR_GRAY, COLOR_BLACK, COLOR_WHITE, COLOR_BLACK, 1,
                             self.end_turn)
        self.ui_elements.append(end_turn_btn)
        
        # バトルログウィンドウ（初期状態は非表示）
        battle_log = ScrollPanel(10, SCREEN_HEIGHT - 100, 300, 90, 200, (30, 30, 30), COLOR_BLACK, 1, 200)
        battle_log.visible = False
        self.ui_elements.append(battle_log)
        self.battle_log = battle_log
    
    def update(self):
        """状態の更新"""
        # ターン表示の更新
        self.turn_label.set_text(f"ターン {self.game_manager.current_turn+1} - {'プレイヤー' if self.game_manager.turn_player == 0 else '敵'}")
        
        # フェーズ表示の更新
        phase_texts = {
            "select_unit": "ユニット選択",
            "move_unit": "移動先選択",
            "select_action": "行動選択",
            "select_attack_target": "攻撃対象選択"
        }
        self.phase_label.set_text(phase_texts.get(self.game_manager.phase, ""))
        
        # ユニット一覧の更新（表示中の場合）
        if self.unit_list.visible:
            self.unit_list.update_units(self.game_manager.game_map.units)
        
        # マップコントローラーの更新
        self.map_controller.update()
        
        # 各UI要素の更新
        for element in self.ui_elements:
            element.update()
    
    def render(self):
        """UI要素の描画"""
        # マップコントローラーの描画
        self.map_controller.render(self.screen)
        
        # 選択中のユニットを強調表示
        if self.game_manager.selected_unit:
            unit = self.game_manager.selected_unit
            rect = pygame.Rect(unit.x * GRID_SIZE, unit.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, COLOR_YELLOW, rect, 3)
        
        # UI要素の描画
        for element in self.ui_elements:
            if element.visible:
                element.render(self.screen)
        
        # 戦闘アニメーション
        if self.game_manager.combat_animation_active:
            self._render_combat_animation()
    
    def _render_combat_animation(self):
        """戦闘アニメーションの描画"""
        # 既存のrenderer.pyのコードを参照
        if self.game_manager.combat_results:
            # 実装はrenderer.pyに既存のものを活用
            pass
    
    def handle_event(self, event):
        """イベント処理"""
        # UI要素のイベント処理
        for element in reversed(self.ui_elements):  # 前面の要素から処理
            if element.visible and element.active and element.handle_event(event):
                return True
        
        # UIで処理されなかった場合、マップ上のクリックとして処理
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            grid_x, grid_y = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE
            
            # 戦闘アニメーション中は処理しない
            if not self.game_manager.combat_animation_active:
                self.map_controller.handle_click(grid_x, grid_y)
                return True
        
        return False
    
    def show_action_menu(self, x, y):
        """行動メニューを表示"""
        # 画面外にならないように調整
        menu_x = min(x, SCREEN_WIDTH - self.action_menu.width)
        menu_y = min(y, SCREEN_HEIGHT - self.action_menu.height)
        
        self.action_menu.set_position(menu_x, menu_y)
        self.action_menu.visible = True
    
    def show_battle_forecast(self, attacker, defender):
        """戦闘予測を表示"""
        self.battle_forecast.update_forecast(attacker, defender)
        self.battle_forecast.visible = True
    
    def show_unit_info(self, unit):
        """ユニット情報ウィンドウを表示"""
        self.unit_info.update_unit(unit)
        self.unit_info.visible = True
    
    def toggle_unit_list(self):
        """ユニット一覧の表示/非表示を切り替え"""
        if self.unit_list.visible:
            self.unit_list.visible = False
        else:
            self.unit_list.update_units(self.game_manager.game_map.units)
            self.unit_list.visible = True
    
    def on_unit_list_selection(self, unit):
        """ユニット一覧からユニットが選択されたときの処理"""
        # マップ上の該当ユニットにカメラを移動する処理などを実装可能
        self.show_unit_info(unit)
    
    def end_turn(self):
        """ターン終了ボタンの処理"""
        if self.game_manager.turn_player == 0:  # プレイヤーのターンの場合のみ
            self.game_manager.end_player_turn()
            # 敵のターン実行
            self.game_manager.execute_ai_turn()
    
    def add_battle_log(self, text):
        """バトルログにテキストを追加"""
        # ログが表示されていない場合は表示
        if not self.battle_log.visible:
            self.battle_log.visible = True
        
        # 新しいログを追加
        y_pos = 0
        if self.battle_log.children:
            last_child = self.battle_log.children[-1]
            y_pos = last_child.y + last_child.height + 5
        
        log_label = Label(10, y_pos, text, self.small_font, 18, COLOR_WHITE)
        self.battle_log.add_child(log_label)
        
        # 古いログを削除（10件以上の場合）
        while len(self.battle_log.children) > 10:
            self.battle_log.remove_child(self.battle_log.children[0])
        
        # コンテンツ高さの更新
        self.battle_log.update_content_height()