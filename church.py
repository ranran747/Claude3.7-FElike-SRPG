# church.py
import pygame
import random
from ui_system import Panel, Label, Button, ScrollPanel

class Church(Panel):
    def __init__(self, x, y, width, height, game_manager, on_close=None):
        super().__init__(x, y, width, height)
        self.game_manager = game_manager
        self.on_close = on_close
        
        # 教会タイトル
        title_label = Label(width // 2, 20, "教会", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # 所持金表示
        gold_label = Label(width - 20, 20, f"所持金: {game_manager.player_gold}G", None, 24, (255, 255, 0), None, "right")
        self.add_child(gold_label)
        self.gold_label = gold_label
        
        # 閉じるボタン
        close_btn = Button(width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close_church)
        self.add_child(close_btn)
        
        # 聖職者の言葉
        message_label = Label(width // 2, 60, "ここは神の御加護があるところじゃ。何をしてほしい？", None, 24, (200, 200, 255), None, "center")
        self.add_child(message_label)
        
        # 戦死したユニットリスト
        dead_units_panel = ScrollPanel(20, 100, width - 40, height - 180, height, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(dead_units_panel)
        self.dead_units_panel = dead_units_panel
        
        # 戦死ユニットの表示
        self.update_dead_units_list()
    
    def update_dead_units_list(self):
        """戦死したユニットリストを更新"""
        self.dead_units_panel.clear_children()
        
        # 戦死ユニットの取得（実際のゲームではゲームマネージャーから取得）
        dead_units = self.game_manager.get_dead_units()
        
        if not dead_units:
            # 戦死者がいない場合のメッセージ
            self.dead_units_panel.add_child(Label(
                self.dead_units_panel.width // 2, 30,
                "戦死したユニットはいません。",
                None, 24, (200, 200, 200), None, "center"
            ))
            return
        
        for i, unit in enumerate(dead_units):
            unit_panel = Panel(10, i * 100 + 10, self.dead_units_panel.width - 30, 90, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # ユニット名と情報
            unit_panel.add_child(Label(10, 10, f"{unit.name} (Lv.{unit.level} {unit.unit_class})", None, 20, (255, 255, 255)))
            
            # 戦死した状態（通常、灰、ロスト）
            status_text = "状態: "
            if unit.death_status == "ash":
                status_text += "灰（復活確率低下）"
                status_color = (180, 180, 180)
            elif unit.death_status == "lost":
                status_text += "ロスト（復活不能）"
                status_color = (255, 100, 100)
            else:
                status_text += "戦死"
                status_color = (255, 200, 200)
            
            unit_panel.add_child(Label(10, 35, status_text, None, 18, status_color))
            
            # 復活にかかる費用
            if unit.death_status != "lost":
                cost = self.calculate_revival_cost(unit)
                cost_text = f"復活費用: {cost}G"
                unit_panel.add_child(Label(10, 60, cost_text, None, 18, (255, 255, 0)))
                
                # 復活ボタン
                revive_btn = Button(unit_panel.width - 90, 30, 80, 30, "復活", None, 18,
                                   (60, 100, 60), (255, 255, 255), (80, 150, 80),
                                   (0, 0, 0), 1, lambda u=unit: self.revive_unit(u))
                unit_panel.add_child(revive_btn)
            else:
                # ロスト状態の場合は復活不可のメッセージ
                unit_panel.add_child(Label(10, 60, "復活不能", None, 18, (255, 100, 100)))
            
            self.dead_units_panel.add_child(unit_panel)
        
        # コンテンツ高さの更新
        self.dead_units_panel.update_content_height()
    
    def calculate_revival_cost(self, unit):
        """復活にかかる費用を計算"""
        # レベルに基づく基本コスト
        base_cost = unit.level * 1000
        
        # 灰状態の場合はコスト増加
        if unit.death_status == "ash":
            base_cost *= 2
        
        return base_cost
    
    def revive_unit(self, unit):
        """ユニットを復活させる"""
        # 復活費用の計算
        cost = self.calculate_revival_cost(unit)
        
        # お金のチェック
        if self.game_manager.player_gold < cost:
            # お金が足りないメッセージ（未実装）
            return
        
        # 復活の成功判定
        success = True
        
        # 灰状態の場合は成功率低下
        if unit.death_status == "ash":
            success = random.random() < 0.7  # 70%の確率で成功
        
        if success:
            # 復活処理
            self.game_manager.player_gold -= cost
            self.game_manager.revive_unit(unit)
            
            # 所持金表示の更新
            self.gold_label.set_text(f"所持金: {self.game_manager.player_gold}G")
            
            # 死亡ユニットリストの更新
            self.update_dead_units_list()
            
            # 復活成功メッセージ（未実装）
        else:
            # 失敗した場合：お金は消費するが、ユニットの状態が悪化
            self.game_manager.player_gold -= cost
            
            # 状態の悪化（通常→灰、灰→ロスト）
            if unit.death_status == "ash":
                unit.death_status = "lost"
            else:
                unit.death_status = "ash"
            
            # 所持金表示の更新
            self.gold_label.set_text(f"所持金: {self.game_manager.player_gold}G")
            
            # 死亡ユニットリストの更新
            self.update_dead_units_list()
            
            # 復活失敗メッセージ（未実装）
    
    def close_church(self):
        """教会を閉じる"""
        if self.on_close:
            self.on_close()