"""
아이템 시스템
"""

import random
from game.core import config
from game.systems import effects

class Item:
    """아이템 베이스 클래스"""
    def __init__(self, x, y, sprite_key="item_default"):
        self.x = x
        self.y = y
        self.sprite_key = sprite_key
        self.picked = False
    
    def on_pick(self, player, stats):
        """아이템 획득 시 호출"""
        pass
    
    def render(self, screen, camera, resources):
        """아이템 렌더링"""
        if self.picked:
            return
        
        screen_x, screen_y = camera.apply((self.x, self.y))
        if camera.is_visible((self.x, self.y)):
            sprite = resources.get_image(self.sprite_key)
            screen.blit(sprite, (screen_x, screen_y))

class GoldenEgg(Item):
    """황금알"""
    def __init__(self, x, y):
        super().__init__(x, y, "golden_egg")
    
    def on_pick(self, player, stats):
        if self.picked:
            return
        
        self.picked = True
        player.eggs += 1
        stats.total_eggs += 1
        
        # 황금 파티클 효과 (시각적 표현은 나중에 추가 가능)
        # 사운드 재생
        if hasattr(player, 'resources') and player.resources:
            player.resources.play_sound("sfx_golden_egg", 0.5)
        
        # DoubleReward 효과가 있으면 추가 획득
        if hasattr(player, 'has_double_reward') and player.has_double_reward:
            player.eggs += 1
            stats.total_eggs += 1

class Food(Item):
    """음식"""
    def __init__(self, x, y):
        super().__init__(x, y, "food")
    
    def on_pick(self, player, stats):
        if self.picked:
            return
        
        self.picked = True
        
        # 회복량 계산
        heal_amount = random.randint(config.FOOD_HEAL_MIN, config.FOOD_HEAL_MAX)
        
        # FoodBoost 효과가 있으면 추가 회복
        if hasattr(player, 'has_food_boost') and player.has_food_boost:
            heal_amount = int(heal_amount * config.FOOD_BOOST_MULTIPLIER)
        
        player.hunger = min(player.max_hunger, player.hunger + heal_amount)
        
        # 사운드 재생
        if hasattr(player, 'resources') and player.resources:
            player.resources.play_sound("sfx_food", 0.3)

class SecretItem(Item):
    """비밀 방 전용 아이템 (거위 깃털)"""
    def __init__(self, x, y):
        super().__init__(x, y, "secret_item")
        self.effect_applied = False
    
    def on_pick(self, player, stats):
        if self.picked:
            return
        
        self.picked = True
        
        # VisionUp + HungerRateDown 결합 버프
        vision_effect = effects.VisionUp(duration=config.EFFECT_VISION_UP_DURATION * 2)
        hunger_effect = effects.HungerRateDown(duration=config.EFFECT_HUNGER_RATE_DOWN_DURATION * 2)
        
        player.apply_effect(vision_effect)
        player.apply_effect(hunger_effect)
        
        stats.secret_rooms_found += 1
        
        # 사운드 재생
        if hasattr(player, 'resources') and player.resources:
            player.resources.play_sound("sfx_secret_item", 0.4)

