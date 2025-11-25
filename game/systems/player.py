"""
Player 클래스 및 GameStats
"""

from game.core import config
from game.systems import effects

class GameStats:
    """게임 통계"""
    def __init__(self):
        self.difficulty = config.DIFFICULTY_NORMAL
        self.mode = "normal"  # "normal" or "challenge"
        self.challenge_id = None
        self.total_eggs = 0
        self.trader_count = 0
        self.bad_effects_count = 0
        self.secret_rooms_found = 0
        self.time_elapsed = 0.0
        self.intro_greedy_choice = False
        self.died_by_hunger = False
        self.random_seed = None
        self.hunger_90plus_time = 0.0

class Player:
    """플레이어 클래스"""
    def __init__(self, x, y, stats, resources=None):
        self.x = x
        self.y = y
        self.stats = stats
        self.resources = resources
        
        # 이동 속도
        self.base_speed = config.BASE_SPEED
        self.speed = config.BASE_SPEED
        self.speed_multiplier = 1.0
        
        # 배고픔
        hunger_mult = {
            config.DIFFICULTY_EASY: config.EASY_HUNGER_MULT,
            config.DIFFICULTY_NORMAL: config.NORMAL_HUNGER_MULT,
            config.DIFFICULTY_HARD: config.HARD_HUNGER_MULT
        }.get(stats.difficulty, 1.0)
        
        self.max_hunger = config.BASE_MAX_HUNGER
        self.hunger = config.BASE_MAX_HUNGER
        self.hunger_rate = config.BASE_HUNGER_RATE * hunger_mult
        self.hunger_rate_multiplier = 1.0
        
        # 황금알
        self.eggs = 0
        
        # 시야
        self.base_vision_radius = config.BASE_VISION_RADIUS
        self.vision_radius = config.BASE_VISION_RADIUS
        
        # 효과
        self.effects = []
        self.has_food_boost = False
        self.has_double_reward = False
        self.has_invincible_on_max_hunger = False
        
        # 상태
        self.sprite_key = "player"
        self.alive = True
        
        # 이동 방향 (렌더링용)
        self.direction = (0, 0)
    
    def move(self, dx, dy, maze, dt):
        """이동 처리"""
        if not self.alive:
            return
        
        # 속도 계산
        current_speed = self.speed * self.speed_multiplier * dt
        
        new_x = self.x + dx * current_speed
        new_y = self.y + dy * current_speed
        
        # 충돌 검사
        tile_x = int(new_x / config.TILE_SIZE)
        tile_y = int(new_y / config.TILE_SIZE)
        
        if maze.is_walkable(tile_x, tile_y):
            self.x = new_x
            self.y = new_y
            if dx != 0 or dy != 0:
                self.direction = (dx, dy)
    
    def update(self, dt):
        """플레이어 상태 갱신"""
        if not self.alive:
            return
        
        # 배고픔 증가
        self.update_hunger(dt)
        
        # 효과 갱신
        self.effects = [e for e in self.effects if e.update(self, dt)]
        
        # 효과 재적용 (효과가 만료되면 제거)
        self._reapply_effects()
        
        # 욕심 디버프 적용
        self._apply_greed_debuff()
        
        # 배고픔 사망 체크
        if self.hunger <= 0:
            self.alive = False
            self.stats.died_by_hunger = True
    
    def update_hunger(self, dt):
        """배고픔 감소"""
        hunger_decrease = self.hunger_rate * self.hunger_rate_multiplier * dt
        self.hunger = max(0, self.hunger - hunger_decrease)
    
    def _reapply_effects(self):
        """효과 재적용 (속도/시야 등)"""
        # 속도/시야 배율 초기화
        self.speed_multiplier = 1.0
        self.vision_radius = self.base_vision_radius
        self.hunger_rate_multiplier = 1.0
        self.has_food_boost = False
        self.has_double_reward = False
        self.has_invincible_on_max_hunger = False
        
        # 모든 활성 효과 재적용
        for effect in self.effects:
            if effect.active:
                effect.apply(self)
    
    def _apply_greed_debuff(self):
        """욕심 디버프 적용"""
        if self.eggs >= config.EGG_VISION_THRESHOLD:
            # 시야 감소
            self.vision_radius = max(1, int(self.vision_radius * (1 - config.EGG_VISION_REDUCTION)))
        
        if self.eggs >= config.EGG_SPEED_THRESHOLD2:
            # 두 번째 속도 감소
            self.speed_multiplier *= (1 - config.EGG_SPEED_REDUCTION2)
        elif self.eggs >= config.EGG_SPEED_THRESHOLD1:
            # 첫 번째 속도 감소
            self.speed_multiplier *= (1 - config.EGG_SPEED_REDUCTION1)
    
    def apply_effect(self, effect):
        """효과 적용"""
        effect.apply(self)
        self.effects.append(effect)
        self._reapply_effects()
    
    def get_tile_pos(self):
        """타일 좌표 반환"""
        return (int(self.x / config.TILE_SIZE), int(self.y / config.TILE_SIZE))
    
    def get_pixel_pos(self):
        """픽셀 좌표 반환"""
        return (self.x, self.y)

