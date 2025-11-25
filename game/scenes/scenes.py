"""
씬 시스템 - TitleScene, IntroScene, TutorialScene, MazeScene, EndingScene
"""

import pygame
import random
from game.core import config
from game.systems import player
from game.systems import maze
from game.systems import camera
from game.ui import ui
from game.logic import endings
from game.logic import achievements
from game.systems import merchant
from game.systems import items

class Scene:
    """씬 베이스 클래스"""
    def __init__(self, game):
        self.game = game
        self.resources = game.resources
    
    def update(self, dt):
        """씬 업데이트"""
        pass
    
    def render(self, screen):
        """씬 렌더링"""
        pass
    
    def handle_event(self, event):
        """이벤트 처리"""
        pass

class TitleScene(Scene):
    """타이틀 씬"""
    def __init__(self, game):
        super().__init__(game)
        self.selected_index = 0
        self.menu_items = [
            "일반 모드",
            "도전 모드",
            "기록/도전과제",
            "설정",
            "종료"
        ]
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.selected_index == 0:  # 일반 모드
                    self.game.stats = player.GameStats()
                    self.game.stats.difficulty = config.DIFFICULTY_NORMAL
                    self.game.stats.mode = "normal"
                    self.game.change_scene(IntroScene(self.game))
                elif self.selected_index == 1:  # 도전 모드
                    self.game.change_scene(ChallengeSelectScene(self.game))
                elif self.selected_index == 2:  # 기록/도전과제
                    self.game.change_scene(RecordsScene(self.game))
                elif self.selected_index == 3:  # 설정
                    pass  # TODO: 설정 씬
                elif self.selected_index == 4:  # 종료
                    self.game.running = False
    
    def render(self, screen):
        screen.fill((20, 20, 40))
        
        # 제목
        font_title = self.resources.get_font("main_title")
        title = font_title.render("황금알을 낳는 거위: 환생", True, (255, 215, 0))
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # 메뉴
        ui.UI.draw_menu(screen, self.resources, self.menu_items, self.selected_index,
                       config.SCREEN_WIDTH // 2 - 100, 300)

class ChallengeSelectScene(Scene):
    """도전 모드 선택 씬"""
    def __init__(self, game):
        super().__init__(game)
        self.selected_index = 0
        self.challenges = [
            ("무욕의 길", config.CHALLENGE_NO_GREED, "황금알을 하나라도 획득하면 실패합니다."),
            ("대부호의 야망", config.CHALLENGE_GREED_OVERDRIVE, "7분 안에 황금알 20개 이상 수집 후 탈출하세요."),
            ("도박 중독", config.CHALLENGE_GAMBLER_CURSE, "상인과 5회 이상 거래 후 탈출하세요."),
        ]
        self.menu_items = [ch[0] for ch in self.challenges]
        self.menu_items.append("뒤로")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.selected_index < len(self.challenges):
                    # 도전 모드 선택
                    self.game.stats = player.GameStats()
                    self.game.stats.difficulty = config.DIFFICULTY_NORMAL
                    self.game.stats.mode = "challenge"
                    self.game.stats.challenge_id = self.challenges[self.selected_index][1]
                    self.game.change_scene(IntroScene(self.game))
                else:  # 뒤로
                    self.game.change_scene(TitleScene(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene(TitleScene(self.game))
    
    def render(self, screen):
        screen.fill((20, 20, 40))
        
        font_title = self.resources.get_font("main_large")
        title = font_title.render("도전 모드", True, (255, 255, 255))
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # 메뉴
        ui.UI.draw_menu(screen, self.resources, self.menu_items, self.selected_index,
                       config.SCREEN_WIDTH // 2 - 150, 200)
        
        # 설명
        if self.selected_index < len(self.challenges):
            font_small = self.resources.get_font("main_small")
            desc = font_small.render(self.challenges[self.selected_index][2], True, (200, 200, 200))
            desc_rect = desc.get_rect(center=(config.SCREEN_WIDTH // 2, 500))
            screen.blit(desc, desc_rect)

class RecordsScene(Scene):
    """기록/도전과제 씬"""
    def __init__(self, game):
        super().__init__(game)
        self.achievement_manager = achievements.AchievementManager()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_scene(TitleScene(self.game))
    
    def render(self, screen):
        screen.fill((20, 20, 40))
        
        font_title = self.resources.get_font("main_large")
        title = font_title.render("도전과제", True, (255, 255, 255))
        screen.blit(title, (50, 50))
        
        font_small = self.resources.get_font("main_small")
        y = 100
        for ach_id, ach in self.achievement_manager.achievements.items():
            if not ach.hidden or ach.unlocked:
                status = "✓" if ach.unlocked else "○"
                color = (100, 255, 100) if ach.unlocked else (150, 150, 150)
                text = font_small.render(f"{status} {ach.name}: {ach.description}", True, color)
                screen.blit(text, (50, y))
                y += 30
        
        # 뒤로 가기 안내
        back_text = font_small.render("ESC: 뒤로", True, (200, 200, 200))
        screen.blit(back_text, (50, config.SCREEN_HEIGHT - 50))

class IntroScene(Scene):
    """인트로 씬 (거위와의 대화)"""
    def __init__(self, game):
        super().__init__(game)
        self.dialogue_index = 0
        self.dialogue_list = [
            "거위: 환생을 원하시는군요.",
            "거위: 하지만 그 대가가 필요합니다.",
            "거위: 황금알을 모으면 부와 권력을 얻을 수 있습니다.",
            "거위: 하지만 욕심은 위험을 불러옵니다.",
            "거위: 선택하세요...",
        ]
        self.show_choice = False
        self.choice_index = 0
        self.choice_items = [
            "욕심을 선택한다",
            "절제를 선택한다",
            "계약을 거절한다"
        ]
        self.choice_made = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.show_choice:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.dialogue_index < len(self.dialogue_list) - 1:
                        self.dialogue_index += 1
                        if self.dialogue_index == len(self.dialogue_list) - 1:
                            self.show_choice = True
            else:
                if not self.choice_made:
                    if event.key == pygame.K_UP:
                        self.choice_index = (self.choice_index - 1) % len(self.choice_items)
                    elif event.key == pygame.K_DOWN:
                        self.choice_index = (self.choice_index + 1) % len(self.choice_items)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.choice_made = True
                        if self.choice_index == 0:  # 욕심
                            self.game.stats.intro_greedy_choice = True
                            self.game.change_scene(TutorialScene(self.game))
                        elif self.choice_index == 1:  # 절제
                            self.game.stats.intro_greedy_choice = False
                            self.game.change_scene(TutorialScene(self.game))
                        elif self.choice_index == 2:  # 계약 거절
                            # 즉시 HEAVEN_WORKER 엔딩
                            ending_manager = endings.EndingManager()
                            ending_type = endings.ENDING_HEAVEN_WORKER
                            ending_manager.record_ending(ending_type)
                            self.game.change_scene(EndingScene(self.game, ending_type))
    
    def render(self, screen):
        screen.fill((30, 30, 50))
        
        font_medium = self.resources.get_font("main_medium")
        font_small = self.resources.get_font("main_small")
        
        if not self.show_choice:
            # 대사 표시
            dialogue = self.dialogue_list[self.dialogue_index]
            text = font_medium.render(dialogue, True, (255, 255, 255))
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
            
            # 다음 안내
            next_text = font_small.render("Space/Enter: 다음", True, (200, 200, 200))
            screen.blit(next_text, (config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT - 100))
        else:
            # 선택지 표시
            ui.UI.draw_menu(screen, self.resources, self.choice_items, self.choice_index,
                           config.SCREEN_WIDTH // 2 - 150, config.SCREEN_HEIGHT // 2 - 50)

class TutorialScene(Scene):
    """튜토리얼 씬"""
    def __init__(self, game):
        super().__init__(game)
        self.tutorial_maze = maze.Maze(config.TUTORIAL_MAZE_WIDTH, config.TUTORIAL_MAZE_HEIGHT)
        self.tutorial_maze.generate(self.game.stats)
        self.tutorial_player = player.Player(
            self.tutorial_maze.start_pos[0] * config.TILE_SIZE,
            self.tutorial_maze.start_pos[1] * config.TILE_SIZE,
            self.game.stats,
            self.resources
        )
        self.tutorial_camera = camera.Camera()
        self.tutorial_step = 0
        self.tutorial_texts = [
            ["WASD/방향키로 이동하세요", "E키로 상인과 상호작용하세요"],
            ["황금알을 모으면 보상을 얻지만", "욕심이 커질수록 위험이 증가합니다"],
            ["음식을 먹어 배고픔을 회복하세요", "배고픔이 0이 되면 게임 오버입니다"],
        ]
        self.skip_allowed = False
    
    def update(self, dt):
        self.tutorial_camera.update(self.tutorial_player.x, self.tutorial_player.y, dt)
        
        # 출구 도달 체크
        tile_x, tile_y = self.tutorial_player.get_tile_pos()
        if self.tutorial_maze.is_exit(tile_x, tile_y):
            self.skip_allowed = True
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.skip_allowed:
                    self.game.change_scene(MazeScene(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene(MazeScene(self.game))
    
    def render(self, screen):
        screen.fill((10, 10, 20))
        
        # 미로 렌더링
        self._render_maze(screen)
        
        # 플레이어 렌더링
        screen_x, screen_y = self.tutorial_camera.apply((self.tutorial_player.x, self.tutorial_player.y))
        player_sprite = self.resources.get_image("player")
        screen.blit(player_sprite, (screen_x, screen_y))
        
        # 튜토리얼 텍스트
        if self.tutorial_step < len(self.tutorial_texts):
            ui.UI.draw_tutorial_panel(screen, self.resources, self.tutorial_texts[self.tutorial_step])
        
        # 스킵 안내
        if self.skip_allowed:
            font_small = self.resources.get_font("main_small")
            skip_text = font_small.render("Space/Enter: 스킵", True, (200, 200, 200))
            screen.blit(skip_text, (config.SCREEN_WIDTH - 200, config.SCREEN_HEIGHT - 50))
    
    def _render_maze(self, screen):
        """미로 렌더링"""
        wall_sprite = self.resources.get_image("wall")
        floor_sprite = self.resources.get_image("floor")
        
        for y in range(self.tutorial_maze.height):
            for x in range(self.tutorial_maze.width):
                screen_x, screen_y = self.tutorial_camera.apply((x * config.TILE_SIZE, y * config.TILE_SIZE))
                if self.tutorial_camera.is_visible((x * config.TILE_SIZE, y * config.TILE_SIZE)):
                    if self.tutorial_maze.grid[y][x] == 0:
                        screen.blit(wall_sprite, (screen_x, screen_y))
                    else:
                        screen.blit(floor_sprite, (screen_x, screen_y))

class MazeScene(Scene):
    """메인 미로 씬"""
    def __init__(self, game):
        super().__init__(game)
        self.maze = maze.Maze(config.MAZE_WIDTH_NORMAL, config.MAZE_HEIGHT_NORMAL)
        self.maze.generate(self.game.stats)
        self.game_player = player.Player(
            self.maze.start_pos[0] * config.TILE_SIZE,
            self.maze.start_pos[1] * config.TILE_SIZE,
            self.game.stats,
            self.resources
        )
        self.game_camera = camera.Camera()
        
        # 상점 상태
        self.shop_state = config.SHOP_STATE_NORMAL
        self.current_merchant = None
        self.shop_menu_index = 0
        
        # 룰렛 상태
        self.roulette_spin_time = 0
        self.roulette_result_effect = None
        self.roulette_current_slot = 0
        
        # 배고픔 사망 연출
        self.death_fade_alpha = 0
        self.death_text_time = 0
        
        # 도전 모드 체크
        self.challenge_failed = False
        
        # 배고픔 90% 이상 시간 추적
        self.hunger_90plus_time = 0.0
        self.game.stats.hunger_90plus_time = 0.0
        
        # 이동 입력
        self.move_dx = 0
        self.move_dy = 0
        
        # 팝업 메시지
        self.popup_message = None
        self.popup_time = 0.0
    
    def update(self, dt):
        if self.challenge_failed or not self.game_player.alive:
            return
        
        # 배고픔 사망 체크
        if self.game_player.hunger <= 0 and self.game_player.alive:
            self.game_player.alive = False
            self.game_player.stats.died_by_hunger = True
        
        # 배고픔 사망 연출
        if self.game_player.stats.died_by_hunger:
            self.death_fade_alpha = min(255, self.death_fade_alpha + int(255 * dt / config.DEATH_FADE_TIME))
            if self.death_fade_alpha >= 200:
                self.death_text_time += dt
                if self.death_text_time >= config.DEATH_TEXT_DISPLAY_TIME + config.DEATH_FADE_TIME:
                    ending_manager = endings.EndingManager()
                    ending_type = ending_manager.determine_ending(self.game_player.stats)
                    ending_manager.record_ending(ending_type)
                    self.game.change_scene(EndingScene(self.game, ending_type))
            return
        
        # 도전 모드 실패 체크
        if self.game_player.stats.mode == "challenge":
            if self.game_player.stats.challenge_id == config.CHALLENGE_NO_GREED:
                if self.game_player.eggs > 0:
                    self.challenge_failed = True
                    self.popup_message = "도전 실패: 황금알을 획득했습니다"
                    self.popup_time = 3.0
            elif self.game_player.stats.challenge_id == config.CHALLENGE_GREED_OVERDRIVE:
                if self.game_player.stats.time_elapsed >= config.CHALLENGE_GREED_OVERDRIVE_TIME_LIMIT:
                    self.challenge_failed = True
                    self.popup_message = "도전 실패: 시간 초과"
                    self.popup_time = 3.0
        
        # 플레이어 이동 (연속 입력)
        if self.move_dx != 0 or self.move_dy != 0:
            self.game_player.move(self.move_dx, self.move_dy, self.maze, dt)
            
            # 아이템 획득 체크
            item = self.maze.get_item_at(self.game_player.x, self.game_player.y)
            if item and not item.picked:
                item.on_pick(self.game_player, self.game_player.stats)
            
            self.move_dx = 0
            self.move_dy = 0
        
        # 플레이어 업데이트
        self.game_player.update(dt)
        
        # 카메라 업데이트
        self.game_camera.update(self.game_player.x, self.game_player.y, dt)
        
        # 시간 경과
        self.game_player.stats.time_elapsed += dt
        
        # 배고픔 90% 이상 시간 추적
        if self.game_player.hunger / self.game_player.max_hunger >= 0.9:
            self.hunger_90plus_time += dt
            self.game_player.stats.hunger_90plus_time = self.hunger_90plus_time
        
        # 룰렛 회전 업데이트
        if self.shop_state == config.SHOP_STATE_ROULETTE_SPIN:
            self.roulette_spin_time += dt
            if self.roulette_spin_time >= config.ROULETTE_SPIN_TIME:
                self.shop_state = config.SHOP_STATE_ROULETTE_RESULT
                self.roulette_spin_time = 0
        
        # 팝업 메시지 업데이트
        if self.popup_message:
            self.popup_time -= dt
            if self.popup_time <= 0:
                if self.challenge_failed:
                    ending_manager = endings.EndingManager()
                    ending_type = endings.ENDING_HELL  # 도전 실패는 HELL
                    ending_manager.record_ending(ending_type)
                    self.game.change_scene(EndingScene(self.game, ending_type))
                self.popup_message = None
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # 상점 상태별 입력 처리
            if self.shop_state == config.SHOP_STATE_NORMAL:
                # 일반 이동
                dx, dy = 0, 0
                if event.key in [pygame.K_w, pygame.K_UP]:
                    dy = -1
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    dy = 1
                elif event.key in [pygame.K_a, pygame.K_LEFT]:
                    dx = -1
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    dx = 1
                elif event.key == pygame.K_e:
                    # 상인 상호작용
                    merchant = self.maze.get_merchant_at(self.game_player.x, self.game_player.y)
                    if merchant:
                        self.current_merchant = merchant
                        self.shop_state = config.SHOP_STATE_MENU
                        self.shop_menu_index = 0
                elif event.key == pygame.K_ESCAPE:
                    pass  # 일시정지 (TODO)
                
                # 이동 입력 저장 (update에서 처리)
                if dx != 0 or dy != 0:
                    self.move_dx = dx
                    self.move_dy = dy
            
            elif self.shop_state == config.SHOP_STATE_MENU:
                # 상점 메뉴
                if event.key == pygame.K_UP:
                    self.shop_menu_index = (self.shop_menu_index - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.shop_menu_index = (self.shop_menu_index + 1) % 3
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.shop_menu_index == 0:  # 룰렛
                        if self.current_merchant:
                            effect, error = self.current_merchant.trade_roulette(self.game_player)
                            if effect:
                                self.roulette_result_effect = effect
                                self.roulette_current_slot = random.randint(0, len(self.current_merchant.roulette_slots) - 1)
                                self.shop_state = config.SHOP_STATE_ROULETTE_SPIN
                                self.roulette_spin_time = 0
                                self.game_player.stats.trader_count += 1
                            elif error:
                                self.popup_message = error
                                self.popup_time = 2.0
                    elif self.shop_menu_index == 1:  # 안전 거래
                        if self.current_merchant:
                            effect, error = self.current_merchant.trade_safe(self.game_player)
                            if effect:
                                self.game_player.stats.trader_count += 1
                                self.shop_state = config.SHOP_STATE_NORMAL
                                self.current_merchant = None
                            elif error:
                                self.popup_message = error
                                self.popup_time = 2.0
                    elif self.shop_menu_index == 2:  # 그만두기
                        self.shop_state = config.SHOP_STATE_NORMAL
                        self.current_merchant = None
                elif event.key == pygame.K_ESCAPE:
                    self.shop_state = config.SHOP_STATE_NORMAL
                    self.current_merchant = None
            
            elif self.shop_state == config.SHOP_STATE_ROULETTE_RESULT:
                # 룰렛 결과 확인
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    self.shop_state = config.SHOP_STATE_NORMAL
                    self.current_merchant = None
                    self.roulette_result_effect = None
    
    def render(self, screen):
        screen.fill((10, 10, 20))
        
        # 미로 렌더링
        self._render_maze(screen)
        
        # 아이템 렌더링
        for item in self.maze.items_list:
            item.render(screen, self.game_camera, self.resources)
        
        # 상인 렌더링
        for m in self.maze.merchants:
            screen_x, screen_y = self.game_camera.apply((m.x, m.y))
            if self.game_camera.is_visible((m.x, m.y)):
                merchant_sprite = self.resources.get_image("merchant")
                screen.blit(merchant_sprite, (screen_x, screen_y))
        
        # 플레이어 렌더링
        screen_x, screen_y = self.game_camera.apply((self.game_player.x, self.game_player.y))
        player_sprite = self.resources.get_image("player")
        screen.blit(player_sprite, (screen_x, screen_y))
        
        # HUD
        ui.UI.draw_hunger_bar(screen, self.resources, self.game_player.hunger, 
                              self.game_player.max_hunger, 10, 10, 200, 30)
        ui.UI.draw_eggs_count(screen, self.resources, self.game_player.eggs, 10, 50)
        ui.UI.draw_effects_list(screen, self.resources, self.game_player.effects, 10, 80)
        
        # 배고픔 경고
        hunger_ratio = self.game_player.hunger / self.game_player.max_hunger
        ui.UI.draw_hunger_warning(screen, hunger_ratio)
        
        # 상점 UI
        if self.shop_state == config.SHOP_STATE_MENU:
            if self.current_merchant:
                ui.UI.draw_shop_menu(screen, self.resources, self.current_merchant, 
                                    self.game_player, self.shop_menu_index)
        elif self.shop_state == config.SHOP_STATE_ROULETTE_SPIN:
            if self.current_merchant:
                ui.UI.draw_roulette(screen, self.resources, self.current_merchant.roulette_slots,
                                   self.roulette_current_slot, self.roulette_spin_time,
                                   config.ROULETTE_SPIN_TIME)
        elif self.shop_state == config.SHOP_STATE_ROULETTE_RESULT:
            if self.roulette_result_effect:
                font = self.resources.get_font("main_medium")
                effect_name = self.roulette_result_effect.type
                text = font.render(f"결과: {effect_name}", True, (255, 255, 255))
                text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
                screen.blit(text, text_rect)
        
        # 팝업 메시지
        if self.popup_message:
            ui.UI.draw_popup(screen, self.resources, self.popup_message, 3.0, 
                           3.0 - self.popup_time)
        
        # 배고픔 사망 연출
        if self.game_player.stats.died_by_hunger:
            ui.UI.draw_death_screen(screen, self.death_fade_alpha)
        
        # 출구 도달 체크
        tile_x, tile_y = self.game_player.get_tile_pos()
        if self.maze.is_exit(tile_x, tile_y):
            # 도전 모드 최종 체크
            if self.game_player.stats.mode == "challenge":
                if self.game_player.stats.challenge_id == config.CHALLENGE_GREED_OVERDRIVE:
                    if self.game_player.eggs < config.CHALLENGE_GREED_OVERDRIVE_TARGET_EGGS:
                        self.challenge_failed = True
                        self.popup_message = "도전 실패: 목표 개수 미달"
                        self.popup_time = 3.0
                        return
                elif self.game_player.stats.challenge_id == config.CHALLENGE_GAMBLER_CURSE:
                    if self.game_player.stats.trader_count < config.CHALLENGE_GAMBLER_CURSE_MIN_TRADES:
                        self.challenge_failed = True
                        self.popup_message = "도전 실패: 상인 거래 횟수 부족"
                        self.popup_time = 3.0
                        return
            
            # 클리어
            ending_manager = endings.EndingManager()
            ending_type = ending_manager.determine_ending(self.game_player.stats)
            ending_manager.record_ending(ending_type)
            self.game.change_scene(EndingScene(self.game, ending_type))
    
    def _render_maze(self, screen):
        """미로 렌더링 (시야 제한 적용)"""
        wall_sprite = self.resources.get_image("wall")
        floor_sprite = self.resources.get_image("floor")
        
        player_tile_x, player_tile_y = self.game_player.get_tile_pos()
        vision_radius = self.game_player.vision_radius
        
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                # 시야 범위 체크
                dist = ((x - player_tile_x) ** 2 + (y - player_tile_y) ** 2) ** 0.5
                if dist <= vision_radius:
                    screen_x, screen_y = self.game_camera.apply((x * config.TILE_SIZE, y * config.TILE_SIZE))
                    if self.game_camera.is_visible((x * config.TILE_SIZE, y * config.TILE_SIZE)):
                        if self.maze.grid[y][x] == 0:
                            screen.blit(wall_sprite, (screen_x, screen_y))
                        else:
                            screen.blit(floor_sprite, (screen_x, screen_y))

class EndingScene(Scene):
    """엔딩 씬"""
    def __init__(self, game, ending_type):
        super().__init__(game)
        self.ending_type = ending_type
        self.ending_manager = endings.EndingManager()
        self.achievement_manager = achievements.AchievementManager()
        
        # 점수 계산
        self.score = self.ending_manager.calculate_score(self.game.stats)
        self.rank = self.ending_manager.calculate_rank(self.score)
        
        # 도전과제 체크
        self.achievement_manager.check_ending_achievements(self.game.stats, ending_type)
        # hunger_90plus_time 체크
        hunger_90_time = getattr(self.game.stats, 'hunger_90plus_time', 0.0)
        self.achievement_manager.check_hunger_90_achievement(hunger_90_time)
        hell_count = self.ending_manager.get_ending_count(endings.ENDING_HELL)
        self.achievement_manager.check_hell_achievement(hell_count)
        
        # 버튼
        self.selected_button = 0
        self.buttons = ["다시하기", "타이틀로"]
        
        # 새 도전과제 표시
        self.show_new_achievements = len(self.achievement_manager.new_achievements) > 0
        self.achievement_display_time = 0.0
    
    def update(self, dt):
        if self.show_new_achievements:
            self.achievement_display_time += dt
            if self.achievement_display_time >= 3.0:
                self.show_new_achievements = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.show_new_achievements:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    self.show_new_achievements = False
            else:
                if event.key == pygame.K_UP:
                    self.selected_button = 0
                elif event.key == pygame.K_DOWN:
                    self.selected_button = 1
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_button == 0:  # 다시하기
                        # 동일한 설정으로 재시작
                        new_stats = player.GameStats()
                        new_stats.difficulty = self.game.stats.difficulty
                        new_stats.mode = self.game.stats.mode
                        new_stats.challenge_id = self.game.stats.challenge_id
                        self.game.stats = new_stats
                        self.game.change_scene(IntroScene(self.game))
                    elif self.selected_button == 1:  # 타이틀로
                        self.game.change_scene(TitleScene(self.game))
    
    def render(self, screen):
        screen.fill((20, 20, 30))
        
        font_title = self.resources.get_font("main_large")
        font_medium = self.resources.get_font("main_medium")
        font_small = self.resources.get_font("main_small")
        
        # 엔딩 제목
        ending_name = endings.ENDING_NAMES.get(self.ending_type, self.ending_type)
        title = font_title.render(ending_name, True, (255, 215, 0))
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # 엔딩 설명
        ending_desc = endings.ENDING_DESCRIPTIONS.get(self.ending_type, "")
        desc = font_medium.render(ending_desc, True, (255, 255, 255))
        desc_rect = desc.get_rect(center=(config.SCREEN_WIDTH // 2, 200))
        screen.blit(desc, desc_rect)
        
        # 점수 및 랭크
        score_text = font_medium.render(f"점수: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(config.SCREEN_WIDTH // 2, 280))
        screen.blit(score_text, score_rect)
        
        rank_text = font_title.render(f"랭크: {self.rank}", True, (255, 215, 0))
        rank_rect = rank_text.get_rect(center=(config.SCREEN_WIDTH // 2, 330))
        screen.blit(rank_text, rank_rect)
        
        # 새 도전과제 표시
        if self.show_new_achievements:
            panel = pygame.Surface((600, 200))
            panel.set_alpha(240)
            panel.fill((0, 50, 0))
            panel_x = (config.SCREEN_WIDTH - 600) // 2
            panel_y = (config.SCREEN_HEIGHT - 200) // 2
            screen.blit(panel, (panel_x, panel_y))
            
            new_text = font_medium.render("새 도전과제 달성!", True, (100, 255, 100))
            new_rect = new_text.get_rect(center=(panel_x + 300, panel_y + 30))
            screen.blit(new_text, new_rect)
            
            y_offset = 70
            for ach in self.achievement_manager.new_achievements:
                ach_text = font_small.render(f"- {ach.name}", True, (255, 255, 255))
                screen.blit(ach_text, (panel_x + 50, panel_y + y_offset))
                y_offset += 30
            
            continue_text = font_small.render("Space/Enter: 계속", True, (200, 200, 200))
            screen.blit(continue_text, (panel_x + 200, panel_y + 160))
        else:
            # 버튼
            ui.UI.draw_menu(screen, self.resources, self.buttons, self.selected_button,
                           config.SCREEN_WIDTH // 2 - 100, 450)

