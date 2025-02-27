# font_manager.py
import pygame
import sys
import os

class FontManager:
    """日本語フォントを管理するシングルトンクラス"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FontManager._initialized:
            # 日本語フォントのパスを検索
            self.font_path = self._find_japanese_font()
            
            # フォントキャッシュ（サイズごとに保持）
            self.font_cache = {}
            
            FontManager._initialized = True
    
    def _find_japanese_font(self):
        """システムから日本語フォントを検索する"""
        font_paths = []
        
        # OSごとのデフォルトフォントパス
        if sys.platform.startswith('win'):
            # Windows
            font_paths = [
                os.path.join(os.environ['WINDIR'], 'Fonts', 'msgothic.ttc'),  # MS Gothic
                os.path.join(os.environ['WINDIR'], 'Fonts', 'meiryo.ttc'),    # Meiryo
                os.path.join(os.environ['WINDIR'], 'Fonts', 'yugothic.ttf')   # Yu Gothic
            ]
        elif sys.platform.startswith('darwin'):
            # macOS
            font_paths = [
                '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                '/System/Library/Fonts/AppleGothic.ttf',
                '/Library/Fonts/Osaka.ttf'
            ]
        else:
            # Linux/Unix
            font_paths = [
                '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
            ]
        
        # プロジェクト内のフォントを検索
        local_font_paths = [
            'fonts/NotoSansJP-Regular.otf',
            'fonts/meiryo.ttc',
            'fonts/msgothic.ttc',
            'fonts/yugothic.ttf'
        ]
        font_paths.extend(local_font_paths)
        
        # 見つかった最初のフォントを使用
        for path in font_paths:
            if os.path.exists(path):
                print(f"Japanese font found: {path}")
                return path
        
        # フォントが見つからない場合はNoneを返す（デフォルトフォント使用）
        print("Warning: No Japanese font found. Using default font.")
        return None
    
    def get_font(self, size):
        """指定サイズのフォントを取得（キャッシュから）"""
        if size not in self.font_cache:
            # フォントをキャッシュに追加
            self.font_cache[size] = pygame.font.Font(self.font_path, size)
        
        return self.font_cache[size]

# シングルトンインスタンスを作成
font_manager = FontManager()

def get_font(size):
    """指定サイズのフォントを取得するショートカット関数"""
    return font_manager.get_font(size)