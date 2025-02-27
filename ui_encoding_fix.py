# ui_encoding_fix.py
import pygame
import os
import sys

def init_font_system():
    """日本語フォントを使用するための初期化を行う"""
    pygame.init()
    
    # OSの判定
    if sys.platform.startswith('win'):
        # Windowsの場合、メイリオなどのフォントを使用
        font_names = ['メイリオ', 'Yu Gothic', 'MS Gothic', 'MS UI Gothic', 'Arial']
    elif sys.platform.startswith('darwin'):
        # macOSの場合、ヒラギノなどのフォントを使用
        font_names = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Osaka', 'Arial']
    else:
        # Linuxなどの場合、さまざまなフォントを試す
        font_names = ['Noto Sans CJK JP', 'IPAGothic', 'VL Gothic', 'Droid Sans Japanese', 'Arial']
    
    # 使用可能な日本語フォントを探す
    available_fonts = pygame.font.get_fonts()
    system_font = None
    
    # 日本語フォントを探す
    for font_name in font_names:
        try:
            # Font関数はフォント名を小文字に変換して処理するため、
            # 元の名前と小文字バージョンの両方で試す
            font_lower = font_name.lower()
            if font_lower in available_fonts or font_name in available_fonts:
                test_font = pygame.font.Font(font_name, 24)
                # 日本語文字が描画できるかテスト
                test_render = test_font.render("日本語テスト", True, (0, 0, 0))
                if test_render.get_width() > 10:  # 正常に描画されていれば幅がある
                    system_font = font_name
                    break
        except:
            continue
    
    # 日本語フォントが見つからなかった場合、代替手段を試みる
    if system_font is None:
        # フォントファイルを直接指定する方法を試す（ファイルが存在する場合）
        font_paths = [
            "fonts/NotoSansCJKjp-Regular.ttf",  # プロジェクトにフォントファイルを追加した場合
            "fonts/meiryo.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    test_font = pygame.font.Font(path, 24)
                    test_render = test_font.render("日本語テスト", True, (0, 0, 0))
                    if test_render.get_width() > 10:
                        # カスタムフォントを使用
                        return {
                            'font_type': 'file',
                            'font_path': path
                        }
                except:
                    continue
    
    # 見つかった日本語フォントを返す
    return {
        'font_type': 'system',
        'font_name': system_font or 'Arial'  # 何も見つからなかった場合はArialを使用
    }

def create_font(size, font_info=None):
    """
    指定されたサイズと日本語対応フォント情報からフォントオブジェクトを作成
    
    Args:
        size: フォントサイズ
        font_info: フォント情報（init_font_system()の戻り値、Noneの場合は自動検出）
    
    Returns:
        pygame.font.Font: 日本語対応フォント
    """
    if font_info is None:
        font_info = init_font_system()
    
    if font_info['font_type'] == 'file':
        # フォントファイルを直接使用
        return pygame.font.Font(font_info['font_path'], size)
    else:
        # システムフォントを使用
        return pygame.font.Font(font_info['font_name'], size)

def create_ui_fonts(base_size=24):
    """
    UI用の標準フォントセットを作成
    
    Args:
        base_size: 基本フォントサイズ
        
    Returns:
        dict: さまざまなサイズのフォントを含む辞書
    """
    font_info = init_font_system()
    
    return {
        'small': create_font(int(base_size * 0.75), font_info),
        'normal': create_font(base_size, font_info),
        'large': create_font(int(base_size * 1.25), font_info),
        'title': create_font(int(base_size * 1.5), font_info),
        'header': create_font(int(base_size * 2), font_info)
    }

def patch_ui_system():
    """
    UI_systemモジュールの文字化け問題を修正するパッチ
    
    このメソッドを実行することで、既存のUIシステムを日本語対応にします。
    """
    from ui_system import Label, Button, Menu, Dialog
    
    # フォント情報の初期化
    font_info = init_font_system()
    
    # Label.__init__の元のメソッドを保存
    original_label_init = Label.__init__
    
    # Labelクラスを日本語対応に書き換え
    def new_label_init(self, x, y, text, font=None, font_size=24, 
                       color=(255, 255, 255), background_color=None, align="left"):
        # フォントが指定されていない場合は日本語対応フォントを使用
        if font is None:
            font = create_font(font_size, font_info)
        
        # 元のイニシャライザを呼び出し
        original_label_init(self, x, y, text, font, font_size, color, background_color, align)
    
    # Labelクラスのイニシャライザを差し替え
    Label.__init__ = new_label_init
    
    # Button.__init__の元のメソッドを保存
    original_button_init = Button.__init__
    
    # Buttonクラスを日本語対応に書き換え
    def new_button_init(self, x, y, width, height, text, font=None, font_size=24,
                        color=(128, 128, 128), text_color=(0, 0, 0),
                        hover_color=(255, 255, 255), border_color=(0, 0, 0),
                        border_width=1, callback=None):
        # フォントが指定されていない場合は日本語対応フォントを使用
        if font is None:
            font = create_font(font_size, font_info)
        
        # 元のイニシャライザを呼び出し
        original_button_init(self, x, y, width, height, text, font, font_size,
                             color, text_color, hover_color, border_color,
                             border_width, callback)
    
    # Buttonクラスのイニシャライザを差し替え
    Button.__init__ = new_button_init
    
    # Menu.__init__の元のメソッドを保存（あれば）
    if hasattr(Menu, '__init__'):
        original_menu_init = Menu.__init__
        
        # Menuクラスを日本語対応に書き換え
        def new_menu_init(self, x, y, width, item_height, items, callbacks=None,
                          color=(128, 128, 128), border_color=(0, 0, 0),
                          border_width=1, alpha=230, font=None, font_size=24):
            # フォントが指定されていない場合は日本語対応フォントを使用
            if font is None:
                font = create_font(font_size, font_info)
            
            # 元のイニシャライザを呼び出し
            original_menu_init(self, x, y, width, item_height, items, callbacks,
                              color, border_color, border_width, alpha, font, font_size)
        
        # Menuクラスのイニシャライザを差し替え
        Menu.__init__ = new_menu_init
    
    # Dialog.__init__の元のメソッドを保存（あれば）
    if hasattr(Dialog, '__init__'):
        original_dialog_init = Dialog.__init__
        
        # Dialogクラスを日本語対応に書き換え
        def new_dialog_init(self, x, y, width, height, title="", 
                            color=(128, 128, 128), border_color=(0, 0, 0),
                            border_width=2, alpha=230, font=None, font_size=24,
                            close_button=True):
            # フォントが指定されていない場合は日本語対応フォントを使用
            if font is None:
                font = create_font(font_size, font_info)
            
            # 元のイニシャライザを呼び出し
            original_dialog_init(self, x, y, width, height, title, 
                               color, border_color, border_width, alpha, 
                               font, font_size, close_button)
        
        # Dialogクラスのイニシャライザを差し替え
        Dialog.__init__ = new_dialog_init
    
    print("UI System has been patched for Japanese text support.")

def patch_renderer():
    """
    renderer.pyモジュールを日本語対応にするパッチ
    """
    try:
        from renderer import GameRenderer
        
        # フォント情報の初期化
        font_info = init_font_system()
        
        # GameRenderer.__init__の元のメソッドを保存
        original_renderer_init = GameRenderer.__init__
        
        # GameRendererクラスを日本語対応に書き換え
        def new_renderer_init(self, screen, game_manager):
            # 元のイニシャライザを呼び出し
            original_renderer_init(self, screen, game_manager)
            
            # フォントを日本語対応のものに差し替え
            self.font = create_font(24, font_info)
            self.small_font = create_font(18, font_info)
            self.title_font = create_font(28, font_info)
        
        # GameRendererクラスのイニシャライザを差し替え
        GameRenderer.__init__ = new_renderer_init
        
        print("Renderer has been patched for Japanese text support.")
    except ImportError:
        print("Renderer module not found, skipping patch.")

def patch_all():
    """
    すべてのUI関連モジュールを日本語対応にするパッチ
    """
    patch_ui_system()
    patch_renderer()
    
    # フォント情報を返す（他のモジュールでも使えるように）
    return init_font_system()

# エントリーポイントとして実行された場合
if __name__ == "__main__":
    font_info = patch_all()
    print(f"Japanese font support initialized: {font_info}")
