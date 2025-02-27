# map_editor.py
import pygame
import json
import os
from typing import List, Dict, Tuple, Optional, Union, Any
from ui_system import Panel, Label, Button, ScrollPanel
from font_manager import get_font
from constants import GRID_SIZE, TerrainType

class MapEditorTile:
    """マップエディタで使用するタイル情報"""
    def __init__(self, x: int, y: int, terrain_type: TerrainType = TerrainType.PLAIN):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.event_id = None  # イベントID（あれば）
        self.properties = {}  # 追加プロパティ
        self.unit = None     # 配置されたユニット
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（保存用）"""
        data = {
            "x": self.x,
            "y": self.y,
            "terrain_type": self.terrain_type.name,
            "properties": self.properties
        }
        
        if self.event_id:
            data["event_id"] = self.event_id
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MapEditorTile':
        """辞書からタイルを生成"""
        tile = cls(
            x=data["x"],
            y=data["y"],
            terrain_type=TerrainType[data["terrain_type"]]
        )
        
        if "event_id" in data:
            tile.event_id = data["event_id"]
        
        if "properties" in data:
            tile.properties = data["properties"]
        
        return tile


class MapEditorEvent:
    """マップ上のイベント定義"""
    def __init__(self, event_id: str, event_type: str, conditions: Dict = None, actions: List[Dict] = None, position: Tuple[int, int] = None):
        self.event_id = event_id
        self.event_type = event_type  # "trigger", "conversation", "reinforcement" など
        self.conditions = conditions or {}
        self.actions = actions or []
        self.position = position  # タイル座標 (x, y)
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（保存用）"""
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "conditions": self.conditions,
            "actions": self.actions
        }
        
        if self.position:
            data["position"] = self.position
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MapEditorEvent':
        """辞書からイベントを生成"""
        position = tuple(data["position"]) if "position" in data else None
        
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            conditions=data.get("conditions", {}),
            actions=data.get("actions", []),
            position=position
        )


class MapEditorData:
    """マップデータ全体を管理"""
    def __init__(self, map_name: str, rows: int, cols: int, tile_size: int = GRID_SIZE):
        self.map_name = map_name
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.tiles = [[MapEditorTile(x, y) for x in range(cols)] for y in range(rows)]
        self.events = {}  # イベントID -> イベントオブジェクト
        self.units = []   # マップ上のユニット
        self.metadata = {
            "author": "",
            "description": "",
            "difficulty": "normal",
            "tags": [],
            "victory_condition": "defeat_all"
        }
    
    def get_tile(self, x: int, y: int) -> Optional[MapEditorTile]:
        """指定座標のタイルを取得"""
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.tiles[y][x]
        return None
    
    def set_terrain(self, x: int, y: int, terrain_type: TerrainType) -> bool:
        """指定座標の地形を設定"""
        tile = self.get_tile(x, y)
        if tile:
            tile.terrain_type = terrain_type
            return True
        return False
    
    def add_event(self, event: MapEditorEvent) -> bool:
        """イベントを追加"""
        if event.event_id in self.events:
            return False  # 既に同じIDのイベントが存在
        
        self.events[event.event_id] = event
        
        # イベントの位置が指定されている場合、タイルにイベントIDを設定
        if event.position:
            x, y = event.position
            tile = self.get_tile(x, y)
            if tile:
                tile.event_id = event.event_id
        
        return True
    
    def remove_event(self, event_id: str) -> bool:
        """イベントを削除"""
        if event_id not in self.events:
            return False
        
        event = self.events[event_id]
        
        # イベントの位置が指定されている場合、タイルからイベントIDを削除
        if event.position:
            x, y = event.position
            tile = self.get_tile(x, y)
            if tile and tile.event_id == event_id:
                tile.event_id = None
        
        del self.events[event_id]
        return True
    
    def add_unit(self, unit, x: int, y: int) -> bool:
        """ユニットを追加"""
        tile = self.get_tile(x, y)
        if not tile or tile.unit:
            return False  # タイルが存在しないか、既にユニットが配置されている
        
        # ユニットの位置を設定
        unit.x = x
        unit.y = y
        
        # タイルにユニットを設定
        tile.unit = unit
        
        # ユニットリストに追加
        self.units.append(unit)
        
        return True
    
    def remove_unit(self, x: int, y: int) -> bool:
        """ユニットを削除"""
        tile = self.get_tile(x, y)
        if not tile or not tile.unit:
            return False
        
        # ユニットリストから削除
        self.units.remove(tile.unit)
        
        # タイルからユニットを削除
        tile.unit = None
        
        return True
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（保存用）"""
        tiles_data = []
        for row in self.tiles:
            for tile in row:
                # デフォルト値以外のタイルのみ保存
                if (tile.terrain_type != TerrainType.PLAIN or
                    tile.event_id is not None or
                    tile.properties):
                    tiles_data.append(tile.to_dict())
        
        events_data = {}
        for event_id, event in self.events.items():
            events_data[event_id] = event.to_dict()
        
        # ユニットデータ（簡易版）
        units_data = []
        for unit in self.units:
            unit_data = {
                "name": unit.name,
                "class": unit.unit_class,
                "level": unit.level,
                "x": unit.x,
                "y": unit.y,
                "team": unit.team
            }
            
            # 種族、所属、性格などのメタデータがあれば追加
            if hasattr(unit, 'race'):
                unit_data["race"] = unit.race
            if hasattr(unit, 'faction'):
                unit_data["faction"] = unit.faction
            if hasattr(unit, 'alignment'):
                unit_data["alignment"] = unit.alignment
            
            units_data.append(unit_data)
        
        return {
            "map_name": self.map_name,
            "rows": self.rows,
            "cols": self.cols,
            "tile_size": self.tile_size,
            "tiles": tiles_data,
            "events": events_data,
            "units": units_data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MapEditorData':
        """辞書からマップデータを生成"""
        map_data = cls(
            map_name=data["map_name"],
            rows=data["rows"],
            cols=data["cols"],
            tile_size=data.get("tile_size", GRID_SIZE)
        )
        
        # タイル設定
        for tile_data in data.get("tiles", []):
            x = tile_data["x"]
            y = tile_data["y"]
            tile = map_data.get_tile(x, y)
            if tile:
                tile.terrain_type = TerrainType[tile_data["terrain_type"]]
                if "event_id" in tile_data:
                    tile.event_id = tile_data["event_id"]
                if "properties" in tile_data:
                    tile.properties = tile_data["properties"]
        
        # イベント設定
        for event_id, event_data in data.get("events", {}).items():
            event = MapEditorEvent.from_dict(event_data)
            map_data.events[event_id] = event
        
        # ユニット設定
        # 注：実際のゲームではユニットの完全な復元ロジックが必要
        # ここでは簡易版
        if "units" in data:
            # キャラクタークリエイターの参照を取得する必要がある
            from unit import Unit
            
            for unit_data in data["units"]:
                # 仮のユニット生成
                unit = Unit(
                    name=unit_data["name"],
                    unit_class=unit_data["class"],
                    level=unit_data["level"],
                    hp=20,  # 仮の値
                    strength=5,
                    magic=0,
                    skill=5,
                    speed=5,
                    luck=0,
                    defense=5,
                    resistance=0,
                    movement=5,
                    team=unit_data["team"],
                    weapons=[]
                )
                
                # メタデータを設定
                if "race" in unit_data:
                    unit.race = unit_data["race"]
                if "faction" in unit_data:
                    unit.faction = unit_data["faction"]
                if "alignment" in unit_data:
                    unit.alignment = unit_data["alignment"]
                
                # ユニットを配置
                x = unit_data["x"]
                y = unit_data["y"]
                map_data.add_unit(unit, x, y)
        
        # メタデータ設定
        if "metadata" in data:
            map_data.metadata = data["metadata"]
        
        return map_data
    
    def save_to_file(self, directory: str = "maps") -> bool:
        """マップデータをファイルに保存"""
        # ディレクトリが存在しなければ作成
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # 適切なファイル名を生成
        filename = f"{self.map_name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(directory, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"マップ保存エラー: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['MapEditorData']:
        """ファイルからマップデータをロード"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"マップ読み込みエラー: {e}")
            return None


class TerrainPalette(Panel):
    """地形パレットパネル"""
    def __init__(self, x, y, width, height, on_select=None):
        super().__init__(x, y, width, height, (50, 50, 60), (0, 0, 0), 1, 220)
        self.on_select = on_select
        self.selected_terrain = TerrainType.PLAIN
        self.terrain_colors = {
            TerrainType.PLAIN: (200, 200, 100),
            TerrainType.FOREST: (50, 150, 50),
            TerrainType.MOUNTAIN: (150, 100, 50),
            TerrainType.WATER: (50, 100, 200),
            TerrainType.WALL: (100, 100, 100),
        }
        self.setup_ui()
    
    def setup_ui(self):
        """UI要素の設定"""
        # タイトル
        self.add_child(Label(self.width // 2, 10, "地形", None, 24, (255, 255, 200), None, "center"))
        
        # 地形ボタン
        button_size = min(self.width // 3 - 10, self.height // 3 - 10)
        terrain_types = [
            TerrainType.PLAIN,
            TerrainType.FOREST,
            TerrainType.MOUNTAIN,
            TerrainType.WATER,
            TerrainType.WALL
        ]
        
        # 地形名のマッピング
        terrain_names = {
            TerrainType.PLAIN: "平地",
            TerrainType.FOREST: "森",
            TerrainType.MOUNTAIN: "山",
            TerrainType.WATER: "水",
            TerrainType.WALL: "壁"
        }
        
        # ボタン配置
        row, col = 0, 0
        for terrain in terrain_types:
            x = col * (button_size + 10) + 10
            y = row * (button_size + 10) + 40
            
            # 地形ボタン
            terrain_btn = Button(x, y, button_size, button_size, "", None, 20,
                                self.terrain_colors[terrain], (0, 0, 0), self.terrain_colors[terrain],
                                (0, 0, 0), 2, lambda t=terrain: self.select_terrain(t))
            self.add_child(terrain_btn)
            
            # 地形名ラベル
            terrain_label = Label(x + button_size // 2, y + button_size + 5, terrain_names[terrain], None, 16, (200, 200, 200), None, "center")
            self.add_child(terrain_label)
            
            # 次の位置へ
            col += 1
            if col >= 2:
                col = 0
                row += 1
    
    def select_terrain(self, terrain_type):
        """地形を選択"""
        self.selected_terrain = terrain_type
        if self.on_select:
            self.on_select(terrain_type)


class EventEditor(Panel):
    """イベントエディタパネル"""
    def __init__(self, x, y, width, height, map_data, on_close=None):
        super().__init__(x, y, width, height, (40, 40, 50), (255, 255, 255), 2, 230)
        self.map_data = map_data
        self.on_close = on_close
        self.selected_event = None
        self.setup_ui()
    
    def setup_ui(self):
        """UI要素の設定"""
        # タイトル
        self.add_child(Label(self.width // 2, 20, "イベントエディタ", None, 30, (255, 255, 200), None, "center"))
        
        # 閉じるボタン
        close_btn = Button(self.width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close)
        self.add_child(close_btn)
        
        # イベントリスト（左側）
        event_list = ScrollPanel(20, 70, self.width // 3, self.height - 100, self.height, (50, 50, 60), (0, 0, 0), 1, 220)
        self.add_child(event_list)
        self.event_list = event_list
        
        # イベント詳細（右側）
        event_details = Panel(self.width // 3 + 30, 70, self.width * 2 // 3 - 50, self.height - 100, (50, 50, 60), (0, 0, 0), 1, 220)
        self.add_child(event_details)
        self.event_details = event_details
        
        # 新規イベント作成ボタン
        create_btn = Button(self.width // 6, self.height - 60, 100, 40, "新規作成", None, 20,
                           (60, 100, 60), (255, 255, 255), (80, 150, 80),
                           (0, 0, 0), 1, self.create_new_event)
        self.add_child(create_btn)
        
        # イベントリストの更新
        self.update_event_list()
    
    def update_event_list(self):
        """イベントリストを更新"""
        self.event_list.clear_children()
        
        # タイトル
        self.event_list.add_child(Label(self.event_list.width // 2, 10, "イベント一覧", None, 24, (255, 255, 200), None, "center"))
        
        # イベントリスト
        y_offset = 50
        for event_id, event in self.map_data.events.items():
            event_btn = Button(10, y_offset, self.event_list.width - 20, 30, event_id, None, 18,
                             (60, 60, 80), (255, 255, 255), (100, 100, 150),
                             (0, 0, 0), 1, lambda e=event: self.select_event(e))
            
            # 現在選択中のイベントをハイライト
            if self.selected_event and self.selected_event.event_id == event_id:
                event_btn.color = (100, 100, 150)
            
            self.event_list.add_child(event_btn)
            y_offset += 40
        
        self.event_list.update_content_height()
    
    def update_event_details(self):
        """イベント詳細を更新"""
        self.event_details.clear_children()
        
        if not self.selected_event:
            self.event_details.add_child(Label(
                self.event_details.width // 2, 
                self.event_details.height // 2, 
                "イベントを選択してください", 
                None, 20, (200, 200, 200), None, "center"
            ))
            return
        
        # イベントID
        self.event_details.add_child(Label(10, 10, "イベントID:", None, 20, (255, 255, 200)))
        self.event_details.add_child(Label(120, 10, self.selected_event.event_id, None, 20, (255, 255, 255)))
        
        # イベントタイプ
        self.event_details.add_child(Label(10, 40, "タイプ:", None, 20, (255, 255, 200)))
        self.event_details.add_child(Label(120, 40, self.selected_event.event_type, None, 20, (255, 255, 255)))
        
        # 位置情報
        self.event_details.add_child(Label(10, 70, "位置:", None, 20, (255, 255, 200)))
        position_text = f"({self.selected_event.position[0]}, {self.selected_event.position[1]})" if self.selected_event.position else "なし"
        self.event_details.add_child(Label(120, 70, position_text, None, 20, (255, 255, 255)))
        
        # 発動条件
        self.event_details.add_child(Label(10, 100, "発動条件:", None, 20, (255, 255, 200)))
        y_offset = 130
        for condition_key, condition_value in self.selected_event.conditions.items():
            condition_text = f"{condition_key}: {condition_value}"
            self.event_details.add_child(Label(30, y_offset, condition_text, None, 18, (200, 200, 200)))
            y_offset += 25
        
        # アクション
        y_offset += 10
        self.event_details.add_child(Label(10, y_offset, "アクション:", None, 20, (255, 255, 200)))
        y_offset += 30
        for i, action in enumerate(self.selected_event.actions):
            action_text = f"{i+1}. {action.get('type', '不明')} - {action.get('param', {})}"
            self.event_details.add_child(Label(30, y_offset, action_text, None, 18, (200, 200, 200)))
            y_offset += 25
        
        # 編集ボタン
        edit_btn = Button(self.event_details.width // 2 - 50, self.event_details.height - 80, 100, 30, "編集", None, 20,
                         (60, 100, 150), (255, 255, 255), (80, 130, 200),
                         (0, 0, 0), 1, self.edit_event)
        self.event_details.add_child(edit_btn)
        
        # 削除ボタン
        delete_btn = Button(self.event_details.width // 2 - 50, self.event_details.height - 40, 100, 30, "削除", None, 20,
                           (150, 60, 60), (255, 255, 255), (200, 80, 80),
                           (0, 0, 0), 1, self.delete_event)
        self.event_details.add_child(delete_btn)
    
    def select_event(self, event):
        """イベントを選択"""
        self.selected_event = event
        self.update_event_list()
        self.update_event_details()
    
    def create_new_event(self):
        """新規イベントを作成"""
        # イベントID生成（実際のゲームでは適切な命名規則を使用）
        event_id = f"event_{len(self.map_data.events) + 1}"
        
        # 新規イベント作成
        event = MapEditorEvent(
            event_id=event_id,
            event_type="trigger",
            conditions={"turn": 1},
            actions=[{"type": "message", "param": {"text": "新しいイベント"}}]
        )
        
        # マップデータに追加
        self.map_data.add_event(event)
        
        # 選択状態を更新
        self.select_event(event)
    
    def edit_event(self):
        """イベントを編集"""
        if not self.selected_event:
            return
        
        # イベント編集ダイアログを表示（実際のゲームでは適切なUIを実装）
        # ここでは簡単のため省略
    
    def delete_event(self):
        """イベントを削除"""
        if not self.selected_event:
            return
        
        # イベント削除
        self.map_data.remove_event(self.selected_event.event_id)
        
        # 選択状態をクリア
        self.selected_event = None
        
        # UI更新
        self.update_event_list()
        self.update_event_details()
    
    def close(self):
        """ウィンドウを閉じる"""
        if self.on_close:
            self.on_close()


class MapMetadataEditor(Panel):
    """マップメタデータエディタパネル"""
    def __init__(self, x, y, width, height, map_data, on_close=None):
        super().__init__(x, y, width, height, (40, 40, 50), (255, 255, 255), 2, 230)
        self.map_data = map_data
        self.on_close = on_close
        self.setup_ui()
    
    def setup_ui(self):
        """UI要素の設定"""
        # タイトル
        self.add_child(Label(self.width // 2, 20, "マップ情報", None, 30, (255, 255, 200), None, "center"))
        
        # 閉じるボタン
        close_btn = Button(self.width - 80, 20, 60, 30, "閉じる", None, 20,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.close)
        self.add_child(close_btn)
        
        # マップ名
        self.add_child(Label(50, 70, "マップ名:", None, 24, (255, 255, 200)))
        map_name_label = Label(150, 70, self.map_data.map_name, None, 24, (255, 255, 255))
        self.add_child(map_name_label)
        
        # マップサイズ
        self.add_child(Label(50, 110, "サイズ:", None, 24, (255, 255, 200)))
        size_text = f"{self.map_data.cols} x {self.map_data.rows}"
        self.add_child(Label(150, 110, size_text, None, 24, (255, 255, 255)))
        
        # 説明
        self.add_child(Label(50, 150, "説明:", None, 24, (255, 255, 200)))
        description_label = Label(150, 150, self.map_data.metadata.get("description", ""), None, 24, (255, 255, 255))
        self.add_child(description_label)
        
        # 難易度
        self.add_child(Label(50, 190, "難易度:", None, 24, (255, 255, 200)))
        difficulty_label = Label(150, 190, self.map_data.metadata.get("difficulty", "normal"), None, 24, (255, 255, 255))
        self.add_child(difficulty_label)
        
        # 勝利条件
        self.add_child(Label(50, 230, "勝利条件:", None, 24, (255, 255, 200)))
        victory_condition = self.map_data.metadata.get("victory_condition", "defeat_all")
        
        # 勝利条件のマッピング
        victory_names = {
            "defeat_all": "敵全滅",
            "defeat_boss": "ボス撃破",
            "survive": "生存",
            "capture": "拠点確保",
            "escape": "脱出"
        }
        
        victory_text = victory_names.get(victory_condition, victory_condition)
        self.add_child(Label(150, 230, victory_text, None, 24, (255, 255, 255)))
        
        # 編集ボタン
        edit_btn = Button(self.width // 2 - 50, self.height - 60, 100, 40, "編集", None, 24,
                         (60, 100, 60), (255, 255, 255), (80, 150, 80),
                         (0, 0, 0), 1, self.edit_metadata)
        self.add_child(edit_btn)
    
    def edit_metadata(self):
        """マップメタデータを編集"""
        # メタデータ編集ダイアログを表示（実際のゲームでは適切なUIを実装）
        # ここでは簡単のため省略
    
    def close(self):
        """ウィンドウを閉じる"""
        if self.on_close:
            self.on_close()


class MapEditor:
    """マップエディタのメインクラス"""
    def __init__(self, screen, character_creator=None, ui_manager=None):
        self.screen = screen
        self.character_creator = character_creator
        self.ui_manager = ui_manager
        
        # マップデータ
        self.map_data = None
        
        # 編集モード
        self.edit_mode = "terrain"  # "terrain", "event", "unit"
        
        # 選択地形
        self.selected_terrain = TerrainType.PLAIN
        
        # 配置用ユニット
        self.placement_unit = None
        
        # UI要素
        self.terrain_palette = None
        self.toolbar = None
        
        # スクロール位置
        self.scroll_x = 0
        self.scroll_y = 0
        
        # マウス状態
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.last_edited_tile = None
    
    def create_new_map(self, map_name, rows, cols):
        """新規マップを作成"""
        self.map_data = MapEditorData(map_name, rows, cols)
        self._setup_ui()
    
    def load_map(self, filepath):
        """マップをロード"""
        map_data = MapEditorData.load_from_file(filepath)
        if map_data:
            self.map_data = map_data
            self._setup_ui()
            return True
        return False
    
    def save_map(self, directory="maps"):
        """マップを保存"""
        if not self.map_data:
            return False
        
        return self.map_data.save_to_file(directory)
    
    def _setup_ui(self):
        """UI要素のセットアップ"""
        if not self.map_data:
            return
        
        # 地形パレット
        self.terrain_palette = TerrainPalette(
            10, 10, 200, 300,
            on_select=self.select_terrain
        )
        
        # ツールバー
        self.toolbar = self._create_toolbar()
    
    def _create_toolbar(self):
        """ツールバーを作成"""
        toolbar = Panel(10, 320, 200, 300, (50, 50, 60), (0, 0, 0), 1, 220)
        
        # タイトル
        toolbar.add_child(Label(toolbar.width // 2, 10, "ツール", None, 24, (255, 255, 200), None, "center"))
        
        # 編集モードボタン
        terrain_btn = Button(toolbar.width // 2, 50, 150, 30, "地形編集", None, 20,
                            (60, 60, 80), (255, 255, 255), (100, 100, 150),
                            (0, 0, 0), 1, lambda: self.set_edit_mode("terrain"))
        toolbar.add_child(terrain_btn)
        
        event_btn = Button(toolbar.width // 2, 90, 150, 30, "イベント編集", None, 20,
                          (60, 60, 80), (255, 255, 255), (100, 100, 150),
                          (0, 0, 0), 1, lambda: self.set_edit_mode("event"))
        toolbar.add_child(event_btn)
        
        unit_btn = Button(toolbar.width // 2, 130, 150, 30, "ユニット配置", None, 20,
                         (60, 60, 80), (255, 255, 255), (100, 100, 150),
                         (0, 0, 0), 1, lambda: self.set_edit_mode("unit"))
        toolbar.add_child(unit_btn)
        
        # その他のツールボタン
        metadata_btn = Button(toolbar.width // 2, 180, 150, 30, "マップ情報", None, 20,
                            (60, 100, 100), (255, 255, 255), (80, 150, 150),
                            (0, 0, 0), 1, self.show_metadata_editor)
        toolbar.add_child(metadata_btn)
        
        save_btn = Button(toolbar.width // 2, 220, 150, 30, "保存", None, 20,
                         (60, 100, 60), (255, 255, 255), (80, 150, 80),
                         (0, 0, 0), 1, lambda: self.save_map())
        toolbar.add_child(save_btn)
        
        load_btn = Button(toolbar.width // 2, 260, 150, 30, "読み込み", None, 20,
                         (60, 60, 100), (255, 255, 255), (80, 80, 150),
                         (0, 0, 0), 1, self.show_load_dialog)
        toolbar.add_child(load_btn)
        
        return toolbar
    
    def select_terrain(self, terrain_type):
        """地形を選択"""
        self.selected_terrain = terrain_type
    
    def set_edit_mode(self, mode):
        """編集モードを設定"""
        self.edit_mode = mode
        
        # モードに応じた処理
        if mode == "event":
            self.show_event_editor()
        elif mode == "unit" and self.character_creator:
            self.show_character_placement()
    
    def set_placement_unit(self, unit):
        """配置用ユニットを設定"""
        self.placement_unit = unit
        self.edit_mode = "unit"
    
    def show_event_editor(self):
        """イベントエディタを表示"""
        if not self.map_data:
            return
        
        event_editor = EventEditor(
            100, 50, self.screen.get_width() - 200, self.screen.get_height() - 100,
            self.map_data, on_close=lambda: self.ui_manager.remove_window(event_editor)
        )
        
        self.ui_manager.add_window(event_editor)
    
    def show_metadata_editor(self):
        """マップメタデータエディタを表示"""
        if not self.map_data:
            return
        
        metadata_editor = MapMetadataEditor(
            200, 100, self.screen.get_width() - 400, self.screen.get_height() - 200,
            self.map_data, on_close=lambda: self.ui_manager.remove_window(metadata_editor)
        )
        
        self.ui_manager.add_window(metadata_editor)
    
    def show_load_dialog(self):
        """マップロードダイアログを表示"""
        # マップロードダイアログを表示（実際のゲームでは適切なUIを実装）
        # ここでは簡単のため省略
    
    def show_character_placement(self):
        """キャラクター配置パネルを表示"""
        if not self.map_data or not self.character_creator:
            return
        
        from map_editor_ui import MapEditorCharacterPlacer
        
        character_placer = MapEditorCharacterPlacer(
            100, 50, self.screen.get_width() - 200, self.screen.get_height() - 100,
            self.character_creator, self,
            on_close=lambda: self.ui_manager.remove_window(character_placer)
        )
        
        self.ui_manager.add_window(character_placer)
    
    def update(self):
        """状態を更新"""
        # マウス位置の更新
        self.mouse_pos = pygame.mouse.get_pos()
        
        # マウスボタンの状態を更新
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_down = mouse_buttons[0]
        
        # マップ編集
        if self.map_data and self.mouse_down:
            self.process_map_edit()
    
    def process_map_edit(self):
        """マップ編集処理"""
        # マップの表示範囲を計算
        map_x = 220  # UI要素の幅
        map_y = 10
        map_width = self.screen.get_width() - map_x - 10
        map_height = self.screen.get_height() - map_y - 10
        
        # マップ範囲内のクリックかチェック
        if self.mouse_pos[0] < map_x or self.mouse_pos[0] >= map_x + map_width:
            return
        if self.mouse_pos[1] < map_y or self.mouse_pos[1] >= map_y + map_height:
            return
        
        # マップ座標に変換
        tile_x = int((self.mouse_pos[0] - map_x) / GRID_SIZE) + self.scroll_x
        tile_y = int((self.mouse_pos[1] - map_y) / GRID_SIZE) + self.scroll_y
        
        # マップ範囲外なら処理しない
        if tile_x < 0 or tile_x >= self.map_data.cols or tile_y < 0 or tile_y >= self.map_data.rows:
            return
        
        # 同じタイルの連続編集を防止
        if self.last_edited_tile == (tile_x, tile_y):
            return
        
        self.last_edited_tile = (tile_x, tile_y)
        
        # 編集モードに応じた処理
        if self.edit_mode == "terrain":
            # 地形編集
            self.map_data.set_terrain(tile_x, tile_y, self.selected_terrain)
        
        elif self.edit_mode == "event":
            # イベント配置
            tile = self.map_data.get_tile(tile_x, tile_y)
            if not tile:
                return
                
            if tile.event_id:
                # 既存イベントの選択
                event = self.map_data.events.get(tile.event_id)
                if event:
                    self.show_event_properties(event)
            else:
                # 新規イベント作成
                self.create_event_at(tile_x, tile_y)
        
        elif self.edit_mode == "unit":
            # ユニット配置
            if self.placement_unit:
                # 既存のユニットがあれば削除
                self.map_data.remove_unit(tile_x, tile_y)
                
                # 配置用ユニットをコピー
                from copy import deepcopy
                unit_copy = deepcopy(self.placement_unit)
                
                # ユニットを配置
                self.map_data.add_unit(unit_copy, tile_x, tile_y)
            else:
                # 配置用ユニットがない場合は削除モード
                self.map_data.remove_unit(tile_x, tile_y)
    
    def create_event_at(self, x, y):
        """指定位置に新規イベントを作成"""
        # イベントID生成
        event_id = f"event_{len(self.map_data.events) + 1}"
        
        # 新規イベント作成
        event = MapEditorEvent(
            event_id=event_id,
            event_type="trigger",
            conditions={"turn": 1},
            actions=[{"type": "message", "param": {"text": "新しいイベント"}}],
            position=(x, y)
        )
        
        # マップデータに追加
        self.map_data.add_event(event)
        
        # イベントプロパティを表示
        self.show_event_properties(event)
    
    def show_event_properties(self, event):
        """イベントプロパティを表示"""
        # 実際のゲームでは適切なUIを表示
        print(f"イベント '{event.event_id}' を選択")
    
    def render(self):
        """マップエディタを描画"""
        # 背景を描画
        self.screen.fill((30, 30, 40))
        
        # マップが存在する場合はマップを描画
        if self.map_data:
            self._render_map()
        
        # UI要素を描画
        if self.terrain_palette:
            self.terrain_palette.render(self.screen)
        
        if self.toolbar:
            self.toolbar.render(self.screen)
        
        # 編集モード表示
        mode_text = f"モード: {self._get_mode_display_name()}"
        mode_font = get_font(24)
        mode_surface = mode_font.render(mode_text, True, (255, 255, 200))
        self.screen.blit(mode_surface, (220, 10))
    
    def _get_mode_display_name(self):
        """編集モードの表示名を取得"""
        mode_names = {
            "terrain": "地形編集",
            "event": "イベント編集",
            "unit": "ユニット配置"
        }
        return mode_names.get(self.edit_mode, self.edit_mode)
    
    def _render_map(self):
        """マップを描画"""
        # マップの表示範囲を計算
        map_x = 220  # UI要素の幅
        map_y = 50
        map_width = self.screen.get_width() - map_x - 10
        map_height = self.screen.get_height() - map_y - 10
        
        # 表示可能なタイル数
        visible_cols = map_width // GRID_SIZE
        visible_rows = map_height // GRID_SIZE
        
        # スクロール範囲を制限
        self.scroll_x = max(0, min(self.scroll_x, self.map_data.cols - visible_cols))
        self.scroll_y = max(0, min(self.scroll_y, self.map_data.rows - visible_rows))
        
        # タイルを描画
        for y in range(self.scroll_y, min(self.scroll_y + visible_rows, self.map_data.rows)):
            for x in range(self.scroll_x, min(self.scroll_x + visible_cols, self.map_data.cols)):
                # 画面上の位置を計算
                screen_x = map_x + (x - self.scroll_x) * GRID_SIZE
                screen_y = map_y + (y - self.scroll_y) * GRID_SIZE
                
                # タイル情報を取得
                tile = self.map_data.get_tile(x, y)
                if not tile:
                    continue
                
                # 地形の色
                terrain_colors = {
                    TerrainType.PLAIN: (200, 200, 100),
                    TerrainType.FOREST: (50, 150, 50),
                    TerrainType.MOUNTAIN: (150, 100, 50),
                    TerrainType.WATER: (50, 100, 200),
                    TerrainType.WALL: (100, 100, 100),
                }
                
                # 地形を描画
                color = terrain_colors.get(tile.terrain_type, (200, 200, 200))
                rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)  # 枠線
                
                # イベントマーカー
                if tile.event_id:
                    # イベントマーカーを描画（例：赤い星）
                    event_rect = pygame.Rect(screen_x + 5, screen_y + 5, GRID_SIZE - 10, GRID_SIZE - 10)
                    pygame.draw.rect(self.screen, (255, 100, 100), event_rect)
                    
                    # イベントID表示
                    event_font = get_font(12)
                    id_surface = event_font.render("E", True, (0, 0, 0))
                    self.screen.blit(id_surface, (screen_x + GRID_SIZE // 2 - 5, screen_y + GRID_SIZE // 2 - 5))
                
                # ユニット表示
                if tile.unit:
                    # ユニットの色（チームに応じた色）
                    unit_colors = {
                        0: (100, 100, 255),  # プレイヤー
                        1: (255, 100, 100),  # 敵
                    }
                    unit_color = unit_colors.get(tile.unit.team, (200, 200, 200))
                    
                    # ユニットを描画（例：円）
                    pygame.draw.circle(
                        self.screen,
                        unit_color,
                        (screen_x + GRID_SIZE // 2, screen_y + GRID_SIZE // 2),
                        GRID_SIZE // 3
                    )
                    
                    # ユニット名の頭文字
                    name_initial = tile.unit.name[0] if tile.unit.name else "?"
                    unit_font = get_font(16)
                    name_surface = unit_font.render(name_initial, True, (0, 0, 0))
                    name_rect = name_surface.get_rect(center=(screen_x + GRID_SIZE // 2, screen_y + GRID_SIZE // 2))
                    self.screen.blit(name_surface, name_rect)
        
        # マップ名表示
        map_name_font = get_font(20)
        map_name_surface = map_name_font.render(self.map_data.map_name, True, (255, 255, 255))
        self.screen.blit(map_name_surface, (map_x, 20))
    
    def handle_event(self, event):
        """イベント処理"""
        # UI要素のイベント処理
        if self.terrain_palette and self.terrain_palette.handle_event(event):
            return True
        
        if self.toolbar and self.toolbar.handle_event(event):
            return True
        
        # マップ操作イベント処理
        if event.type == pygame.MOUSEBUTTONDOWN:
            # マウスホイールでスクロール
            if event.button == 4:  # 上スクロール
                self.scroll_y = max(0, self.scroll_y - 1)
                return True
            elif event.button == 5:  # 下スクロール
                self.scroll_y += 1
                return True
            elif event.button == 1:  # 左クリック
                self.mouse_down = True
                self.last_edited_tile = None
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左クリック解除
                self.mouse_down = False
                self.last_edited_tile = None
                return True
        
        elif event.type == pygame.KEYDOWN:
            # キーボードでスクロール
            if event.key == pygame.K_LEFT:
                self.scroll_x = max(0, self.scroll_x - 1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.scroll_x += 1
                return True
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 1)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_y += 1
                return True
        
        return False


# マップエディタの新規作成ダイアログ
class NewMapDialog(Panel):
    """新規マップ作成ダイアログ"""
    def __init__(self, x, y, width, height, on_create=None, on_cancel=None):
        super().__init__(x, y, width, height, (40, 40, 50), (255, 255, 255), 2, 230)
        self.on_create = on_create
        self.on_cancel = on_cancel
        
        # マップ設定
        self.map_name = "新規マップ"
        self.map_rows = 15
        self.map_cols = 20
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI要素を設定"""
        # タイトル
        self.add_child(Label(self.width // 2, 20, "新規マップ作成", None, 30, (255, 255, 200), None, "center"))
        
        # マップ名
        self.add_child(Label(self.width // 4, 80, "マップ名:", None, 24, (255, 255, 200)))
        name_label = Label(self.width * 3 // 4, 80, self.map_name, None, 24, (255, 255, 255))
        self.add_child(name_label)
        self.name_label = name_label
        
        # マップ名編集ボタン
        name_edit_btn = Button(self.width - 100, 80, 80, 30, "編集", None, 20,
                             (60, 100, 150), (255, 255, 255), (80, 130, 200),
                             (0, 0, 0), 1, self.edit_map_name)
        self.add_child(name_edit_btn)
        
        # マップサイズ（行数）
        self.add_child(Label(self.width // 4, 130, "高さ:", None, 24, (255, 255, 200)))
        
        rows_down_btn = Button(self.width // 2 - 80, 130, 30, 30, "-", None, 24,
                             (60, 60, 100), (255, 255, 255), (80, 80, 150),
                             (0, 0, 0), 1, lambda: self.change_rows(-1))
        self.add_child(rows_down_btn)
        
        rows_label = Label(self.width // 2, 130, str(self.map_rows), None, 24, (255, 255, 255), None, "center")
        self.add_child(rows_label)
        self.rows_label = rows_label
        
        rows_up_btn = Button(self.width // 2 + 50, 130, 30, 30, "+", None, 24,
                           (60, 60, 100), (255, 255, 255), (80, 80, 150),
                           (0, 0, 0), 1, lambda: self.change_rows(1))
        self.add_child(rows_up_btn)
        
        # マップサイズ（列数）
        self.add_child(Label(self.width // 4, 180, "幅:", None, 24, (255, 255, 200)))
        
        cols_down_btn = Button(self.width // 2 - 80, 180, 30, 30, "-", None, 24,
                             (60, 60, 100), (255, 255, 255), (80, 80, 150),
                             (0, 0, 0), 1, lambda: self.change_cols(-1))
        self.add_child(cols_down_btn)
        
        cols_label = Label(self.width // 2, 180, str(self.map_cols), None, 24, (255, 255, 255), None, "center")
        self.add_child(cols_label)
        self.cols_label = cols_label
        
        cols_up_btn = Button(self.width // 2 + 50, 180, 30, 30, "+", None, 24,
                           (60, 60, 100), (255, 255, 255), (80, 80, 150),
                           (0, 0, 0), 1, lambda: self.change_cols(1))
        self.add_child(cols_up_btn)
        
        # 作成ボタン
        create_btn = Button(self.width // 2 - 110, self.height - 60, 100, 40, "作成", None, 24,
                          (60, 100, 60), (255, 255, 255), (80, 150, 80),
                          (0, 0, 0), 1, self.create_map)
        self.add_child(create_btn)
        
        # キャンセルボタン
        cancel_btn = Button(self.width // 2 + 10, self.height - 60, 100, 40, "キャンセル", None, 24,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.cancel)
        self.add_child(cancel_btn)
    
    def edit_map_name(self):
        """マップ名を編集"""
        # 実際のゲームではテキスト入力ダイアログを表示
        # ここでは簡単のため直接設定
        new_name = "カスタムマップ " + str(random.randint(1, 100))
        self.map_name = new_name
        self.name_label.set_text(new_name)
    
    def change_rows(self, delta):
        """行数を変更"""
        new_rows = max(5, min(50, self.map_rows + delta))
        if new_rows != self.map_rows:
            self.map_rows = new_rows
            self.rows_label.set_text(str(new_rows))
    
    def change_cols(self, delta):
        """列数を変更"""
        new_cols = max(5, min(50, self.map_cols + delta))
        if new_cols != self.map_cols:
            self.map_cols = new_cols
            self.cols_label.set_text(str(new_cols))
    
    def create_map(self):
        """マップを作成"""
        if self.on_create:
            self.on_create(self.map_name, self.map_rows, self.map_cols)
    
    def cancel(self):
        """作成をキャンセル"""
        if self.on_cancel:
            self.on_cancel()


# マップロードダイアログ
class LoadMapDialog(Panel):
    """マップロードダイアログ"""
    def __init__(self, x, y, width, height, on_load=None, on_cancel=None):
        super().__init__(x, y, width, height, (40, 40, 50), (255, 255, 255), 2, 230)
        self.on_load = on_load
        self.on_cancel = on_cancel
        
        # マップリスト
        self.map_list = []
        self.selected_map = None
        
        # マップリストを取得
        self.load_map_list()
        
        self.setup_ui()
    
    def load_map_list(self):
        """マップリストを読み込み"""
        self.map_list = []
        
        # マップディレクトリのファイルをチェック
        map_dir = "maps"
        if os.path.exists(map_dir):
            for filename in os.listdir(map_dir):
                if filename.endswith(".json"):
                    map_path = os.path.join(map_dir, filename)
                    map_name = filename[:-5].replace("_", " ").title()
                    self.map_list.append((map_name, map_path))
    
    def setup_ui(self):
        """UI要素を設定"""
        # タイトル
        self.add_child(Label(self.width // 2, 20, "マップ読み込み", None, 30, (255, 255, 200), None, "center"))
        
        # マップリスト
        map_panel = ScrollPanel(20, 70, self.width - 40, self.height - 150, self.height, (50, 50, 60), (0, 0, 0), 1, 220)
        self.add_child(map_panel)
        self.map_panel = map_panel
        
        # マップリスト表示
        y_offset = 10
        for i, (map_name, map_path) in enumerate(self.map_list):
            map_btn = Button(10, y_offset, map_panel.width - 20, 30, map_name, None, 20,
                           (60, 60, 80), (255, 255, 255), (100, 100, 150),
                           (0, 0, 0), 1, lambda p=map_path: self.select_map(p))
            
            map_panel.add_child(map_btn)
            y_offset += 40
        
        map_panel.update_content_height()
        
        # 読み込みボタン
        load_btn = Button(self.width // 2 - 110, self.height - 60, 100, 40, "読み込み", None, 24,
                         (60, 100, 60), (255, 255, 255), (80, 150, 80),
                         (0, 0, 0), 1, self.load_map)
        self.add_child(load_btn)
        self.load_btn = load_btn
        self.load_btn.set_active(False)  # 初期状態では無効
        
        # キャンセルボタン
        cancel_btn = Button(self.width // 2 + 10, self.height - 60, 100, 40, "キャンセル", None, 24,
                          (100, 60, 60), (255, 255, 255), (150, 80, 80),
                          (0, 0, 0), 1, self.cancel)
        self.add_child(cancel_btn)
    
    def select_map(self, map_path):
        """マップを選択"""
        self.selected_map = map_path
        self.load_btn.set_active(True)
    
    def load_map(self):
        """マップを読み込む"""
        if self.selected_map and self.on_load:
            self.on_load(self.selected_map)
    
    def cancel(self):
        """読み込みをキャンセル"""
        if self.on_cancel:
            self.on_cancel()


# マップエディタの起動関数
def launch_map_editor(screen, character_creator=None, ui_manager=None):
    """マップエディタを起動する"""
    # マップエディタのインスタンスを作成
    map_editor = MapEditor(screen, character_creator, ui_manager)
    
    # 新規マップ作成ダイアログを表示
    show_new_map_dialog(map_editor, ui_manager)
    
    return map_editor


def show_new_map_dialog(map_editor, ui_manager):
    """新規マップ作成ダイアログを表示"""
    dialog = NewMapDialog(
        ui_manager.screen.get_width() // 2 - 200,
        ui_manager.screen.get_height() // 2 - 150,
        400, 300,
        on_create=lambda name, rows, cols: create_new_map(map_editor, name, rows, cols, dialog, ui_manager),
        on_cancel=lambda: ui_manager.remove_window(dialog)
    )
    
    ui_manager.add_window(dialog)


def create_new_map(map_editor, name, rows, cols, dialog, ui_manager):
    """新規マップを作成"""
    map_editor.create_new_map(name, rows, cols)
    ui_manager.remove_window(dialog)


def show_load_map_dialog(map_editor, ui_manager):
    """マップロードダイアログを表示"""
    dialog = LoadMapDialog(
        ui_manager.screen.get_width() // 2 - 200,
        ui_manager.screen.get_height() // 2 - 150,
        400, 300,
        on_load=lambda filepath: load_map(map_editor, filepath, dialog, ui_manager),
        on_cancel=lambda: ui_manager.remove_window(dialog)
    )
    
    ui_manager.add_window(dialog)


def load_map(map_editor, filepath, dialog, ui_manager):
    """マップを読み込む"""
    if map_editor.load_map(filepath):
        ui_manager.remove_window(dialog)