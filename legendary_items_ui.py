# legendary_items_ui.py
import pygame
from typing import List, Dict, Tuple, Optional, Callable
from ui_system import Panel, Label, Button, ScrollPanel
from legendary_items import LegendaryWeapon, ItemRarity, ItemEffect
from constants import COLOR_BLACK, COLOR_WHITE, COLOR_BLUE, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_GRAY
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class WeaponInfoWindow(Panel):
    """武器の詳細情報を表示するウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 weapon: LegendaryWeapon,
                 on_close: Optional[Callable] = None,
                 on_equip: Optional[Callable] = None,
                 color=(30, 30, 50), border_color=COLOR_WHITE, border_width=2, alpha=230):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.weapon = weapon
        self.on_close = on_close
        self.on_equip = on_equip
        
        # フォント
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # スクロールパネル（背景ストーリー用）
        self.lore_panel = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        if not self.weapon:
            return
        
        # レア度に応じた色
        rarity_colors = {
            ItemRarity.COMMON: COLOR_WHITE,
            ItemRarity.UNCOMMON: (100, 255, 100),  # 緑
            ItemRarity.RARE: (100, 100, 255),      # 青
            ItemRarity.EPIC: (200, 100, 255),      # 紫
            ItemRarity.LEGENDARY: (255, 200, 0)    # 金
        }
        
        # タイトル（武器名）
        title_color = rarity_colors.get(self.weapon.rarity, COLOR_WHITE)
        title_label = Label(self.width // 2, 15, self.weapon.name, self.title_font, 28, title_color, None, "center")
        self.add_child(title_label)
        
        # 閉じるボタン
        close_btn = Button(self.width - 30, 10, 20, 20, "×", None, 20,
                          (200, 50, 50), COLOR_WHITE, (255, 100, 100),
                          None, 0, self.close)
        self.add_child(close_btn)
        
        # レア度表示
        rarity_text = f"レア度: {self.weapon.rarity.name}"
        rarity_label = Label(self.width // 2, 45, rarity_text, self.font, 24, title_color, None, "center")
        self.add_child(rarity_label)
        
        # 武器の基本情報
        stat_x = 30
        stat_y = 80
        
        # 威力・命中・必殺
        self.add_child(Label(stat_x, stat_y, f"威力: {self.weapon.might}", self.font, 24, COLOR_WHITE))
        self.add_child(Label(stat_x, stat_y + 30, f"命中: {self.weapon.hit}", self.font, 24, COLOR_WHITE))
        self.add_child(Label(stat_x, stat_y + 60, f"必殺: {self.weapon.crit}", self.font, 24, COLOR_WHITE))
        
        # 重さ・射程・耐久度
        stat_x2 = self.width // 2 + 30
        self.add_child(Label(stat_x2, stat_y, f"重さ: {self.weapon.weight}", self.font, 24, COLOR_WHITE))
        self.add_child(Label(stat_x2, stat_y + 30, f"射程: {self.weapon.range_min}-{self.weapon.range_max}", self.font, 24, COLOR_WHITE))
        self.add_child(Label(stat_x2, stat_y + 60, f"耐久: {self.weapon.durability}/{self.weapon.max_durability}", self.font, 24, COLOR_WHITE))
        
        # 必要レベル
        req_level_text = f"必要レベル: {self.weapon.required_level}"
        req_level_label = Label(self.width // 2, stat_y + 95, req_level_text, self.font, 24, COLOR_WHITE, None, "center")
        self.add_child(req_level_label)
        
        # 専用キャラクター（ある場合）
        if self.weapon.unique_owner:
            unique_text = f"専用: {self.weapon.unique_owner}"
            unique_label = Label(self.width // 2, stat_y + 125, unique_text, self.font, 24, COLOR_YELLOW, None, "center")
            self.add_child(unique_label)
        
        # 効果一覧
        effect_y = stat_y + 155
        self.add_child(Label(self.width // 2, effect_y, "特殊効果", self.font, 24, COLOR_GREEN, None, "center"))
        
        effect_y += 30
        if self.weapon.effects:
            for i, effect in enumerate(self.weapon.effects):
                effect_text = f"• {effect.name}: {effect.description}"
                self.add_child(Label(stat_x, effect_y + i * 25, effect_text, self.small_font, 18, COLOR_WHITE))
        else:
            self.add_child(Label(self.width // 2, effect_y, "なし", self.small_font, 18, COLOR_WHITE, None, "center"))
        
        # スキル一覧
        skill_y = effect_y + (len(self.weapon.effects) if self.weapon.effects else 1) * 25 + 20
        self.add_child(Label(self.width // 2, skill_y, "付与スキル", self.font, 24, COLOR_BLUE, None, "center"))
        
        skill_y += 30
        skills = self.weapon.get_granted_skills()
        if skills:
            for i, skill in enumerate(skills):
                skill_text = f"• {skill.name}: {skill.description}"
                self.add_child(Label(stat_x, skill_y + i * 25, skill_text, self.small_font, 18, COLOR_WHITE))
        else:
            self.add_child(Label(self.width // 2, skill_y, "なし", self.small_font, 18, COLOR_WHITE, None, "center"))
        
        # 背景ストーリー
        lore_y = skill_y + (len(skills) if skills else 1) * 25 + 20
        self.add_child(Label(self.width // 2, lore_y, "背景ストーリー", self.font, 24, COLOR_YELLOW, None, "center"))
        
        # スクロール可能な背景ストーリーパネル
        lore_panel = ScrollPanel(stat_x, lore_y + 30, self.width - 60, 100, 200, (50, 50, 60), None, 0, 200)
        
        # 背景ストーリーテキスト
        if self.weapon.lore:
            lore_lines = self._wrap_text(self.weapon.lore, self.small_font, lore_panel.width - 20)
            for i, line in enumerate(lore_lines):
                lore_panel.add_child(Label(10, i * 20, line, self.small_font, 18, COLOR_WHITE))
        else:
            lore_panel.add_child(Label(lore_panel.width // 2, 10, "不明", self.small_font, 18, COLOR_WHITE, None, "center"))
        
        self.add_child(lore_panel)
        self.lore_panel = lore_panel
        
        # 装備ボタン（装備可能な場合）
        if self.on_equip:
            equip_btn = Button(self.width // 2 - 50, self.height - 40, 100, 30, "装備",
                              self.font, 20, (60, 100, 60), COLOR_WHITE, (80, 150, 80),
                              COLOR_BLACK, 1, self.equip_weapon)
            self.add_child(equip_btn)
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """テキストを指定幅で折り返す"""
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = font.render(word, True, COLOR_WHITE)
            word_width = word_surface.get_width()
            
            # スペースの幅を計算
            space_width = font.render(' ', True, COLOR_WHITE).get_width()
            
            # この単語を追加すると行の幅を超える場合
            if current_width + word_width + (space_width if current_line else 0) > max_width:
                # 現在の行を確定
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    # 1単語だけで幅を超える場合は分割が必要
                    lines.append(word)
                    current_line = []
                    current_width = 0
            else:
                # 単語を追加
                current_line.append(word)
                current_width += word_width + (space_width if current_line else 0)
        
        # 最後の行を追加
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def equip_weapon(self):
        """武器を装備する"""
        if self.on_equip:
            self.on_equip(self.weapon)
            self.close()
    
    def close(self):
        """ウィンドウを閉じる"""
        self.visible = False
        if self.on_close:
            self.on_close()


class ItemDropWindow(Panel):
    """アイテムドロップ表示用ウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 weapon: LegendaryWeapon,
                 on_take: Optional[Callable] = None,
                 on_discard: Optional[Callable] = None,
                 color=(40, 40, 60), border_color=COLOR_YELLOW, border_width=2, alpha=230):
        super().__init__(x, y, width, height, color, border_color, border_width, alpha)
        
        self.weapon = weapon
        self.on_take = on_take
        self.on_discard = on_discard
        
        # フォント
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # 武器画像（仮）
        self.weapon_image = None
        
        # アニメーション用変数
        self.animation_timer = 0
        self.animation_active = True  # アニメーション中
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        if not self.weapon:
            return
        
        # レア度に応じた色
        rarity_colors = {
            ItemRarity.COMMON: COLOR_WHITE,
            ItemRarity.UNCOMMON: (100, 255, 100),  # 緑
            ItemRarity.RARE: (100, 100, 255),      # 青
            ItemRarity.EPIC: (200, 100, 255),      # 紫
            ItemRarity.LEGENDARY: (255, 200, 0)    # 金
        }
        rarity_color = rarity_colors.get(self.weapon.rarity, COLOR_WHITE)
        
        # タイトル
        title_label = Label(self.width // 2, 15, "新しい武器を発見！", self.title_font, 28, COLOR_YELLOW, None, "center")
        self.add_child(title_label)
        
        # 武器名
        weapon_name_label = Label(self.width // 2, 50, self.weapon.name, self.title_font, 28, rarity_color, None, "center")
        self.add_child(weapon_name_label)
        
        # レア度表示
        rarity_text = f"レア度: {self.weapon.rarity.name}"
        rarity_label = Label(self.width // 2, 80, rarity_text, self.font, 24, rarity_color, None, "center")
        self.add_child(rarity_label)
        
        # 武器の基本情報
        stat_x = 30
        stat_y = 120
        
        self.add_child(Label(stat_x, stat_y, f"威力: {self.weapon.might}", self.font, 24, COLOR_WHITE))
        self.add_child(Label(stat_x, stat_y + 30, f"命中: {self.weapon.hit}", self.font, 24, COLOR_WHITE))
        self.add_child(Label(stat_x, stat_y + 60, f"必殺: {self.weapon.crit}", self.font, 24, COLOR_WHITE))
        
        # 効果の簡易表示
        effect_y = stat_y + 100
        if self.weapon.effects:
            self.add_child(Label(stat_x, effect_y, "特殊効果:", self.font, 24, COLOR_GREEN))
            for i, effect in enumerate(self.weapon.effects[:2]):  # 最初の2つだけ表示
                self.add_child(Label(stat_x + 20, effect_y + 30 + i * 25, f"• {effect.description}", self.small_font, 18, COLOR_WHITE))
            
            # 効果が3つ以上ある場合
            if len(self.weapon.effects) > 2:
                self.add_child(Label(stat_x + 20, effect_y + 80, f"他 {len(self.weapon.effects) - 2} 個の効果...", self.small_font, 18, COLOR_WHITE))
        
        # ボタン
        button_y = self.height - 60
        
        # 取得ボタン
        take_btn = Button(self.width // 2 - 110, button_y, 100, 40, "取得",
                         self.font, 20, (60, 100, 60), COLOR_WHITE, (80, 150, 80),
                         COLOR_BLACK, 1, self.take_weapon)
        self.add_child(take_btn)
        
        # 詳細ボタン
        detail_btn = Button(self.width // 2, button_y, 100, 40, "詳細",
                           self.font, 20, (60, 60, 100), COLOR_WHITE, (80, 80, 150),
                           COLOR_BLACK, 1, self.show_details)
        self.add_child(detail_btn)
        
        # 捨てるボタン
        discard_btn = Button(self.width // 2 + 110, button_y, 100, 40, "捨てる",
                            self.font, 20, (100, 60, 60), COLOR_WHITE, (150, 80, 80),
                            COLOR_BLACK, 1, self.discard_weapon)
        self.add_child(discard_btn)
    
    def update(self):
        """アニメーション更新"""
        super().update()
        
        if self.animation_active:
            self.animation_timer += 1
            
            # アニメーション終了
            if self.animation_timer > 60:  # 約1秒
                self.animation_active = False
    
    def render(self, screen):
        """描画処理（オーバーライド）"""
        super().render(screen)
        
        # アニメーション演出
        if self.animation_active:
            # 輝く効果
            glow_alpha = int(128 + 127 * abs(pygame.math.sin(self.animation_timer * 0.1)))
            border_width = max(1, int(3 * abs(pygame.math.sin(self.animation_timer * 0.1))))
            
            # レア度に応じた色
            rarity_colors = {
                ItemRarity.UNCOMMON: (100, 255, 100, glow_alpha),  # 緑
                ItemRarity.RARE: (100, 100, 255, glow_alpha),      # 青
                ItemRarity.EPIC: (200, 100, 255, glow_alpha),      # 紫
                ItemRarity.LEGENDARY: (255, 200, 0, glow_alpha)    # 金
            }
            
            if self.weapon and self.weapon.rarity in rarity_colors:
                glow_color = rarity_colors[self.weapon.rarity]
                
                # 輝く枠
                glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, glow_color, (0, 0, self.width + 10, self.height + 10), border_width)
                screen.blit(glow_surface, (self.x - 5, self.y - 5))
    
    def take_weapon(self):
        """武器を取得"""
        if self.on_take:
            self.on_take(self.weapon)
            self.visible = False
    
    def show_details(self):
        """武器の詳細を表示"""
        if self.weapon:
            # 詳細ウィンドウの表示を呼び出し側に委譲
            self.visible = False
            
            # UIManagerを通じて詳細ウィンドウを表示させるための呼び出し
            # （ここでは実際の実装は省略、呼び出し側で実装）
    
    def discard_weapon(self):
        """武器を捨てる"""
        if self.on_discard:
            self.on_discard(self.weapon)
            self.visible = False


class InventoryWindow(ScrollPanel):
    """インベントリ表示ウィンドウ"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 items: List,  # 武器やアイテムのリスト
                 unit=None,    # 選択中のユニット（装備変更用）
                 on_select: Optional[Callable] = None,
                 on_close: Optional[Callable] = None,
                 color=(40, 40, 60), border_color=COLOR_WHITE, border_width=2, alpha=230):
        super().__init__(x, y, width, height, height, color, border_color, border_width, alpha)
        
        self.items = items
        self.unit = unit
        self.on_select = on_select
        self.on_close = on_close
        
        # フォント
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # フィルター設定
        self.filter_rarity = None  # 特定のレア度のみ表示
        self.filter_type = None    # 特定の武器タイプのみ表示
        
        # 選択中のアイテム
        self.selected_item = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        # タイトル
        title_text = "インベントリ" if not self.unit else f"{self.unit.name}の装備変更"
        title_label = Label(self.width // 2, 15, title_text, self.title_font, 28, COLOR_WHITE, None, "center")
        self.add_child(title_label)
        
        # 閉じるボタン
        close_btn = Button(self.width - 30, 10, 20, 20, "×", None, 20,
                          (200, 50, 50), COLOR_WHITE, (255, 100, 100),
                          None, 0, self.close)
        self.add_child(close_btn)
        
        # フィルターボタン
        filter_y = 45
        
        # レア度フィルター
        self.add_child(Label(20, filter_y, "レア度:", self.font, 24, COLOR_WHITE))
        
        filter_btns = [
            (None, "全て"),
            (ItemRarity.LEGENDARY, "伝説"),
            (ItemRarity.EPIC, "史詩"),
            (ItemRarity.RARE, "レア"),
            (ItemRarity.UNCOMMON, "珍しい")
        ]
        
        btn_x = 100
        for rarity, label in filter_btns:
            btn = Button(btn_x, filter_y, 60, 25, label, self.small_font, 16,
                        (60, 60, 80), COLOR_WHITE, (100, 100, 150),
                        COLOR_BLACK, 1, lambda r=rarity: self.set_filter_rarity(r))
            
            # 現在のフィルター状態を反映
            if self.filter_rarity == rarity:
                btn.color = (100, 100, 150)
            
            self.add_child(btn)
            btn_x += 70
        
        # アイテムリスト
        self.update_item_list()
    
    def update_item_list(self):
        """アイテムリストを更新"""
        # アイテム表示部分のみクリア
        self.children = [child for child in self.children if child.y < 80]
        
        # フィルタリング
        filtered_items = self.items
        if self.filter_rarity:
            filtered_items = [item for item in filtered_items 
                             if hasattr(item, 'rarity') and item.rarity == self.filter_rarity]
        
        if self.filter_type:
            filtered_items = [item for item in filtered_items 
                             if hasattr(item, 'weapon_type') and item.weapon_type == self.filter_type]
        
        # レア度でソート（降順）
        sorted_items = sorted(filtered_items, 
                             key=lambda item: getattr(item, 'rarity', ItemRarity.COMMON).value, 
                             reverse=True)
        
        # アイテムの表示
        y_offset = 80
        item_height = 70
        
        for i, item in enumerate(sorted_items):
            # アイテムパネル
            item_panel = Panel(10, y_offset, self.width - 30, item_height,
                              (60, 60, 70), COLOR_BLACK, 1, 255)
            
            # レア度に応じた色
            rarity_colors = {
                ItemRarity.COMMON: COLOR_WHITE,
                ItemRarity.UNCOMMON: (100, 255, 100),  # 緑
                ItemRarity.RARE: (100, 100, 255),      # 青
                ItemRarity.EPIC: (200, 100, 255),      # 紫
                ItemRarity.LEGENDARY: (255, 200, 0)    # 金
            }
            
            if hasattr(item, 'rarity'):
                item_color = rarity_colors.get(item.rarity, COLOR_WHITE)
            else:
                item_color = COLOR_WHITE
            
            # アイテム名
            item_name = getattr(item, 'name', '不明なアイテム')
            item_panel.add_child(Label(10, 5, item_name, self.font, 24, item_color))
            
            # アイテム情報
            if hasattr(item, 'weapon_type'):
                weapon_type_text = f"タイプ: {item.weapon_type.name}"
                item_panel.add_child(Label(10, 30, weapon_type_text, self.small_font, 18, COLOR_WHITE))
            
            if hasattr(item, 'might'):
                might_text = f"威力: {item.might}"
                item_panel.add_child(Label(150, 30, might_text, self.small_font, 18, COLOR_WHITE))
            
            # 効果の有無
            if hasattr(item, 'effects') and item.effects:
                effects_text = f"効果: {len(item.effects)}"
                item_panel.add_child(Label(250, 30, effects_text, self.small_font, 18, COLOR_GREEN))
            
            # 装備中の表示
            if self.unit and hasattr(self.unit, 'equipped_weapon') and self.unit.equipped_weapon == item:
                equipped_label = Label(self.width - 100, 10, "装備中", self.font, 20, COLOR_YELLOW)
                item_panel.add_child(equipped_label)
            
            # クリックハンドラ
            item_index = i  # クロージャのためにインデックスを保存
            
            def make_handler(idx):
                return lambda: self.select_item(sorted_items[idx])
            
            item_panel.handle_event = make_handler(item_index)
            
            self.add_child(item_panel)
            y_offset += item_height + 5
        
        # コンテンツ高さの更新
        self.update_content_height()
    
    def set_filter_rarity(self, rarity):
        """レア度フィルターを設定"""
        self.filter_rarity = rarity
        self.update_item_list()
    
    def set_filter_type(self, type_):
        """武器タイプフィルターを設定"""
        self.filter_type = type_
        self.update_item_list()
    
    def select_item(self, item):
        """アイテムを選択"""
        self.selected_item = item
        
        if self.on_select:
            self.on_select(item)
    
    def close(self):
        """ウィンドウを閉じる"""
        self.visible = False
        if self.on_close:
            self.on_close()


# UIManagerに追加するメソッド
def show_weapon_info(self, weapon, on_equip=None):
    """武器情報ウィンドウを表示"""
    weapon_info = WeaponInfoWindow(
        SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400,
        weapon, None, on_equip
    )
    self.ui_elements.append(weapon_info)
    return weapon_info

def show_item_drop(self, weapon, on_take=None, on_discard=None):
    """アイテムドロップウィンドウを表示"""
    drop_window = ItemDropWindow(
        SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300,
        weapon, on_take, on_discard
    )
    self.ui_elements.append(drop_window)
    return drop_window

def show_inventory(self, items, unit=None, on_select=None):
    """インベントリウィンドウを表示"""
    inventory = InventoryWindow(
        SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 200, 600, 400,
        items, unit, on_select
    )
    self.ui_elements.append(inventory)
    return inventory