# renderer.py
import pygame
from constants import GRID_SIZE, COLOR_BLACK, COLOR_WHITE, COLOR_BLUE, COLOR_RED
from constants import COLOR_GREEN, COLOR_YELLOW, TerrainType
from font_manager import get_font  # フォントマネージャーをインポート

class GameRenderer:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.game_manager = game_manager
        
        # フォントマネージャーから日本語フォントを取得
        self.font = get_font(24)
        self.small_font = get_font(20)
        self.large_font = get_font(28)
        
        # テクスチャ用のダミーカラー
        self.terrain_colors = {
            TerrainType.PLAIN: (200, 200, 100),
            TerrainType.FOREST: (50, 150, 50),
            TerrainType.MOUNTAIN: (150, 100, 50),
            TerrainType.WATER: (50, 100, 200),
            TerrainType.WALL: (100, 100, 100),
        }
        
        self.team_colors = {
            0: COLOR_BLUE,  # プレイヤー
            1: COLOR_RED,   # 敵
        }
        
        # アニメーション関連
        self.animation_timer = 0
        self.animation_frame = 0
        self.max_animation_frames = 60
    
    def render(self):
        """従来の完全な描画（UI連携後は主に下位メソッドを使用）"""
        self.screen.fill(COLOR_BLACK)
        
        # マップの描画
        self.render_map()
        
        # 選択中のユニットの移動範囲
        self._render_movement_range()
        
        # 攻撃範囲
        self._render_attack_range()
        
        # ユニットの描画
        self.render_units()
        
        # 選択中のユニットのハイライト
        self._render_selected_unit()
        
        # UIの描画
        self._render_ui()
        
        # 戦闘アニメーション
        if self.game_manager.combat_animation_active:
            self._render_combat_animation()
    
    def render_map(self):
        """マップのみ描画（UIシステムと連携するために分離）"""
        self.screen.fill(COLOR_BLACK)
        
        game_map = self.game_manager.game_map
        
        for y in range(game_map.rows):
            for x in range(game_map.cols):
                terrain = game_map.tiles[y][x].terrain_type
                color = self.terrain_colors.get(terrain, COLOR_BLACK)
                
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_BLACK, rect, 1)  # グリッド線
    
    def render_units(self):
        """ユニットのみ描画（UIシステムと連携するために分離）"""
        for unit in self.game_manager.game_map.units:
            if unit.is_dead():
                continue
                
            color = self.team_colors.get(unit.team, COLOR_WHITE)
            x, y = unit.x * GRID_SIZE, unit.y * GRID_SIZE
            
            # ユニットの描画（簡易的な円）
            pygame.draw.circle(self.screen, color, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), GRID_SIZE // 2 - 2)
            
            # HPバー
            hp_ratio = unit.current_hp / unit.max_hp
            hp_color = COLOR_GREEN if hp_ratio > 0.5 else COLOR_YELLOW if hp_ratio > 0.25 else COLOR_RED
            hp_width = int(GRID_SIZE * hp_ratio)
            pygame.draw.rect(self.screen, hp_color, (x, y + GRID_SIZE - 5, hp_width, 5))
            
            # 既に行動済みのユニットは暗く表示
            if unit.has_moved:
                s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                s.fill((0, 0, 0, 128))  # 半透明ブラック
                self.screen.blit(s, (x, y))
    
    def _render_movement_range(self):
        """移動範囲を描画"""
        if self.game_manager.phase == "move_unit" and self.game_manager.move_targets:
            for x, y in self.game_manager.move_targets:
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                s.fill((0, 0, 255, 128))  # 半透明ブルー
                self.screen.blit(s, (x * GRID_SIZE, y * GRID_SIZE))
    
    def _render_attack_range(self):
        """攻撃範囲を描画"""
        if self.game_manager.phase == "select_attack_target" and self.game_manager.attack_targets:
            for x, y in self.game_manager.attack_targets:
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                s.fill((255, 0, 0, 128))  # 半透明レッド
                self.screen.blit(s, (x * GRID_SIZE, y * GRID_SIZE))
    
    def _render_selected_unit(self):
        """選択中のユニットをハイライト表示"""
        if self.game_manager.selected_unit:
            unit = self.game_manager.selected_unit
            x, y = unit.x * GRID_SIZE, unit.y * GRID_SIZE
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, COLOR_YELLOW, rect, 2)
    
    def _render_ui(self):
        """基本的なUI要素を描画"""
        # 現在のターンとフェーズの表示
        turn_text = f"ターン {self.game_manager.current_turn+1} - {'プレイヤー' if self.game_manager.turn_player == 0 else '敵'}"
        turn_surface = self.font.render(turn_text, True, COLOR_WHITE)
        self.screen.blit(turn_surface, (10, self.screen.get_height() - 30))
        
        # 選択中のユニット情報
        if self.game_manager.selected_unit:
            unit = self.game_manager.selected_unit
            unit_text = f"{unit.name} - HP: {unit.current_hp}/{unit.max_hp}"
            unit_surface = self.font.render(unit_text, True, COLOR_WHITE)
            self.screen.blit(unit_surface, (self.screen.get_width() - 200, self.screen.get_height() - 30))
            
            # スキルリストの表示
            if hasattr(unit, 'skills') and unit.skills:
                y_offset = 60
                skill_title_surface = self.font.render("スキル:", True, COLOR_WHITE)
                self.screen.blit(skill_title_surface, (self.screen.get_width() - 200, y_offset))
                
                for i, skill in enumerate(unit.skills):
                    skill_surface = self.font.render(f"- {skill.name}", True, COLOR_WHITE)
                    self.screen.blit(skill_surface, (self.screen.get_width() - 190, y_offset + 20 + i * 20))
        
        # フェーズに応じたメッセージ
        phase_messages = {
            "select_unit": "ユニットを選択",
            "move_unit": "移動先を選択",
            "select_action": "行動を選択: [A]攻撃 or [W]待機",
            "select_attack_target": "攻撃対象を選択"
        }
        
        phase_text = phase_messages.get(self.game_manager.phase, "")
        phase_surface = self.font.render(phase_text, True, COLOR_WHITE)
        self.screen.blit(phase_surface, (10, 10))
    
    def _render_combat_animation(self):
        """戦闘アニメーションを描画（日本語対応）"""
        if not self.game_manager.combat_results:
            return
            
        # アニメーションの進行を更新
        self.animation_timer += 1
        if self.animation_timer % 3 == 0:  # 3フレームごとに進める
            self.animation_frame += 1
        
        # 戦闘結果を取得
        results = self.game_manager.combat_results
        attacker = results["attacker_unit"]
        defender = results["defender_unit"]
        
        # 背景を暗くする
        s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        s.fill((0, 0, 0, 192))
        self.screen.blit(s, (0, 0))
        
        # 戦闘ウィンドウの表示
        window_rect = pygame.Rect(50, 50, self.screen.get_width() - 100, self.screen.get_height() - 100)
        pygame.draw.rect(self.screen, COLOR_WHITE, window_rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, window_rect, 2)
        
        # 攻撃者と防御者の情報
        attacker_text = f"{attacker.name}: HP {attacker.current_hp}/{attacker.max_hp}"
        defender_text = f"{defender.name}: HP {defender.current_hp}/{defender.max_hp}"
        
        # 日本語対応フォントでテキストをレンダリング
        attacker_surface = self.font.render(attacker_text, True, COLOR_BLACK)
        defender_surface = self.font.render(defender_text, True, COLOR_BLACK)
        
        # テキストの表示
        self.screen.blit(attacker_surface, (70, 70))
        self.screen.blit(defender_surface, (70, 100))
        
        # 戦闘結果の表示（段階的に表示）
        y_offset = 140
        
        # アニメーションフレーム数に基づいて表示内容を制御
        if self.animation_frame >= 10:  # 攻撃側の結果を表示
            for i, result in enumerate(results["attacker_results"]):
                # 後から表示される分はフレーム数チェック
                if i > 0 and self.animation_frame < 25:
                    continue
                    
                hit_text = "命中" if result["hit"] else "ミス"
                crit_text = "会心!" if result["critical"] else ""
                damage_text = f"{hit_text} {crit_text} ダメージ: {result['damage']}"
                
                result_surface = self.font.render(damage_text, True, COLOR_BLUE)
                self.screen.blit(result_surface, (70, y_offset + i * 30))
        
        if self.animation_frame >= 25:  # 防御側の結果を表示
            y_offset += len(results["attacker_results"]) * 30 + 10
            for i, result in enumerate(results["defender_results"]):
                hit_text = "命中" if result["hit"] else "ミス"
                crit_text = "会心!" if result["critical"] else ""
                damage_text = f"{hit_text} {crit_text} ダメージ: {result['damage']}"
                
                result_surface = self.font.render(damage_text, True, COLOR_RED)
                self.screen.blit(result_surface, (70, y_offset + i * 30))
        
        # スキル発動情報の表示
        if self.animation_frame >= 40 and "activated_skills" in results:
            activated_skills = results["activated_skills"]
            
            attacker_skills = activated_skills.get("attacker", [])
            defender_skills = activated_skills.get("defender", [])
            
            # スキル発動テキスト表示
            y_offset += len(results["defender_results"]) * 30 + 10
            if attacker_skills:
                attacker_name = attacker.name
                skill_text = f"{attacker_name}のスキル発動: {', '.join(attacker_skills)}"
                skill_surface = self.font.render(skill_text, True, COLOR_BLUE)
                self.screen.blit(skill_surface, (70, y_offset))
                y_offset += 25
            
            if defender_skills:
                defender_name = defender.name
                skill_text = f"{defender_name}のスキル発動: {', '.join(defender_skills)}"
                skill_surface = self.font.render(skill_text, True, COLOR_RED)
                self.screen.blit(skill_surface, (70, y_offset))
        
        # 続行ボタンの表示（アニメーション終了後）
        if self.animation_frame >= 50:
            continue_text = "クリックで続行"
            continue_surface = self.font.render(continue_text, True, COLOR_BLACK)
            continue_rect = continue_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 100))
            self.screen.blit(continue_surface, continue_rect)
            
            # 点滅効果
            if self.animation_timer % 60 < 30:
                pygame.draw.rect(self.screen, COLOR_YELLOW, continue_rect.inflate(10, 5), 2)
        
        # 戦闘アニメーションを終了
        if self.animation_frame >= self.max_animation_frames or pygame.mouse.get_pressed()[0]:
            self.game_manager.combat_animation_active = False
            self.game_manager.combat_results = None
            self.animation_timer = 0
            self.animation_frame = 0
    
    def handle_combat_animation_click(self):
        """戦闘アニメーション中のクリック処理"""
        # アニメーションを早送り
        if self.animation_frame < 50:
            self.animation_frame = 50
        else:
            # アニメーション終了
            self.game_manager.combat_animation_active = False
            self.game_manager.combat_results = None
            self.animation_timer = 0
            self.animation_frame = 0