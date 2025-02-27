# support_system.py
from typing import Dict, List, Tuple, Optional
import json
import os
from enum import Enum

class SupportLevel(Enum):
    """支援レベルを定義するクラス"""
    NONE = 0    # 支援なし
    C = 1       # Cランク
    B = 2       # Bランク
    A = 3       # Aランク
    S = 4       # Sランク（最大）

class SupportBonus:
    """支援効果を定義するクラス"""
    def __init__(self, 
                 damage_bonus: int = 0,      # 与ダメージボーナス
                 defense_bonus: int = 0,     # 受けダメージ軽減
                 hit_bonus: int = 0,         # 命中率ボーナス
                 avoid_bonus: int = 0):      # 回避率ボーナス
        self.damage_bonus = damage_bonus
        self.defense_bonus = defense_bonus
        self.hit_bonus = hit_bonus
        self.avoid_bonus = avoid_bonus
    
    def __add__(self, other):
        """複数の支援効果を加算できるようにする"""
        if not isinstance(other, SupportBonus):
            return self
        
        return SupportBonus(
            self.damage_bonus + other.damage_bonus,
            self.defense_bonus + other.defense_bonus,
            self.hit_bonus + other.hit_bonus,
            self.avoid_bonus + other.avoid_bonus
        )
    
    @classmethod
    def calculate_from_level(cls, level: SupportLevel):
        """支援レベルから標準的な支援効果を計算する"""
        level_value = level.value
        return cls(
            damage_bonus=level_value,             # レベル分のダメージ増加
            defense_bonus=level_value,            # レベル分のダメージ減少
            hit_bonus=level_value * 5,            # レベル×5の命中率上昇
            avoid_bonus=level_value * 5           # レベル×5の回避率上昇
        )

class SupportConversation:
    """支援会話を管理するクラス"""
    def __init__(self, 
                 characters: Tuple[str, str],         # 会話する2人のキャラクター
                 level: SupportLevel,                 # 支援レベル
                 title: str = "",                     # 会話タイトル
                 content: List[Dict] = None,          # 会話内容（辞書のリスト）
                 requirements: Dict = None,           # 会話の発生条件
                 viewed: bool = False):               # 既読フラグ
        self.characters = characters
        self.level = level
        self.title = title or f"{characters[0]}と{characters[1]}の{level.name}支援"
        self.content = content or []
        self.requirements = requirements or {"battles": 0}  # デフォルトは戦闘回数
        self.viewed = viewed
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（シリアライズ用）"""
        return {
            "characters": self.characters,
            "level": self.level.name,
            "title": self.title,
            "content": self.content,
            "requirements": self.requirements,
            "viewed": self.viewed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SupportConversation':
        """辞書からインスタンスを生成（デシリアライズ用）"""
        try:
            return cls(
                characters=tuple(data["characters"]),
                level=SupportLevel[data["level"]],
                title=data.get("title", ""),
                content=data.get("content", []),
                requirements=data.get("requirements", {"battles": 0}),
                viewed=data.get("viewed", False)
            )
        except (KeyError, ValueError) as e:
            print(f"支援会話データの読み込みエラー: {e}")
            return None

class SupportPair:
    """2人のキャラクター間の支援関係を管理するクラス"""
    def __init__(self, 
                 characters: Tuple[str, str],                 # 支援する2人のキャラクター
                 current_level: SupportLevel = SupportLevel.NONE,  # 現在の支援レベル
                 max_level: SupportLevel = SupportLevel.A,    # 最大支援レベル
                 points: int = 0,                             # 現在の支援ポイント
                 points_needed: Dict[SupportLevel, int] = None,  # 各レベルに必要なポイント
                 conversations: Dict[SupportLevel, SupportConversation] = None):  # 各レベルの会話
        self.characters = sorted(characters)  # 常にアルファベット順に保存
        self.current_level = current_level
        self.max_level = max_level
        self.points = points
        
        # 各レベルに必要なポイントの設定（デフォルト値）
        self.points_needed = points_needed or {
            SupportLevel.C: 20,
            SupportLevel.B: 60,
            SupportLevel.A: 120,
            SupportLevel.S: 200
        }
        
        # 支援会話の初期化
        self.conversations = conversations or {}
    
    def add_points(self, points: int) -> Tuple[bool, Optional[SupportLevel]]:
        """
        支援ポイントを追加し、レベルアップの有無を返す
        
        Args:
            points: 追加するポイント数
            
        Returns:
            Tuple[bool, Optional[SupportLevel]]: レベルアップしたかどうかとレベルアップ後のレベル
        """
        if self.current_level == self.max_level:
            return False, None  # 既に最大レベルに達している
        
        old_level = self.current_level
        self.points += points
        
        # 次のレベルを計算
        next_level = None
        for level in [SupportLevel.C, SupportLevel.B, SupportLevel.A, SupportLevel.S]:
            if level.value > self.current_level.value and level.value <= self.max_level.value:
                if self.points >= self.points_needed[level]:
                    next_level = level
                break
        
        # レベルアップ処理
        if next_level and next_level.value > self.current_level.value:
            self.current_level = next_level
            return True, next_level
        
        return False, None
    
    def get_next_required_points(self) -> int:
        """次のレベルに必要な残りポイント数を取得"""
        if self.current_level == self.max_level:
            return 0
        
        # 次のレベルを特定
        next_level = None
        for level in [SupportLevel.C, SupportLevel.B, SupportLevel.A, SupportLevel.S]:
            if level.value > self.current_level.value and level.value <= self.max_level.value:
                next_level = level
                break
        
        if not next_level:
            return 0
        
        return max(0, self.points_needed[next_level] - self.points)
    
    def has_available_conversation(self) -> bool:
        """未読の支援会話があるかどうか"""
        return (self.current_level in self.conversations and 
                not self.conversations[self.current_level].viewed)
    
    def get_conversation(self, level: SupportLevel = None) -> Optional[SupportConversation]:
        """指定レベルの支援会話を取得（レベル未指定の場合は現在のレベル）"""
        level = level or self.current_level
        return self.conversations.get(level)
    
    def mark_conversation_viewed(self, level: SupportLevel = None):
        """支援会話を既読にする"""
        level = level or self.current_level
        if level in self.conversations:
            self.conversations[level].viewed = True
    
    def get_support_bonus(self) -> SupportBonus:
        """現在のレベルに基づいた支援効果を取得"""
        return SupportBonus.calculate_from_level(self.current_level)
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（シリアライズ用）"""
        return {
            "characters": self.characters,
            "current_level": self.current_level.name,
            "max_level": self.max_level.name,
            "points": self.points,
            "points_needed": {level.name: points for level, points in self.points_needed.items()},
            "conversations": {level.name: conv.to_dict() for level, conv in self.conversations.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SupportPair':
        """辞書からインスタンスを生成（デシリアライズ用）"""
        try:
            # ポイント必要数の変換
            points_needed = {}
            for level_name, points in data.get("points_needed", {}).items():
                try:
                    level = SupportLevel[level_name]
                    points_needed[level] = points
                except KeyError:
                    continue
            
            # 会話の変換
            conversations = {}
            for level_name, conv_data in data.get("conversations", {}).items():
                try:
                    level = SupportLevel[level_name]
                    conv = SupportConversation.from_dict(conv_data)
                    if conv:
                        conversations[level] = conv
                except KeyError:
                    continue
            
            return cls(
                characters=tuple(data["characters"]),
                current_level=SupportLevel[data.get("current_level", "NONE")],
                max_level=SupportLevel[data.get("max_level", "A")],
                points=data.get("points", 0),
                points_needed=points_needed,
                conversations=conversations
            )
        except (KeyError, ValueError) as e:
            print(f"支援ペアデータの読み込みエラー: {e}")
            return None

class SupportSystem:
    """全ユニットの支援関係を管理するクラス"""
    def __init__(self, data_path: str = "data/supports/"):
        self.data_path = data_path
        self.supports = {}  # キャラクターペアをキーとした支援ペアの辞書
        self.battle_counts = {}  # キャラクターペアをキーとした戦闘回数の辞書
        
        # データディレクトリの確認
        os.makedirs(data_path, exist_ok=True)
        
        # 支援会話データの読み込み
        self.load_support_data()
    
    def get_support_pair_key(self, char1: str, char2: str) -> str:
        """2人のキャラクターから辞書キーを生成（常にアルファベット順）"""
        return "_".join(sorted([char1, char2]))
    
    def get_support_pair(self, char1: str, char2: str) -> Optional[SupportPair]:
        """2人のキャラクター間の支援ペアを取得"""
        key = self.get_support_pair_key(char1, char2)
        return self.supports.get(key)
    
    def register_support_pair(self, char1: str, char2: str, max_level: SupportLevel = SupportLevel.A) -> SupportPair:
        """新しい支援ペアを登録"""
        key = self.get_support_pair_key(char1, char2)
        if key not in self.supports:
            self.supports[key] = SupportPair(
                characters=(char1, char2),
                max_level=max_level
            )
        return self.supports[key]
    
    def add_support_points(self, char1: str, char2: str, points: int) -> Tuple[bool, Optional[SupportLevel]]:
        """2人のキャラクター間の支援ポイントを追加"""
        pair = self.get_support_pair(char1, char2)
        if not pair:
            return False, None
        
        return pair.add_points(points)
    
    def record_battle_together(self, char1: str, char2: str):
        """2人のキャラクターが同じマップで戦闘したことを記録"""
        key = self.get_support_pair_key(char1, char2)
        
        # 支援ペアがない場合はスキップ
        if key not in self.supports:
            return
        
        # 戦闘回数を増加
        self.battle_counts[key] = self.battle_counts.get(key, 0) + 1
        
        # 一定回数戦闘するとポイント増加
        if self.battle_counts[key] % 5 == 0:  # 5戦闘ごとにポイント獲得
            self.add_support_points(char1, char2, 5)
    
    def record_adjacent_turns(self, char1: str, char2: str):
        """2人のキャラクターが隣接してターンを終了したことを記録"""
        key = self.get_support_pair_key(char1, char2)
        
        # 支援ペアがない場合はスキップ
        if key not in self.supports:
            return
        
        # 隣接してターン終了するとポイント増加
        self.add_support_points(char1, char2, 1)
    
    def get_available_conversations(self) -> List[Tuple[str, str, SupportLevel]]:
        """閲覧可能な支援会話のリストを取得"""
        available = []
        
        for key, pair in self.supports.items():
            if pair.has_available_conversation():
                char1, char2 = pair.characters
                available.append((char1, char2, pair.current_level))
        
        return available
    
    def get_conversation(self, char1: str, char2: str, level: Optional[SupportLevel] = None) -> Optional[SupportConversation]:
        """指定したキャラクターとレベルの支援会話を取得"""
        pair = self.get_support_pair(char1, char2)
        if not pair:
            return None
        
        return pair.get_conversation(level)
    
    def mark_conversation_viewed(self, char1: str, char2: str, level: Optional[SupportLevel] = None):
        """支援会話を既読にする"""
        pair = self.get_support_pair(char1, char2)
        if pair:
            pair.mark_conversation_viewed(level)
    
    def get_support_bonus(self, unit, game_map) -> SupportBonus:
        """
        ユニットが受ける全支援効果を計算
        
        Args:
            unit: 対象ユニット
            game_map: ゲームマップ
            
        Returns:
            SupportBonus: 適用される総合的な支援効果
        """
        total_bonus = SupportBonus()
        
        # 指定ユニットと支援関係があるユニットを探す
        for key, pair in self.supports.items():
            # 支援レベルがNONEの場合はスキップ
            if pair.current_level == SupportLevel.NONE:
                continue
            
            # このペアに指定ユニットが含まれるか確認
            if unit.name not in pair.characters:
                continue
            
            # もう一方のキャラクターを特定
            other_name = pair.characters[0] if pair.characters[1] == unit.name else pair.characters[1]
            
            # マップ上で相手を探す
            other_unit = None
            for u in game_map.units:
                if u.name == other_name and not u.is_dead():
                    other_unit = u
                    break
            
            if not other_unit:
                continue
            
            # 距離を計算
            distance = abs(unit.x - other_unit.x) + abs(unit.y - other_unit.y)
            
            # 3マス以内なら支援効果を適用
            if distance <= 3:
                total_bonus += pair.get_support_bonus()
        
        return total_bonus
    
    def apply_support_effects(self, attacker, defender, combat_data, game_map):
        """
        戦闘時に支援効果を適用する
        
        Args:
            attacker: 攻撃側ユニット
            defender: 防御側ユニット
            combat_data: 戦闘データ（修正用）
            game_map: ゲームマップ
        """
        # 攻撃側の支援効果
        attacker_bonus = self.get_support_bonus(attacker, game_map)
        
        # 防御側の支援効果
        defender_bonus = self.get_support_bonus(defender, game_map)
        
        # 戦闘データに効果を適用
        # 与ダメージボーナス
        combat_data["damage_modifier"] = combat_data.get("damage_modifier", 0) + attacker_bonus.damage_bonus
        
        # 受けダメージ軽減
        combat_data["damage_reduction"] = combat_data.get("damage_reduction", 0) + defender_bonus.defense_bonus
        
        # 命中率ボーナス
        combat_data["hit_modifier"] = combat_data.get("hit_modifier", 0) + attacker_bonus.hit_bonus
        
        # 回避率ボーナス
        combat_data["avoid_modifier"] = combat_data.get("avoid_modifier", 0) + defender_bonus.avoid_bonus
    
    def load_support_data(self):
        """支援データをファイルから読み込む"""
        # 支援ペアファイル
        pairs_file = os.path.join(self.data_path, "support_pairs.json")
        
        # ファイルが存在する場合は読み込み
        if os.path.exists(pairs_file):
            try:
                with open(pairs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 支援ペアの復元
                    for key, pair_data in data.get("supports", {}).items():
                        pair = SupportPair.from_dict(pair_data)
                        if pair:
                            self.supports[key] = pair
                    
                    # 戦闘回数の復元
                    self.battle_counts = data.get("battle_counts", {})
            except Exception as e:
                print(f"支援データの読み込みエラー: {e}")
    
    def save_support_data(self):
        """支援データをファイルに保存"""
        # 支援ペアファイル
        pairs_file = os.path.join(self.data_path, "support_pairs.json")
        
        try:
            # 保存用データの準備
            data = {
                "supports": {key: pair.to_dict() for key, pair in self.supports.items()},
                "battle_counts": self.battle_counts
            }
            
            # ファイルに保存
            with open(pairs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"支援データの保存エラー: {e}")
    
    def register_default_supports(self, character_data: List[Dict]):
        """
        キャラクターデータから初期支援関係を登録
        
        Args:
            character_data: キャラクター情報の辞書リスト。各辞書には少なくとも
                           'name'キーと'supports'キー（対応キャラクターリスト）が必要
        """
        for char_info in character_data:
            char_name = char_info.get('name')
            supports = char_info.get('supports', [])
            
            for support_info in supports:
                other_name = support_info.get('character')
                max_level_name = support_info.get('max_level', 'A')
                
                try:
                    max_level = SupportLevel[max_level_name]
                except KeyError:
                    max_level = SupportLevel.A
                
                # 支援ペアの登録
                self.register_support_pair(char_name, other_name, max_level)
                
                # 支援会話の登録（各レベル用）
                self._register_conversation(char_name, other_name, SupportLevel.C, 
                                          support_info.get('c_conv'))
                self._register_conversation(char_name, other_name, SupportLevel.B, 
                                          support_info.get('b_conv'))
                self._register_conversation(char_name, other_name, SupportLevel.A, 
                                          support_info.get('a_conv'))
                self._register_conversation(char_name, other_name, SupportLevel.S, 
                                          support_info.get('s_conv'))
    
    def _register_conversation(self, char1: str, char2: str, level: SupportLevel, conv_data: Dict = None):
        """特定レベルの支援会話を登録"""
        if not conv_data:
            return
        
        pair = self.get_support_pair(char1, char2)
        if not pair or level.value > pair.max_level.value:
            return
        
        # 会話の作成
        conversation = SupportConversation(
            characters=(char1, char2),
            level=level,
            title=conv_data.get('title', ''),
            content=conv_data.get('content', []),
            requirements=conv_data.get('requirements', {'battles': 0})
        )
        
        # 会話の登録
        pair.conversations[level] = conversation