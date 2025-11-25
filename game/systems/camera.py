"""
Camera 시스템 - 플레이어 중심 렌더링
"""

from game.core import config

class Camera:
    """카메라 클래스"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
    
    def update(self, target_x, target_y, dt):
        """카메라 업데이트 (부드러운 추적)"""
        self.target_x = target_x
        self.target_y = target_y
        
        # 부드러운 추적
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        self.x += dx * config.CAMERA_FOLLOW_SPEED * dt
        self.y += dy * config.CAMERA_FOLLOW_SPEED * dt
    
    def apply(self, position):
        """월드 좌표 → 화면 좌표 변환"""
        world_x, world_y = position
        screen_x = world_x - self.x + config.SCREEN_WIDTH // 2
        screen_y = world_y - self.y + config.SCREEN_HEIGHT // 2
        return (screen_x, screen_y)
    
    def is_visible(self, position, margin=100):
        """위치가 화면에 보이는지 확인"""
        screen_x, screen_y = self.apply(position)
        return (-margin <= screen_x <= config.SCREEN_WIDTH + margin and
                -margin <= screen_y <= config.SCREEN_HEIGHT + margin)
    
    def get_view_bounds(self):
        """카메라가 보는 범위 (월드 좌표)"""
        left = self.x - config.SCREEN_WIDTH // 2
        right = self.x + config.SCREEN_WIDTH // 2
        top = self.y - config.SCREEN_HEIGHT // 2
        bottom = self.y + config.SCREEN_HEIGHT // 2
        return (left, top, right, bottom)

