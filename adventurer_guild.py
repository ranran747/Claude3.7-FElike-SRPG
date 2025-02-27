# adventurer_guild.py
import pygame
import random
from ui_system import Panel, Label, Button, ScrollPanel
from unit import Unit
from constants import WeaponType

class AdventurerGuild(Panel):
    def __init__(self, x, y, width, height, game_manager, on_close=None):
        super().__init__(x, y, width, height)
        self.game_manager = game_manager
        self.on_close = on_close
        
        # ギルドタイトル
        title_label = Label(width // 2, 20, "冒険者ギルド", None, 30, (255, 255, 200), None, "center")
        self.add_child(title_label)
        
        # タブボタン
        tab_y = 60
        tab_width = width // 3 - 20
        
        recruit_tab = Button(20, tab_y, tab_width, 30, "仲間を探す", None, 20, 
                            (80, 60, 100), (255, 255, 255), (120, 80, 150),
                            (0, 0, 0), 1, lambda: self.change_tab("recruit"))
        self.add_child(recruit_tab)
        
        class_change_tab = Button(30 + tab_width, tab_y, tab_width, 30, "転職", None, 20,
                                 (60, 80, 100), (255, 255, 255), (80, 120, 150),
                                 (0, 0, 0), 1, lambda: self.change_tab("class_change"))
        self.add_child(class_change_tab)
        
        dismiss_tab = Button(40 + tab_width * 2, tab_y, tab_width, 30, "解雇", None, 20,
                            (100, 60, 60), (255, 255, 255), (150, 80, 80),
                            (0, 0, 0), 1, lambda: self.change_tab("dismiss"))
        self.add_child(dismiss_tab)
        
        # コンテンツパネル
        content_panel = Panel(20, tab_y + 40, width - 40, height - tab_y - 100, (40, 40, 50), (0, 0, 0), 1, 220)
        self.add_child(content_panel)
        self.content_panel = content_panel
        
        # 閉じるボタン
        close_btn = Button(width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close_guild)
        self.add_child(close_btn)
        
        # 現在のタブ
        self.current_tab = "recruit"
        
        # タブの内容を更新
        self.update_tab_content()
    
    def change_tab(self, tab_name):
        """タブを切り替える"""
        self.current_tab = tab_name
        self.update_tab_content()
    
    def update_tab_content(self):
        """現在のタブに応じた内容を表示"""
        self.content_panel.clear_children()
        
        if self.current_tab == "recruit":
            self.show_recruit_tab()
        elif self.current_tab == "class_change":
            self.show_class_change_tab()
        elif self.current_tab == "dismiss":
            self.show_dismiss_tab()
    
    def show_recruit_tab(self):
        """仲間を探すタブの表示"""
        # 募集中のユニット（例えば3人）を表示
        available_units = self.get_available_recruits(3)
        
        for i, unit in enumerate(available_units):
            unit_panel = Panel(10, i * 120 + 10, self.content_panel.width - 20, 110, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # ユニット名と職業
            unit_panel.add_child(Label(10, 10, f"{unit['name']} ({unit['class']})", None, 20, (255, 255, 255)))
            
            # レベルと主要ステータス
            stats_text = f"Lv.{unit['level']}  HP:{unit['hp']}  力:{unit['strength']}  速:{unit['speed']}  技:{unit['skill']}"
            unit_panel.add_child(Label(10, 35, stats_text, None, 16, (200, 200, 200)))
            
            # スキル
            skills_text = "スキル: " + (", ".join([s['name'] for s in unit['skills']]) if unit['skills'] else "なし")
            unit_panel.add_child(Label(10, 55, skills_text, None, 16, (200, 200, 200)))
            
            # 雇用費用
            cost_text = f"雇用費: {unit['cost']}G"
            unit_panel.add_child(Label(10, 80, cost_text, None, 18, (255, 255, 0)))
            
            # 雇用ボタン
            recruit_btn = Button(unit_panel.width - 90, 75, 80, 30, "雇用", None, 18,
                                (60, 100, 60), (255, 255, 255), (80, 150, 80),
                                (0, 0, 0), 1, lambda u=unit: self.recruit_unit(u))
            unit_panel.add_child(recruit_btn)
            
            self.content_panel.add_child(unit_panel)
    
    def show_class_change_tab(self):
        """転職タブの表示"""
        # プレイヤーユニットのリスト
        units = [unit for unit in self.game_manager.game_map.units if unit.team == 0]
        
        # スクロール可能なユニットリスト
        unit_list = ScrollPanel(0, 0, self.content_panel.width // 2 - 10, self.content_panel.height, 
                               self.content_panel.height, (40, 40, 50), None, 0, 220)
        self.content_panel.add_child(unit_list)
        
        # 各ユニットを表示
        for i, unit in enumerate(units):
            unit_panel = Panel(10, i * 70 + 10, unit_list.width - 20, 60, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # ユニット名と職業
            unit_panel.add_child(Label(10, 10, f"{unit.name} (Lv.{unit.level})", None, 18, (255, 255, 255)))
            unit_panel.add_child(Label(10, 35, f"職業: {unit.unit_class}", None, 16, (200, 200, 200)))
            
            # クリックハンドラを設定
            unit_index = i
            
            def make_handler(idx):
                return lambda: self.select_unit_for_class_change(units[idx])
            
            unit_panel.handle_event = make_handler(unit_index)
            
            unit_list.add_child(unit_panel)
        
        # コンテンツ高さを更新
        unit_list.update_content_height()
        
        # 職業リストと詳細（右側）- 初期状態では非表示
        class_panel = Panel(self.content_panel.width // 2 + 10, 0, self.content_panel.width // 2 - 10, self.content_panel.height,
                           (40, 40, 50), None, 0, 220)
        self.content_panel.add_child(class_panel)
        class_panel.add_child(Label(class_panel.width // 2, 20, "ユニットを選択してください", None, 18, (200, 200, 200), None, "center"))
        
        # 職業リストパネルを保存
        self.class_panel = class_panel
    
    def show_dismiss_tab(self):
        """解雇タブの表示"""
        # プレイヤーユニットのリスト
        units = [unit for unit in self.game_manager.game_map.units if unit.team == 0]
        
        # 各ユニットを表示
        for i, unit in enumerate(units):
            unit_panel = Panel(10, i * 70 + 10, self.content_panel.width - 20, 60, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # ユニット名と職業
            unit_panel.add_child(Label(10, 10, f"{unit.name} (Lv.{unit.level} {unit.unit_class})", None, 18, (255, 255, 255)))
            
            # ステータス
            stats_text = f"HP:{unit.max_hp}  力:{unit.strength}  速:{unit.speed}  技:{unit.skill}"
            unit_panel.add_child(Label(10, 35, stats_text, None, 16, (200, 200, 200)))
            
            # 解雇ボタン（主人公など重要キャラは解雇不可）
            if not unit.is_important:
                dismiss_btn = Button(unit_panel.width - 90, 15, 80, 30, "解雇", None, 18,
                                    (150, 60, 60), (255, 255, 255), (200, 80, 80),
                                    (0, 0, 0), 1, lambda u=unit: self.confirm_dismiss(u))
                unit_panel.add_child(dismiss_btn)
            
            self.content_panel.add_child(unit_panel)
    
    def get_available_recruits(self, count):
        """募集可能なユニットのリストを取得"""
        # 実際のゲームではデータベースから取得するなど
        recruits = []
        
        classes = ["戦士", "ナイト", "アーチャー", "シーフ", "魔道士", "僧侶"]
        names = ["アルフレッド", "ベアトリス", "カルロス", "デイジー", "エドワード", "フローラ"]
        
        for i in range(count):
            unit_class = random.choice(classes)
            level = random.randint(1, 5)
            
            # クラスに応じた基本ステータス
            base_stats = {
                "戦士": {"hp": 20, "strength": 7, "magic": 0, "skill": 5, "speed": 5},
                "ナイト": {"hp": 22, "strength": 8, "magic": 0, "skill": 3, "speed": 3},
                "アーチャー": {"hp": 18, "strength": 5, "magic": 0, "skill": 7, "speed": 6},
                "シーフ": {"hp": 16, "strength": 4, "magic": 0, "skill": 8, "speed": 9},
                "魔道士": {"hp": 15, "strength": 2, "magic": 7, "skill": 5, "speed": 5},
                "僧侶": {"hp": 17, "strength": 3, "magic": 6, "skill": 4, "speed": 4}
            }
            
            # レベルに応じた成長（簡易的）
            stats = base_stats[unit_class].copy()
            for stat in stats:
                stats[stat] += (level - 1) * random.randint(0, 2)
            
            # スキルの追加（ランダム）
            skills = []
            if random.random() < 0.7:  # 70%の確率でスキルを持つ
                skills.append({"name": "会心", "description": "クリティカル率+10%"})
            
            recruit = {
                "name": random.choice(names),
                "class": unit_class,
                "level": level,
                "hp": stats["hp"],
                "strength": stats["strength"],
                "magic": stats["magic"],
                "skill": stats["skill"],
                "speed": stats["speed"],
                "skills": skills,
                "cost": level * 1000 + random.randint(100, 500)  # レベルに応じたコスト
            }
            
            recruits.append(recruit)
        
        return recruits
    
    def recruit_unit(self, unit_data):
        """ユニットを雇用"""
        # お金のチェック
        if self.game_manager.player_gold < unit_data["cost"]:
            # お金が足りないメッセージ
            return
        
        # 雇用処理
        self.game_manager.player_gold -= unit_data["cost"]
        
        # ユニットの生成
        new_unit = Unit(
            unit_data["name"],
            unit_data["class"],
            unit_data["level"],
            unit_data["hp"],
            unit_data["strength"],
            unit_data["magic"],
            unit_data["skill"],
            unit_data["speed"],
            random.randint(3, 7),  # 幸運
            random.randint(3, 7),  # 守備
            random.randint(2, 5),  # 魔防
            4,  # 移動力
            0,  # プレイヤーチーム
            []  # 武器（後で装備）
        )
        
        # スキルの追加
        for skill_data in unit_data["skills"]:
            # スキルの生成と追加（実際のコードでは適切なスキルオブジェクトを生成）
            pass
        
        # 新しいユニットのチームに追加
        self.game_manager.add_unit_to_party(new_unit)
        
        # タブの内容を更新
        self.update_tab_content()
        
        # 雇用完了メッセージ（未実装）
    
    def select_unit_for_class_change(self, unit):
        """転職のためのユニット選択"""
        self.class_panel.clear_children()
        
        # ユニット情報
        self.class_panel.add_child(Label(10, 10, f"ユニット: {unit.name}", None, 18, (255, 255, 255)))
        self.class_panel.add_child(Label(10, 35, f"現在の職業: {unit.unit_class}", None, 16, (200, 200, 200)))
        
        # 転職可能な職業リスト
        self.class_panel.add_child(Label(10, 60, "転職先:", None, 18, (255, 255, 200)))
        
        # 転職可能な職業を取得（実際のゲームではユニットの条件に基づいて）
        available_classes = self.get_available_classes(unit)
        
        for i, class_info in enumerate(available_classes):
            class_panel = Panel(10, 90 + i * 80, self.class_panel.width - 20, 70, (50, 50, 60), (0, 0, 0), 1, 255)
            
            # 職業名
            class_panel.add_child(Label(10, 10, class_info["name"], None, 18, (255, 255, 255)))
            
            # 特徴
            class_panel.add_child(Label(10, 35, f"特徴: {class_info['feature']}", None, 16, (200, 200, 200)))
            
            # 必要条件
            req_text = "条件: "
            if class_info["requirements"]:
                req_text += ", ".join([f"{req}" for req in class_info["requirements"]])
            else:
                req_text += "なし"
            class_panel.add_child(Label(10, 55, req_text, None, 14, (180, 180, 220)))
            
            # 転職ボタン
            change_btn = Button(class_panel.width - 90, 20, 80, 30, "転職", None, 18,
                               (60, 100, 60), (255, 255, 255), (80, 150, 80),
                               (0, 0, 0), 1, lambda c=class_info: self.change_class(unit, c))
            
            # 条件を満たしているかチェック
            can_change = True
            for req in class_info["requirements"]:
                if "レベル" in req:
                    req_level = int(req.split(" ")[1])
                    if unit.level < req_level:
                        can_change = False
            
            # 条件を満たしていない場合はボタンを無効化
            if not can_change:
                change_btn.set_active(False)
                change_btn.color = (100, 100, 100)
            
            class_panel.add_child(change_btn)
            
            self.class_panel.add_child(class_panel)
    
    def get_available_classes(self, unit):
        """ユニットの転職可能な職業を取得"""
        # 実際のゲームでは職業ツリーなどに基づいて
        current_class = unit.unit_class
        
        # 職業ツリー（簡易的な例）
        class_tree = {
            "戦士": [
                {"name": "勇者", "feature": "バランスの取れた強力なユニット", "requirements": ["レベル 10"]},
                {"name": "バーサーカー", "feature": "圧倒的な攻撃力", "requirements": ["レベル 10", "力 12以上"]}
            ],
            "ナイト": [
                {"name": "ジェネラル", "feature": "鉄壁の守備力", "requirements": ["レベル 10"]},
                {"name": "パラディン", "feature": "高い機動力", "requirements": ["レベル 10", "技 8以上"]}
            ],
            "アーチャー": [
                {"name": "スナイパー", "feature": "高い命中率と射程", "requirements": ["レベル 10"]},
                {"name": "ボウナイト", "feature": "弓と機動力を兼ね備える", "requirements": ["レベル 10", "速さ 12以上"]}
            ],
            "シーフ": [
                {"name": "アサシン", "feature": "高い必殺率", "requirements": ["レベル 10"]},
                {"name": "ローグ", "feature": "扉や宝箱を開けられる", "requirements": ["レベル 10", "技 10以上"]}
            ],
            "魔道士": [
                {"name": "セージ", "feature": "高い魔力とスキル", "requirements": ["レベル 10"]},
                {"name": "ダークマージ", "feature": "暗黒魔法が使える", "requirements": ["レベル 10", "魔力 12以上"]}
            ],
            "僧侶": [
                {"name": "ビショップ", "feature": "高い回復力と魔防", "requirements": ["レベル 10"]},
                {"name": "ヴァルキリー", "feature": "回復と攻撃魔法の両立", "requirements": ["レベル 10", "速さ 10以上"]}
            ]
        }
        
        if current_class in class_tree:
            return class_tree[current_class]
        return []
    
    def change_class(self, unit, class_info):
        """職業を変更"""
        # 職業変更の処理
        old_class = unit.unit_class
        unit.unit_class = class_info["name"]
        
        # 職業変更に伴うステータス変更（実際のゲームではより複雑な処理）
        if "勇者" in class_info["name"] or "バーサーカー" in class_info["name"]:
            unit.strength += 2
        elif "ジェネラル" in class_info["name"]:
            unit.defense += 3
        elif "スナイパー" in class_info["name"]:
            unit.skill += 3
        # 他の職業に応じた処理...
        
        # クラスパネルを更新
        self.select_unit_for_class_change(unit)
        
        # 職業変更完了メッセージ（未実装）
    
    def confirm_dismiss(self, unit):
        """解雇の確認"""
        # 確認ダイアログの表示（実際のゲームではダイアログUIを使用）
        response = True  # 仮の確認結果
        
        if response:
            # 解雇処理
            self.game_manager.remove_unit_from_party(unit)
            
            # タブの内容を更新
            self.update_tab_content()
    
    def close_guild(self):
        """ギルドを閉じる"""
        if self.on_close:
            self.on_close()