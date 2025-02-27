# scenario_select_screen.py
import pygame
from ui_system import Panel, Label, Button, ScrollPanel

class ScenarioSelectScreen(Panel):
    def __init__(self, x, y, width, height, scenarios, on_select=None, on_back=None):
        super().__init__(x, y, width, height)
        self.scenarios = scenarios
        self.on_select = on_select
        self.on_back = on_back
        
        # タイトル
        title_label = Label(width // 2, 20, "シナリオ選択", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # シナリオリスト（スクロール可能）
        scenario_list = ScrollPanel(20, 70, width - 40, height - 150, height, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(scenario_list)
        
        # シナリオの表示
        for i, scenario in enumerate(self.scenarios):
            scenario_panel = Panel(10, i * 100 + 10, scenario_list.width - 30, 90, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # シナリオ名
            scenario_panel.add_child(Label(10, 10, scenario["name"], None, 24, (255, 255, 255)))
            
            # シナリオ説明
            scenario_panel.add_child(Label(10, 40, scenario["description"], None, 18, (200, 200, 200)))
            
            # 推奨レベル
            level_text = f"推奨Lv: {scenario['recommended_level']}"
            scenario_panel.add_child(Label(scenario_panel.width - 100, 10, level_text, None, 20, (200, 255, 200)))
            
            # 選択ボタン
            select_btn = Button(scenario_panel.width - 90, 60, 80, 25, "選択", None, 18,
                               (60, 100, 60), (255, 255, 255), (80, 150, 80),
                               (0, 0, 0), 1, lambda s=scenario: self.select_scenario(s))
            scenario_panel.add_child(select_btn)
            
            scenario_list.add_child(scenario_panel)
        
        # コンテンツの高さを更新
        scenario_list.update_content_height()
        
        # 戻るボタン
        back_btn = Button(20, height - 60, 100, 40, "戻る", None, 24,
                         (100, 60, 60), (255, 255, 255), (150, 80, 80),
                         (0, 0, 0), 1, self.go_back)
        self.add_child(back_btn)
    
    def select_scenario(self, scenario):
        if self.on_select:
            self.on_select(scenario)
    
    def go_back(self):
        if self.on_back:
            self.on_back()