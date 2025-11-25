"""
버프/디버프 시스템
"""

from game.core import config

class Effect:
    """효과 베이스 클래스"""
    def __init__(self, effect_type, duration, value):
        self.type = effect_type
        self.duration = duration  # -1은 영구
        self.value = value
        self.active = True
        self.time_remaining = duration
    
    def apply(self, player):
        """효과 적용"""
        pass
    
    def update(self, player, dt):
        """효과 갱신"""
        if self.duration > 0:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.expire(player)
                return False
        return True
    
    def expire(self, player):
        """효과 만료"""
        self.active = False

class SpeedUp(Effect):
    """이동 속도 증가"""
    def __init__(self, duration=config.EFFECT_SPEED_UP_DURATION, value=config.EFFECT_SPEED_UP_VALUE):
        super().__init__("speed_up", duration, value)
    
    def apply(self, player):
        player.speed_multiplier += self.value

class SpeedDown(Effect):
    """이동 속도 감소"""
    def __init__(self, duration=config.EFFECT_SPEED_DOWN_DURATION, value=config.EFFECT_SPEED_DOWN_VALUE):
        super().__init__("speed_down", duration, value)
    
    def apply(self, player):
        player.speed_multiplier -= self.value

class VisionUp(Effect):
    """시야 증가"""
    def __init__(self, duration=config.EFFECT_VISION_UP_DURATION, value=config.EFFECT_VISION_UP_VALUE):
        super().__init__("vision_up", duration, value)
    
    def apply(self, player):
        player.vision_radius += int(self.value)

class VisionDown(Effect):
    """시야 감소"""
    def __init__(self, duration=config.EFFECT_VISION_DOWN_DURATION, value=config.EFFECT_VISION_DOWN_VALUE):
        super().__init__("vision_down", duration, value)
    
    def apply(self, player):
        player.vision_radius = max(1, player.vision_radius - int(self.value))

class HungerRateDown(Effect):
    """배고픔 감소 속도 감소"""
    def __init__(self, duration=config.EFFECT_HUNGER_RATE_DOWN_DURATION, value=config.EFFECT_HUNGER_RATE_DOWN_VALUE):
        super().__init__("hunger_rate_down", duration, value)
    
    def apply(self, player):
        player.hunger_rate_multiplier *= (1 - self.value)

class HungerInstantUp(Effect):
    """배고픔 즉시 회복"""
    def __init__(self, value=config.EFFECT_HUNGER_INSTANT_UP_VALUE):
        super().__init__("hunger_instant_up", 0, value)  # 즉시 효과, duration=0
    
    def apply(self, player):
        player.hunger = min(player.max_hunger, player.hunger + self.value)

class FoodBoost(Effect):
    """음식 회복량 증가"""
    def __init__(self, duration=config.EFFECT_FOOD_BOOST_DURATION):
        super().__init__("food_boost", duration, config.FOOD_BOOST_MULTIPLIER)
    
    def apply(self, player):
        player.has_food_boost = True

class DoubleReward(Effect):
    """보상 2배"""
    def __init__(self, duration=config.EFFECT_DOUBLE_REWARD_DURATION):
        super().__init__("double_reward", duration, 2.0)
    
    def apply(self, player):
        player.has_double_reward = True

class InvincibleOnMaxHunger(Effect):
    """배고픔 최대일 때 무적"""
    def __init__(self, duration=-1):  # 영구
        super().__init__("invincible_on_max_hunger", duration, 1.0)
    
    def apply(self, player):
        player.has_invincible_on_max_hunger = True
    
    def update(self, player, dt):
        # 배고픔이 최대가 아니면 효과 비활성화
        if player.hunger < player.max_hunger:
            self.expire(player)
            return False
        return True

# 좋은 효과 목록 (룰렛 weight 조정용)
GOOD_EFFECTS = ["speed_up", "vision_up", "hunger_rate_down", "hunger_instant_up", "food_boost"]

# 나쁜 효과 목록
BAD_EFFECTS = ["speed_down", "vision_down"]

