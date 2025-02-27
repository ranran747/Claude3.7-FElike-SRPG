# support_conversation_ui.py
import pygame
from typing import List, Dict, Tuple, Optional, Callable
from ui_system import Panel, Label, Button, ScrollPanel
from support_system import SupportSystem, SupportLevel, SupportConversation
from constants import COLOR_BLACK, COLOR_WHITE, COLOR_BLUE, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_GRAY
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class SupportListWindow(Panel):
    """支援関係一覧を表示するウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 support_system: SupportSystem,
                 unit_name: Optional[str] = None,  # 特定ユニットのみ表示する場合
                 on_select: Optional[Callable] = None,
                 on_close: Optional[Callable] = None,
                 color=(40, 40, 40), border_color=COLOR_WHITE, border_width=2, alpha=230):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.support_system = support_system
        self.unit_name = unit_name
        self.on_select = on_select
        self.on_close = on_close
        
        # フォント
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # スクロールパネル
        self.scroll_panel = None
        
        # 選択中の支援ペア
        self.selected_pair = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        # タイトル
        title_text = "支援関係一覧" if not self.unit_name else f"{self.unit_name}の支援関係"
        title_label = Label(self.width // 2, 15, title_text, self.title_font, 28, COLOR_WHITE, None, "center")
        self.add_child(title_label)
        
        # 閉じるボタン
        close_btn = Button(self.width - 30, 10, 20, 20, "×", None, 20,
                          (200, 50, 50), COLOR_WHITE, (255, 100, 100),
                          None, 0, self.close)
        self.add_child(close_btn)
        
        # スクロールパネル
        scroll_panel = ScrollPanel(10, 50, self.width - 20, self.height - 70,
                                  self.height, (50, 50, 50), COLOR_BLACK, 1, 220)
        self.add_child(scroll_panel)
        self.scroll_panel = scroll_panel
        
        # 支援関係の一覧を表示
        self.update_support_list()
    
    def update_support_list(self):
        """支援関係リストを更新"""
        if not self.scroll_panel:
            return
            
        self.scroll_panel.clear_children()
        
        # 表示する支援ペアを収集
        pairs_to_show = []
        for key, pair in self.support_system.supports.items():
            # 特定ユニットの支援のみ表示する場合
            if self.unit_name and self.unit_name not in pair.characters:
                continue
                
            # 支援レベルがNONEの場合は条件次第で除外
            if pair.current_level == SupportLevel.NONE:
                # 特定ユニット表示時のみNONEも表示
                if not self.unit_name:
                    continue
            
            pairs_to_show.append(pair)
        
        # ソート（支援レベル降順、次に名前順）
        pairs_to_show.sort(key=lambda p: (-p.current_level.value, p.characters[0], p.characters[1]))
        
        # 各支援ペアを表示
        y_offset = 10
        for i, pair in enumerate(pairs_to_show):
            # ペアのパネル
            pair_height = 60
            pair_panel = Panel(5, y_offset, self.scroll_panel.width - 20, pair_height,
                              (60, 60, 60), COLOR_BLACK, 1, 255)
            
            # キャラクター名
            char1, char2 = pair.characters
            names_text = f"{char1} ＆ {char2}"
            pair_panel.add_child(Label(10, 8, names_text, self.font, 24, COLOR_WHITE))
            
            # 支援レベル
            level_colors = {
                SupportLevel.NONE: COLOR_GRAY,
                SupportLevel.C: (150, 150, 255),
                SupportLevel.B: (100, 100, 255),
                SupportLevel.A: (50, 50, 255),
                SupportLevel.S: (255, 150, 150)
            }
            level_text = f"支援レベル: {pair.current_level.name}"
            level_color = level_colors.get(pair.current_level, COLOR_WHITE)
            pair_panel.add_child(Label(10, 30, level_text, self.font, 20, level_color))
            
            # 次のレベルへの進捗
            if pair.current_level != pair.max_level:
                next_points = pair.get_next_required_points()
                progress_text = f"次のレベルまで: {next_points}ポイント"
                pair_panel.add_child(Label(200, 30, progress_text, self.small_font, 18, COLOR_WHITE))
            
            # 会話アイコン（未読会話がある場合）
            if pair.has_available_conversation():
                msg_btn = Button(self.scroll_panel.width - 60, 10, 40, 40, "会話",
                               self.font, 16, (80, 150, 80), COLOR_WHITE, (100, 200, 100),
                               COLOR_BLACK, 1, lambda p=pair: self.select_pair(p))
                pair_panel.add_child(msg_btn)
            
            self.scroll_panel.add_child(pair_panel)
            y_offset += pair_height + 5
        
        # コンテンツ高さの更新
        self.scroll_panel.update_content_height()
    
    def select_pair(self, pair):
        """支援ペアを選択して会話ウィンドウを表示"""
        self.selected_pair = pair
        
        if self.on_select:
            self.on_select(pair.characters[0], pair.characters[1], pair.current_level)
    
    def close(self):
        """ウィンドウを閉じる"""
        self.visible = False

class SupportConversationWindow(Panel):
    """支援会話を表示するウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 conversation: SupportConversation,
                 on_close: Optional[Callable] = None,
                 on_complete: Optional[Callable] = None,
                 color=(20, 20, 60), border_color=COLOR_YELLOW, border_width=2, alpha=230):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.conversation = conversation
        self.on_close = on_close
        self.on_complete = on_complete
        
        # フォント
        self.title_font = pygame.font.Font(None, 28)
        self.name_font = pygame.font.Font(None, 24)
        self.text_font = pygame.font.Font(None, 22)
        
        # 会話の進行状況
        self.current_message_index = 0
        self.current_char_index = 0
        self.message_speed = 2  # 1フレームあたりの文字数
        self.message_delay = 0  # メッセージ間の遅延
        
        # アニメーション用タイマー
        self.animation_timer = 0
        
        # キャラクターの配置（左右）
        if conversation and len(conversation.characters) >= 2:
            self.left_character = conversation.characters[0]
            self.right_character = conversation.characters[1]
        else:
            self.left_character = "???"
            self.right_character = "???"
        
        # 背景画像（仮）
        self.background = None
        
        # 会話メッセージ
        self.messages = []
        if conversation:
            self.messages = conversation.content
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        # タイトル
        title_text = self.conversation.title if self.conversation else "支援会話"
        title_label = Label(self.width // 2, 15, title_text, self.title_font, 28, COLOR_YELLOW, None, "center")
        self.add_child(title_label)
        
        # 支援レベル表示
        level_text = f"支援レベル: {self.conversation.level.name}" if self.conversation else ""
        level_label = Label(self.width // 2, 45, level_text, self.name_font, 24, COLOR_WHITE, None, "center")
        self.add_child(level_label)
        
        # キャラクター表示領域（左右）
        left_char_panel = Panel(20, 70, 120, 150, (40, 40, 80), None, 0, 150)
        right_char_panel = Panel(self.width - 140, 70, 120, 150, (40, 40, 80), None, 0, 150)
        
        # キャラクター名
        left_char_label = Label(80, 230, self.left_character, self.name_font, 24, COLOR_BLUE, None, "center")
        right_char_label = Label(self.width - 80, 230, self.right_character, self.name_font, 24, COLOR_RED, None, "center")
        
        self.add_child(left_char_panel)
        self.add_child(right_char_panel)
        self.add_child(left_char_label)
        self.add_child(right_char_label)
        
        # メッセージウィンドウ
        message_panel = Panel(20, self.height - 120, self.width - 40, 100, (40, 40, 60), COLOR_WHITE, 1, 230)
        self.add_child(message_panel)
        self.message_panel = message_panel
        
        # 発言者名ラベル
        speaker_label = Label(40, self.height - 120, "", self.name_font, 24, COLOR_YELLOW)
        self.add_child(speaker_label)
        self.speaker_label = speaker_label
        
        # メッセージテキスト
        message_label = Label(30, self.height - 95, "", self.text_font, 22, COLOR_WHITE)
        message_label.set_text("")
        self.add_child(message_label)
        self.message_label = message_label
        
        # 進行ボタン（テキスト送り/会話終了）
        next_btn = Button(self.width - 80, self.height - 40, 60, 30, "次へ",
                         self.name_font, 20, (60, 60, 100), COLOR_WHITE, (80, 80, 150),
                         COLOR_BLACK, 1, self.next_message)
        self.add_child(next_btn)
        self.next_btn = next_btn
        
        # 最初のメッセージを表示
        self.update_current_message()
    
    def update(self):
        """状態更新（テキストアニメーション）"""
        super().update()
        
        if not self.messages or self.current_message_index >= len(self.messages):
            return
        
        current_message = self.messages[self.current_message_index]
        full_text = current_message.get("text", "")
        
        # メッセージ遅延中なら待機
        if self.message_delay > 0:
            self.message_delay -= 1
            return
        
        # アニメーションタイマー更新
        self.animation_timer += 1
        
        # 一定間隔で文字を増やす
        if self.animation_timer >= self.message_speed:
            self.animation_timer = 0
            
            # 表示する文字数を増やす
            if self.current_char_index < len(full_text):
                self.current_char_index += 1
                # 現在のテキストを更新
                current_text = full_text[:self.current_char_index]
                self.message_label.set_text(current_text)
                
                # 文字表示時のSE（未実装）
                # self._play_text_sound()
    
    def update_current_message(self):
        """現在のメッセージを更新"""
        if not self.messages or self.current_message_index >= len(self.messages):
            # 会話終了
            self.next_btn.text = "閉じる"
            self.speaker_label.set_text("")
            self.message_label.set_text("（会話終了）")
            return
        
        # 現在のメッセージ取得
        current_message = self.messages[self.current_message_index]
        speaker = current_message.get("speaker", "")
        full_text = current_message.get("text", "")
        
        # 話者名を更新
        self.speaker_label.set_text(speaker)
        
        # 話者によって色を変更
        if speaker == self.left_character:
            self.speaker_label.color = COLOR_BLUE
        elif speaker == self.right_character:
            self.speaker_label.color = COLOR_RED
        else:
            self.speaker_label.color = COLOR_YELLOW
        
        # テキストのアニメーション開始
        self.current_char_index = 0
        self.animation_timer = 0
        self.message_label.set_text("")
    
    def next_message(self):
        """次のメッセージに進む、または会話を終了"""
        # 現在のメッセージがまだ全部表示されていない場合は全部表示
        if self.messages and self.current_message_index < len(self.messages):
            current_message = self.messages[self.current_message_index]
            full_text = current_message.get("text", "")
            
            if self.current_char_index < len(full_text):
                self.current_char_index = len(full_text)
                self.message_label.set_text(full_text)
                return
        
        # 次のメッセージへ
        self.current_message_index += 1
        
        # まだメッセージがある場合
        if self.messages and self.current_message_index < len(self.messages):
            self.message_delay = 10  # 次のメッセージまでの遅延
            self.update_current_message()
        else:
            # 会話終了
            if self.on_complete:
                self.on_complete(self.conversation)
            
            # 閉じるボタンとして機能
            if self.next_btn.text == "閉じる":
                self.close()
    
    def close(self):
        """ウィンドウを閉じる"""
        self.visible = False
        if self.on_close:
            self.on_close()

class SupportConfirmationWindow(Panel):
    """支援レベルアップの確認ウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 char1: str, char2: str, new_level: SupportLevel,
                 on_view_conversation: Optional[Callable] = None,
                 on_close: Optional[Callable] = None,
                 color=(40, 40, 70), border_color=COLOR_YELLOW, border_width=2, alpha=230):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.char1 = char1
        self.char2 = char2
        self.new_level = new_level
        self.on_view_conversation = on_view_conversation
        self.on_close = on_close
        
        # フォント
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 24)
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        # タイトル
        title_label = Label(self.width // 2, 20, "支援レベルアップ！", 
                           self.title_font, 28, COLOR_YELLOW, None, "center")
        self.add_child(title_label)
        
        # キャラクター名
        names_text = f"{self.char1} と {self.char2}"
        names_label = Label(self.width // 2, 60, names_text, 
                           self.font, 24, COLOR_WHITE, None, "center")
        self.add_child(names_label)
        
        # 新しい支援レベル
        level_text = f"支援レベルが{self.new_level.name}になりました！"
        level_label = Label(self.width // 2, 90, level_text, 
                           self.font, 24, COLOR_BLUE, None, "center")
        self.add_child(level_label)
        
        # 効果説明
        bonus = SupportBonus.calculate_from_level(self.new_level)
        effects_text = [
            f"与えるダメージ: +{bonus.damage_bonus}",
            f"受けるダメージ: -{bonus.defense_bonus}",
            f"命中率: +{bonus.hit_bonus}%",
            f"回避率: +{bonus.avoid_bonus}%"
        ]
        
        y_offset = 130
        for text in effects_text:
            effect_label = Label(self.width // 2, y_offset, text, 
                                self.font, 20, COLOR_WHITE, None, "center")
            self.add_child(effect_label)
            y_offset += 25
        
        # 会話を見るボタン
        view_btn = Button(self.width // 2 - 100, self.height - 60, 200, 40, "支援会話を見る",
                         self.font, 20, (60, 100, 60), COLOR_WHITE, (80, 150, 80),
                         COLOR_BLACK, 1, self.view_conversation)
        self.add_child(view_btn)
    
    def view_conversation(self):
        """支援会話を表示"""
        self.visible = False
        if self.on_view_conversation:
            self.on_view_conversation(self.char1, self.char2, self.new_level)
    
    def close(self):
        """ウィンドウを閉じる"""
        self.visible = False
        if self.on_close:
            self.on_close()


# UIManagerに追加するメソッド
def show_support_list(self, unit_name=None):
    """支援リストウィンドウを表示"""
    support_list = SupportListWindow(
        SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400,
        self.game_manager.support_system,
        unit_name,
        lambda char1, char2, level: self.show_support_conversation(char1, char2, level)
    )
    self.ui_elements.append(support_list)
    return support_list

def show_support_conversation(self, char1, char2, level=None):
    """支援会話ウィンドウを表示"""
    conversation = self.game_manager.support_system.get_conversation(char1, char2, level)
    if not conversation:
        return None
        
    # 会話ウィンドウを作成
    conv_window = SupportConversationWindow(
        SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 200, 600, 400,
        conversation,
        None,
        lambda conv: self.game_manager.support_system.mark_conversation_viewed(char1, char2, level)
    )
    self.ui_elements.append(conv_window)
    return conv_window

def show_support_level_up(self, char1, char2, new_level):
    """支援レベルアップ確認ウィンドウを表示"""
    confirm_window = SupportConfirmationWindow(
        SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300,
        char1, char2, new_level,
        lambda c1, c2, lvl: self.show_support_conversation(c1, c2, lvl)
    )
    self.ui_elements.append(confirm_window)
    return confirm_window