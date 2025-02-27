# main.py (修正版)
import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from game_state_manager import GameStateManager, GameState
from title_screen import TitleScreen
from town_screen import TownScreen
from scenario_select_screen import ScenarioSelectScreen
from game_manager import GameManager
from renderer import GameRenderer
from ui_system import UIManager
from level_sync_manager import LevelSyncManager
from save_system import SaveSystem
from dialogue_system import DialogueScreen

def main():
    pygame.init()
    
    # ui_encoding_fix.pyは使わない
    # 代わりにフォントマネージャーを初期化
    from font_manager import font_manager
    print(f"Japanese font initialized: {font_manager.font_path}")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ファイアーエムブレム風SRPG")
    clock = pygame.time.Clock()
    
    # ゲームステートマネージャーの初期化
    state_manager = GameStateManager()
    
    # ゲームマネージャーの初期化（マップ戦闘用）
    game_manager = None
    
    # レベルシンクマネージャーの初期化
    from growth_system import GrowthSystem
    growth_system = GrowthSystem()
    level_sync_manager = LevelSyncManager(growth_system)
    
    # セーブシステムの初期化
    save_system = SaveSystem()
    
    # 現在表示している画面のUIエレメント
    current_screen = None
    
    # タイトル画面の作成
    def show_title_screen():
        nonlocal current_screen
        title_screen = TitleScreen(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 
                                  on_new_game=start_new_game,
                                  on_continue=continue_game,
                                  on_options=show_options)
        current_screen = title_screen
    
    # 新規ゲームの開始
    def start_new_game():
        nonlocal game_manager, current_screen
        # ゲームの初期化
        state_manager.initialize_new_game()
        
        # 最初の街画面を表示
        show_town_screen()
    
    # ゲームのロード
    def continue_game():
        # セーブデータ選択画面を表示（未実装）
        pass
    
    # オプション画面の表示
    # main.py (修正版の続き)
    def show_options():
        # オプション画面の表示（未実装）
        pass
    
    # 街画面の表示
    def show_town_screen():
        nonlocal current_screen
        state_manager.change_state(GameState.TOWN)
        town_screen = TownScreen(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, state_manager, on_leave_town=show_scenario_select)
        current_screen = town_screen
    
    # シナリオ選択画面の表示
    def show_scenario_select():
        nonlocal current_screen
        state_manager.change_state(GameState.SCENARIO_SELECT)
        
        # シナリオデータの取得（実際のゲームではデータベースなどから）
        scenarios = [
            {
                "id": "scenario1",
                "name": "始まりの章 - 平和な村",
                "description": "冒険の始まり。平和だった村が魔物に襲われ...",
                "recommended_level": 1,
                "maps": ["map1", "map2", "map3"],
                "pre_dialogue": "dialogue1_pre",
                "post_dialogue": "dialogue1_post"
            },
            {
                "id": "scenario2",
                "name": "第2章 - 古代遺跡の謎",
                "description": "村の長老から古代遺跡についての話を聞き...",
                "recommended_level": 5,
                "maps": ["map4", "map5"],
                "pre_dialogue": "dialogue2_pre",
                "post_dialogue": "dialogue2_post"
            },
            {
                "id": "scenario3",
                "name": "第3章 - 王都の陰謀",
                "description": "遺跡で見つけた古文書を解読するため王都へ...",
                "recommended_level": 10,
                "maps": ["map6", "map7", "map8"],
                "pre_dialogue": "dialogue3_pre",
                "post_dialogue": "dialogue3_post"
            }
        ]
        
        scenario_select = ScenarioSelectScreen(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, scenarios, 
                                              on_select=start_scenario,
                                              on_back=show_town_screen)
        current_screen = scenario_select
    
    # シナリオの開始
    def start_scenario(scenario):
        nonlocal game_manager
        state_manager.current_scenario = scenario
        state_manager.current_map_index = 0
        
        # マップ前の会話があれば表示
        if "pre_dialogue" in scenario and scenario["pre_dialogue"]:
            show_pre_map_dialogue(scenario)
        else:
            apply_level_sync(scenario)
    
    # マップ前の会話表示
    def show_pre_map_dialogue(scenario):
        nonlocal current_screen
        state_manager.change_state(GameState.PRE_MAP_DIALOGUE)
        
        # 会話データの取得（実際のゲームではデータベースなどから）
        dialogue_id = scenario["pre_dialogue"]
        dialogue_data = get_dialogue_data(dialogue_id)
        
        dialogue_screen = DialogueScreen(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, dialogue_data, 
                                        on_complete=lambda: apply_level_sync(scenario))
        current_screen = dialogue_screen
    
    # レベルシンクの適用
    def apply_level_sync(scenario):
        nonlocal game_manager
        state_manager.change_state(GameState.LEVEL_SYNC)
        
        # パーティーのユニットにレベルシンクを適用
        units = state_manager.game_data.get("party", [])
        map_id = scenario["maps"][state_manager.current_map_index]
        synced_units = level_sync_manager.apply_level_sync(units, map_id)
        
        # レベルシンク情報の表示（任意）
        
        # マップの開始
        start_map(scenario, map_id)
    
    # マップの開始
    def start_map(scenario, map_id):
        nonlocal game_manager, current_screen
        state_manager.change_state(GameState.MAP)
        
        # マップの初期化
        from map import GameMap
        game_map = GameMap(10, 15)  # 仮のサイズ
        
        # マップのセットアップ（実際のゲームではマップデータに基づく）
        from setup import setup_game
        setup_game(game_map)
        
        # ゲームマネージャーの初期化
        game_manager = GameManager(game_map)
        
        # レンダラーの初期化
        renderer = GameRenderer(screen, game_manager)
        
        # UIマネージャーの初期化
        ui_manager = UIManager(screen, game_manager)
        
        # マップループ（独自のループが必要）
        map_running = True
        while map_running and state_manager.current_state == GameState.MAP:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # UIマネージャーにイベントを渡す
                if ui_manager.handle_event(event):
                    continue
                
                # 戦闘中でない場合の入力処理
                if not game_manager.combat_animation_active:
                    if event.type == pygame.KEYDOWN:
                        # Escキーでマップを中断（オプション表示など）
                        if event.key == pygame.K_ESCAPE:
                            # マップ中断メニューの表示（未実装）
                            pass
                        
                        # ターン終了キー
                        elif event.key == pygame.K_e and game_manager.turn_player == 0:
                            game_manager.end_player_turn()
                            # 敵のターン実行
                            game_manager.execute_ai_turn()
            
            # ゲームの状態更新
            ui_manager.update()
            
            # マップクリア判定
            if check_map_clear():
                map_running = False
                finish_map(scenario)
                break
            
            # ゲームオーバー判定
            if check_game_over():
                map_running = False
                show_game_over()
                break
            
            # 描画処理
            renderer.render_map()
            renderer.render_units()
            ui_manager.render()
            
            pygame.display.flip()
            clock.tick(60)
    
    # マップクリア判定
    def check_map_clear():
        # マップクリア条件をチェック（実際のゲームではより複雑な判定）
        if game_manager:
            # 例：敵がすべて倒されたか判定
            enemies = [unit for unit in game_manager.game_map.units if unit.team == 1 and not unit.is_dead()]
            return len(enemies) == 0
        return False
    
    # ゲームオーバー判定
    def check_game_over():
        """ゲームオーバー判定"""
        # ゲームオーバー条件をチェック
        if game_manager:
            # 例：主人公が倒されたか判定
            # 以前のコード: hero = next((unit for unit in game_manager.game_map.units if unit.team == 0 and unit.is_hero), None)
            
            # 修正1: hasattr でis_hero属性があるか確認
            hero = next((unit for unit in game_manager.game_map.units 
                        if unit.team == 0 and hasattr(unit, 'is_hero') and unit.is_hero), None)
            
            # 修正2: 代替として、名前で主人公を特定
            if hero is None:
                hero = next((unit for unit in game_manager.game_map.units 
                            if unit.team == 0 and unit.name == "Marth"), None)  # または主人公の名前に変更
            
            return hero and hero.is_dead()
        return False
    
    # マップ終了時の処理
    def finish_map(scenario):
        # マップ後の会話があれば表示
        if "post_dialogue" in scenario and scenario["post_dialogue"]:
            show_post_map_dialogue(scenario)
        else:
            process_map_rewards()
    
    # マップ後の会話表示
    def show_post_map_dialogue(scenario):
        nonlocal current_screen
        state_manager.change_state(GameState.POST_MAP_DIALOGUE)
        
        # 会話データの取得
        dialogue_id = scenario["post_dialogue"]
        dialogue_data = get_dialogue_data(dialogue_id)
        
        dialogue_screen = DialogueScreen(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, dialogue_data, 
                                        on_complete=process_map_rewards)
        current_screen = dialogue_screen
    
    # マップクリア後の報酬処理
    def process_map_rewards():
        state_manager.change_state(GameState.LEVEL_UP_PROCESSING)
        
        # レベルシンクの解除
        units = state_manager.game_data.get("party", [])
        level_sync_manager.remove_level_sync(units)
        
        # 経験値の適用とレベルアップ処理
        level_up_results = level_sync_manager.apply_pending_exp(units, growth_system)
        
        # レベルアップ画面の表示（未実装）
        
        # 次のマップがあれば次へ、なければシナリオ終了
        move_to_next_map_or_finish()
    
    # 次のマップへ移動またはシナリオ終了
    def move_to_next_map_or_finish():
        scenario = state_manager.current_scenario
        state_manager.current_map_index += 1
        
        # まだマップが残っている場合
        if state_manager.current_map_index < len(scenario["maps"]):
            # 次のマップへ
            apply_level_sync(scenario)
        else:
            # シナリオ終了、セーブして街へ戻る
            show_save_screen()
    
    # セーブ画面の表示
    def show_save_screen():
        state_manager.change_state(GameState.SAVE)
        
        # セーブ画面の表示（未実装）
        
        # 仮の実装：すぐに街へ戻る
        show_town_screen()
    
    # ゲームオーバー画面の表示
    def show_game_over():
        # ゲームオーバー画面の表示（未実装）
        
        # 仮の実装：タイトルに戻る
        show_title_screen()
    
    # 会話データの取得
    def get_dialogue_data(dialogue_id):
        # 実際のゲームではデータベースやファイルから取得
        dialogue_data = {
            "dialogue1_pre": [
                {"speaker": "村長", "text": "最近、村の周辺で魔物の出現が増えている。調査してほしい。", "left_character": "村長", "right_character": "主人公"},
                {"speaker": "主人公", "text": "了解しました。私たちに任せてください。", "left_character": "村長", "right_character": "主人公"}
            ],
            "dialogue1_post": [
                {"speaker": "主人公", "text": "村周辺の魔物は退治しました。", "left_character": "村長", "right_character": "主人公"},
                {"speaker": "村長", "text": "ありがとう。しかし、これは何かの前触れかもしれない...", "left_character": "村長", "right_character": "主人公"}
            ]
        }
        
        return dialogue_data.get(dialogue_id, [])
    
    # 最初にタイトル画面を表示
    show_title_screen()
    
    # メインゲームループ
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 現在の画面にイベントを渡す
            if current_screen:
                current_screen.handle_event(event)
        
        # 画面の更新
        if current_screen:
            current_screen.update()
        
        # 画面の描画
        screen.fill((0, 0, 0))  # 背景をクリア
        if current_screen:
            current_screen.render(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()