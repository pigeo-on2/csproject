"""
황금알을 낳는 거위: 환생 - 메인 게임 루프
"""

import pygame
import sys
from game.core import config
from game.core import resources
from game.scenes import scenes
from game.systems import player

class Game:
    """게임 메인 클래스"""
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("황금알을 낳는 거위: 환생")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # ResourceManager 초기화
        self.resources = resources.ResourceManager()
        self.resources.initialize_defaults()
        
        # GameStats 초기화
        self.stats = player.GameStats()
        
        # 현재 씬
        self.current_scene = scenes.TitleScene(self)
        
        # 디버그 모드
        self.debug_mode = False
    
    def change_scene(self, new_scene):
        """씬 변경"""
        self.current_scene = new_scene
    
    def run(self):
        """메인 게임 루프"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # 초 단위
            
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # 디버그 키
                    if event.key == pygame.K_F1:
                        self.debug_mode = not self.debug_mode
                    elif event.key == pygame.K_F2:
                        if hasattr(self.stats, 'random_seed') and self.stats.random_seed:
                            print(f"랜덤 시드: {self.stats.random_seed}")
                
                # 씬 이벤트 처리
                self.current_scene.handle_event(event)
            
            # 씬 업데이트
            self.current_scene.update(dt)
            
            # 씬 렌더링
            self.current_scene.render(self.screen)
            
            # 디버그 정보
            if self.debug_mode:
                self._render_debug()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _render_debug(self):
        """디버그 정보 렌더링"""
        font = pygame.font.Font(None, 24)
        debug_texts = [
            f"FPS: {int(self.clock.get_fps())}",
            f"씬: {type(self.current_scene).__name__}",
        ]
        
        if hasattr(self.current_scene, 'game_player'):
            player = self.current_scene.game_player
            debug_texts.extend([
                f"위치: ({int(player.x)}, {int(player.y)})",
                f"배고픔: {player.hunger:.1f}/{player.max_hunger}",
                f"황금알: {player.eggs}",
                f"시야: {player.vision_radius}",
            ])
        
        y = 10
        for text in debug_texts:
            surface = font.render(text, True, (255, 255, 0))
            self.screen.blit(surface, (config.SCREEN_WIDTH - 300, y))
            y += 25

def main():
    """메인 함수"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

