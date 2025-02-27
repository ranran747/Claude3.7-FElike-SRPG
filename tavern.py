# tavern.py
import pygame
from ui_system import Panel, Label, Button, ScrollPanel

class Tavern(Panel):
    def __init__(self, x, y, width, height, game_manager, on_close=None):
        super().__init__(x, y, width, height)
        self.game_manager = game_manager
        self.on_close = on_close
        
        # 酒場タイトル
        title_label = Label(width // 2, 20, "酒場", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # タブボタン
        tab_y = 60
        tab_width = width // 3 - 20
        
        support_tab = Button(20, tab_y, tab_width, 30, "支援会話", None, 20,
                            (80, 60, 100), (255, 255, 255), (120, 80, 150),
                            (0, 0, 0), 1, lambda: self.change_tab("support"))
        self.add_child(support_tab)
        
        skill_tab = Button(30 + tab_width, tab_y, tab_width, 30, "スキル編集", None, 20,
                          (60, 80, 100), (255, 255, 255), (80, 120, 150),
                          (0, 0, 0), 1, lambda: self.change_tab("skill"))
        self.add_child(skill_tab)
        
        info_tab = Button(40 + tab_width * 2, tab_y, tab_width, 30, "噂を聞く", None, 20,
                         (100, 80, 60), (255, 255, 255), (150, 120, 80),
                         (0, 0, 0), 1, lambda: self.change_tab("info"))
        self.add_child(info_tab)
        
        # 閉じるボタン
        close_btn = Button(width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close_tavern)
        self.add_child(close_btn)
        
        # コンテンツパネル
        content_panel = Panel(20, tab_y + 40, width - 40, height - tab_y - 60, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(content_panel)
        self.content_panel = content_panel
        
        # 現在のタブ
        self.current_tab = "support"
        
        # タブの内容を更新
        self.update_tab_content()
    
    def change_tab(self, tab_name):
        """タブを切り替える"""
        self.current_tab = tab_name
        self.update_tab_content()
    
    def update_tab_content(self):
        """現在のタブに応じた内容を表示"""
        self.content_panel.clear_children()
        
        if self.current_tab == "support":
            self.show_support_tab()
        elif self.current_tab == "skill":
            self.show_skill_tab()
        elif self.current_tab == "info":
            self.show_info_tab()
    
    def show_support_tab(self):
        """支援会話タブの表示"""
        # 支援会話一覧（支援システムから取得）
        available_supports = self.game_manager.get_available_support_conversations()
        
        if not available_supports:
            # 閲覧可能な支援会話がない場合
            self.content_panel.add_child(Label(
                self.content_panel.width // 2, 30,
                "閲覧可能な支援会話はありません。",
                None, 24, (200, 200, 200), None, "center"
            ))
            return
        
        # 支援会話リスト
        for i, (char1, char2, level) in enumerate(available_supports):
            support_panel = Panel(10, i * 80 + 10, self.content_panel.width - 20, 70, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # キャラクター名と支援レベル
            support_panel.add_child(Label(10, 10, f"{char1} ＆ {char2}", None, 20, (255, 255, 255)))
            
            # 支援レベル
            level_text = f"支援レベル: {level.name}"
            level_colors = {
                "C": (150, 150, 255),
                "B": (100, 100, 255),
                "A": (50, 50, 255),
                "S": (255, 150, 150)
            }
            level_color = level_colors.get(level.name, (200, 200, 200))
            support_panel.add_child(Label(10, 35, level_text, None, 18, level_color))
            
            # 閲覧ボタン
            view_btn = Button(support_panel.width - 90, 20, 80, 30, "閲覧", None, 18,
                             (60, 100, 60), (255, 255, 255), (80, 150, 80),
                             (0, 0, 0), 1, lambda c1=char1, c2=char2, lvl=level: self.view_support_conversation(c1, c2, lvl))
            support_panel.add_child(view_btn)
            
            self.content_panel.add_child(support_panel)
    
    def show_skill_tab(self):
        """スキル編集タブの表示"""
        # ユニット選択部分（左側）
        unit_select = ScrollPanel(0, 0, self.content_panel.width // 2 - 10, self.content_panel.height,
                                 self.content_panel.height, (40, 40, 50), None, 0, 220)
        self.content_panel.add_child(unit_select)
        
        # ユニットリストの取得
        units = [unit for unit in self.game_manager.game_map.units if unit.team == 0]
        
        for i, unit in enumerate(units):
            unit_panel = Panel(10, i * 60 + 10, unit_select.width - 20, 50, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # ユニット名と職業
            unit_panel.add_child(Label(10, 10, f"{unit.name} (Lv.{unit.level})", None, 18, (255, 255, 255)))
            unit_panel.add_child(Label(10, 30, unit.unit_class, None, 16, (200, 200, 200)))
            
            # クリックハンドラを設定
            unit_index = i
            
            def make_handler(idx):
                return lambda: self.select_unit_for_skills(units[idx])
            
            unit_panel.handle_event = make_handler(unit_index)
            
            unit_select.add_child(unit_panel)
        
        # コンテンツ高さを更新
        unit_select.update_content_height()
        
        # スキル編集部分（右側）- 初期状態では非表示
        skill_panel = Panel(self.content_panel.width // 2 + 10, 0, self.content_panel.width // 2 - 10, self.content_panel.height,
                           (40, 40, 50), None, 0, 220)
        self.content_panel.add_child(skill_panel)
        skill_panel.add_child(Label(skill_panel.width // 2, 20, "ユニットを選択してください", None, 18, (200, 200, 200), None, "center"))
        
        # スキルパネルを保存
        self.skill_panel = skill_panel
    
    def show_info_tab(self):
        """噂を聞くタブの表示"""
        # 噂（ヒント）のリスト
        hints = [
            "北の森には珍しい武器が隠されているという噂がある...",
            "この街の南にある湖には、かつて竜が住んでいたという伝説が...",
            "東の山岳地帯では、古代の遺跡が発見されたらしい...",
            "最近、魔物の活動が活発化しているという報告が各地から届いている..."
        ]
        
        # タイトル
        self.content_panel.add_child(Label(self.content_panel.width // 2, 20, "酒場のマスターの話", None, 24, (255, 200, 150), None, "center"))
        
        # 噂のテキスト
        hint_y = 60
        for hint in hints:
            self.content_panel.add_child(Label(20, hint_y, hint, None, 18, (200, 200, 200)))
            hint_y += 40
    
    def select_unit_for_skills(self, unit):
       """スキル編集用のユニット選択"""
       self.skill_panel.clear_children()
       
       # ユニット情報
       self.skill_panel.add_child(Label(10, 10, f"ユニット: {unit.name}", None, 18, (255, 255, 255)))
       self.skill_panel.add_child(Label(10, 35, f"職業: {unit.unit_class}", None, 16, (200, 200, 200)))
       
       # 現在のスキルリスト
       self.skill_panel.add_child(Label(10, 60, "装備中スキル:", None, 18, (255, 255, 200)))
       
       if unit.skills:
           for i, skill in enumerate(unit.skills):
               skill_panel = Panel(10, 90 + i * 70, self.skill_panel.width - 20, 60, (50, 50, 60), (0, 0, 0), 1, 255)
               
               # スキル名
               skill_panel.add_child(Label(10, 10, skill.name, None, 18, (255, 255, 255)))
               
               # スキル説明（短く）
               desc = skill.description
               if len(desc) > 30:
                   desc = desc[:27] + "..."
               skill_panel.add_child(Label(10, 35, desc, None, 14, (200, 200, 200)))
               
               # 外すボタン
               remove_btn = Button(skill_panel.width - 70, 15, 60, 30, "外す", None, 16,
                                  (150, 60, 60), (255, 255, 255), (200, 80, 80),
                                  (0, 0, 0), 1, lambda s=skill: self.remove_skill(unit, s))
               skill_panel.add_child(remove_btn)
               
               self.skill_panel.add_child(skill_panel)
       else:
           self.skill_panel.add_child(Label(self.skill_panel.width // 2, 90, "スキルなし", None, 16, (180, 180, 180), None, "center"))
       
       # 装備可能なスキルリスト（ユニットが習得済みだが装備していないスキル）
       available_skills = self.get_available_skills(unit)
       
       if available_skills:
           self.skill_panel.add_child(Label(10, 210, "習得済みスキル:", None, 18, (255, 255, 200)))
           
           for i, skill in enumerate(available_skills):
               skill_panel = Panel(10, 240 + i * 70, self.skill_panel.width - 20, 60, (50, 50, 60), (0, 0, 0), 1, 255)
               
               # スキル名
               skill_panel.add_child(Label(10, 10, skill.name, None, 18, (255, 255, 255)))
               
               # スキル説明（短く）
               desc = skill.description
               if len(desc) > 30:
                   desc = desc[:27] + "..."
               skill_panel.add_child(Label(10, 35, desc, None, 14, (200, 200, 200)))
               
               # 装備ボタン
               equip_btn = Button(skill_panel.width - 70, 15, 60, 30, "装備", None, 16,
                                 (60, 100, 60), (255, 255, 255), (80, 150, 80),
                                 (0, 0, 0), 1, lambda s=skill: self.equip_skill(unit, s))
               skill_panel.add_child(equip_btn)
               
               self.skill_panel.add_child(skill_panel)
   
   def get_available_skills(self, unit):
       """ユニットが装備可能な（習得済みだが未装備の）スキルを取得"""
       # 実際のゲームでは習得済みスキルのリストからユニットの装備中スキルを除外
       available_skills = []
       
       # 仮のデータ（実際のゲームでは適切なデータソースから取得）
       from skills import create_sample_skills
       all_skills = create_sample_skills()
       
       # 現在装備していないスキルを抽出
       equipped_skill_names = [skill.name for skill in unit.skills]
       for skill in all_skills:
           if skill.name not in equipped_skill_names:
               # このスキルが習得可能か確認（レベルや職業による条件）
               if self.can_learn_skill(unit, skill):
                   available_skills.append(skill)
       
       return available_skills
   
   def can_learn_skill(self, unit, skill):
       """ユニットがスキルを習得可能か確認"""
       # 実際のゲームではより複雑な条件チェック
       # 例：レベル条件、職業条件、前提スキルなど
       
       # 仮の実装：レベルに基づく簡易チェック
       level_req = 1
       if "太陽" in skill.name or "月光" in skill.name:
           level_req = 10
       elif "連撃" in skill.name or "連続攻撃" in skill.name:
           level_req = 5
       
       return unit.level >= level_req
   
   def equip_skill(self, unit, skill):
       """スキルを装備"""
       # スキルスロット制限（仮に3つまで）
       if len(unit.skills) >= 3:
           # スキルスロット上限メッセージ（未実装）
           return
       
       # スキルを追加
       unit.add_skill(skill)
       
       # スキルパネルを更新
       self.select_unit_for_skills(unit)
   
   def remove_skill(self, unit, skill):
       """スキルを外す"""
       # スキルを削除
       unit.remove_skill(skill.name)
       
       # スキルパネルを更新
       self.select_unit_for_skills(unit)
   
   def view_support_conversation(self, char1, char2, level):
       """支援会話の閲覧"""
       # ゲームマネージャーの会話表示メソッドを呼び出す
       self.game_manager.view_support_conversation(char1, char2, level)
       
       # 閲覧後にタブを更新（会話が既読になるため）
       self.update_tab_content()
   
   def close_tavern(self):
       """酒場を閉じる"""
       if self.on_close:
           self.on_close()