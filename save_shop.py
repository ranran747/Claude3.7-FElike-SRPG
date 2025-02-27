# save_shop.py
import pygame
import os
import datetime
from ui_system import Panel, Label, Button, ScrollPanel

class SaveShop(Panel):
    def __init__(self, x, y, width, height, game_manager, save_system, on_close=None):
        super().__init__(x, y, width, height)
        self.game_manager = game_manager
        self.save_system = save_system
        self.on_close = on_close
        
        # セーブショップタイトル
        title_label = Label(width // 2, 20, "セーブ屋", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # 店主のセリフ
        message_label = Label(width // 2, 60, "冒険の記録を残すのかい？どのスロットを使う？", None, 24, (200, 255, 200), None, "center")
        self.add_child(message_label)
        
        # 閉じるボタン
        close_btn = Button(width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close_shop)
        self.add_child(close_btn)
        
        # セーブスロットパネル
        save_slots_panel = Panel(20, 100, width - 40, height - 150, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(save_slots_panel)
        
        # セーブスロットの表示
        self.create_save_slots(save_slots_panel)
    
    def create_save_slots(self, parent_panel):
        """セーブスロットを作成"""
        # 現在のセーブデータを取得
        saves = self.save_system.get_all_saves()
        
        # セーブスロットのレイアウト
        slot_width = parent_panel.width - 20
        slot_height = 80
        slot_spacing = 10
        
        # 9つのセーブスロットを作成
        for i in range(1, 10):
            y_pos = (i - 1) * (slot_height + slot_spacing) + 10
            
            # スロットパネル
            slot_panel = Panel(10, y_pos, slot_width, slot_height, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # スロット番号
            slot_panel.add_child(Label(20, 10, f"スロット {i}", None, 20, (255, 255, 255)))
            
            # セーブデータがある場合は情報を表示
            if i in saves:
                save_info = saves[i]
                
                # 保存日時
                slot_panel.add_child(Label(20, 35, f"保存日時: {save_info['save_time']}", None, 16, (200, 200, 255)))
                
                # プレイ時間
                play_time = save_info.get('play_time', 0)
                hours = play_time // 3600
                minutes = (play_time % 3600) // 60
                time_text = f"プレイ時間: {hours}時間{minutes}分"
                slot_panel.add_child(Label(20, 55, time_text, None, 16, (200, 200, 255)))
                
                # 進行状況
                progress_text = f"シナリオ: {save_info.get('current_scenario', '不明')}"
                slot_panel.add_child(Label(slot_width - 150, 35, progress_text, None, 16, (200, 255, 200)))
                
                # 上書き保存ボタン
                overwrite_btn = Button(slot_width - 170, 10, 80, 25, "上書き", None, 16,
                                      (60, 100, 60), (255, 255, 255), (80, 150, 80),
                                      (0, 0, 0), 1, lambda slot=i: self.save_game(slot))
                slot_panel.add_child(overwrite_btn)
                
                # ロードボタン
                load_btn = Button(slot_width - 80, 10, 70, 25, "ロード", None, 16,
                                 (60, 60, 100), (255, 255, 255), (80, 80, 150),
                                 (0, 0, 0), 1, lambda slot=i: self.load_game(slot))
                slot_panel.add_child(load_btn)
            else:
                # 空きスロット
                slot_panel.add_child(Label(slot_width // 2, 40, "空きスロット", None, 18, (180, 180, 180), None, "center"))
                
                # 新規保存ボタン
                save_btn = Button(slot_width - 80, 10, 70, 25, "保存", None, 16,
                                 (60, 100, 60), (255, 255, 255), (80, 150, 80),
                                 (0, 0, 0), 1, lambda slot=i: self.save_game(slot))
                slot_panel.add_child(save_btn)
            
            parent_panel.add_child(slot_panel)
    
    def save_game(self, slot):
        """ゲームを保存"""
        # ゲームデータの取得
        game_data = self.game_manager.prepare_save_data()
        
        # 保存処理
        success = self.save_system.save_game(slot, game_data)
        
        if success:
            # 保存成功メッセージ（未実装）
            pass
        else:
            # 保存失敗メッセージ（未実装）
            pass
    
    def load_game(self, slot):
        """ゲームをロード"""
        # セーブデータのロード
        save_data = self.save_system.load_game(slot)
        
        if save_data:
            # ロードの実行
            self.game_manager.load_game_data(save_data)
            
            # ロード成功メッセージ（未実装）
            
            # セーブ屋を閉じる
            self.close_shop()
        else:
            # ロード失敗メッセージ（未実装）
            pass
    
    def close_shop(self):
        """セーブ屋を閉じる"""
        if self.on_close:
            self.on_close()