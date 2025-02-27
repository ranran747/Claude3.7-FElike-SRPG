# title_screen.py
import pygame
from ui_system import Panel, Label, Button

class TitleScreen(Panel):
    def __init__(self, x, y, width, height, on_new_game=None, on_continue=None, on_options=None):
        super().__init__(x, y, width, height)
        self.on_new_game = on_new_game
        self.on_continue = on_continue
        self.on_options = on_options
        
        # タイトルロゴ（画像またはテキスト）
        title_label = Label(width // 2, 80, "ファイアーエムブレム風SRPG", None, 36, (255, 255, 0), None, "center")
        self.add_child(title_label)
        
        # ボタン
        start_btn = Button(width // 2 - 100, 200, 200, 40, "はじめから", None, 24, 
                           (60, 100, 60), (255, 255, 255), (80, 150, 80),
                           (0, 0, 0), 1, self.start_new_game)
        self.add_child(start_btn)
        
        continue_btn = Button(width // 2 - 100, 260, 200, 40, "つづきから", None, 24,
                             (60, 60, 100), (255, 255, 255), (80, 80, 150),
                             (0, 0, 0), 1, self.continue_game)
        self.add_child(continue_btn)
        
        options_btn = Button(width // 2 - 100, 320, 200, 40, "オプション", None, 24,
                            (100, 60, 60), (255, 255, 255), (150, 80, 80),
                            (0, 0, 0), 1, self.show_options)
        self.add_child(options_btn)
    
    def start_new_game(self):
        if self.on_new_game:
            self.on_new_game()
    
    def continue_game(self):
        if self.on_continue:
            self.on_continue()
    
    def show_options(self):
        if self.on_options:
            self.on_options()