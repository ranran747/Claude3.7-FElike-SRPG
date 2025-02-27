# dialogue_system.py
import pygame
from ui_system import Panel, Label, Button

class DialogueScreen(Panel):
    def __init__(self, x, y, width, height, dialogue_data, on_complete=None):
        super().__init__(x, y, width, height)
        self.dialogue_data = dialogue_data
        self.on_complete = on_complete
        self.current_line = 0
        
        # キャラクター表示領域（左右）
        self.left_char_panel = Panel(20, 70, 120, 150, (40, 40, 80), None, 0, 150)
        self.right_char_panel = Panel(width - 140, 70, 120, 150, (40, 40, 80), None, 0, 150)
        
        self.add_child(self.left_char_panel)
        self.add_child(self.right_char_panel)
        
        # キャラクター名ラベル
        self.left_name = Label(80, 230, "", None, 24, (100, 100, 255), None, "center")
        self.right_name = Label(width - 80, 230, "", None, 24, (255, 100, 100), None, "center")
        
        self.add_child(self.left_name)
        self.add_child(self.right_name)
        
        # 会話テキスト領域
        self.dialogue_panel = Panel(20, height - 120, width - 40, 100, (40, 40, 60), (255, 255, 255), 1, 230)
        self.add_child(self.dialogue_panel)
        
        # 話者名
        self.speaker_label = Label(40, height - 120, "", None, 24, (255, 255, 0))
        self.add_child(self.speaker_label)
        
        # 会話テキスト
        self.text_label = Label(30, height - 90, "", None, 22, (255, 255, 255))
        self.add_child(self.text_label)
        
        # 次へボタン
        self.next_btn = Button(width - 80, height - 40, 60, 30, "次へ", None, 20,
                              (60, 60, 100), (255, 255, 255), (80, 80, 150),
                              (0, 0, 0), 1, self.next_line)
        self.add_child(self.next_btn)
        
        # 最初の会話行を表示
        self.update_dialogue()
    
    def update_dialogue(self):
        """現在の会話行を表示"""
        if not self.dialogue_data or self.current_line >= len(self.dialogue_data):
            # 会話終了
            if self.on_complete:
                self.on_complete()
            return
        
        line = self.dialogue_data[self.current_line]
        speaker = line.get("speaker", "")
        text = line.get("text", "")
        left_char = line.get("left_character", "")
        right_char = line.get("right_character", "")
        
        # 話者と会話テキストを更新
        self.speaker_label.set_text(speaker)
        self.text_label.set_text(text)
        
        # キャラクター名を更新
        self.left_name.set_text(left_char)
        self.right_name.set_text(right_char)
        
        # 話者に応じた色を設定
        if speaker == left_char:
            self.speaker_label.color = (100, 100, 255)  # 左側キャラクターの色
        elif speaker == right_char:
            self.speaker_label.color = (255, 100, 100)  # 右側キャラクターの色
        else:
            self.speaker_label.color = (255, 255, 0)  # デフォルト色
    
    def next_line(self):
        """次の会話行に進む"""
        self.current_line += 1
        
        if self.current_line >= len(self.dialogue_data):
            # 会話終了
            if self.on_complete:
                self.on_complete()
        else:
            self.update_dialogue()