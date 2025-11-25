"""
상점 및 룰렛 시스템
"""

import random
from game.core import config
from game.systems import effects

class RouletteSlot:
    """룰렛 슬롯"""
    def __init__(self, effect_type, weight):
        self.effect_type = effect_type
        self.weight = weight
        self.effect_class = None  # Effect 클래스는 나중에 설정

class Merchant:
    """상인 클래스"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite_key = "merchant"
        self.traded_times = 0
        self.roulette_slots = []
        self._initialize_roulette()
    
    def _initialize_roulette(self):
        """룰렛 초기화 (최소 8칸)"""
        # 룰렛 슬롯 정의
        slots = [
            ("speed_up", 2.0),
            ("vision_up", 2.0),
            ("hunger_rate_down", 2.0),
            ("hunger_instant_up", 2.0),
            ("food_boost", 1.5),
            ("speed_down", 1.5),
            ("vision_down", 1.5),
            ("double_reward", 1.0),
        ]
        
        # 최소 8칸 보장
        while len(slots) < config.ROULETTE_SLOTS_MIN:
            # 추가 슬롯 (좋은 효과와 나쁜 효과 균형)
            if len(slots) % 2 == 0:
                slots.append(("speed_up", 1.0))
            else:
                slots.append(("speed_down", 1.0))
        
        self.roulette_slots = [RouletteSlot(effect_type, weight) for effect_type, weight in slots]
        
        # Effect 클래스 매핑
        effect_classes = {
            "speed_up": effects.SpeedUp,
            "speed_down": effects.SpeedDown,
            "vision_up": effects.VisionUp,
            "vision_down": effects.VisionDown,
            "hunger_rate_down": effects.HungerRateDown,
            "hunger_instant_up": effects.HungerInstantUp,
            "food_boost": effects.FoodBoost,
            "double_reward": effects.DoubleReward,
        }
        
        for slot in self.roulette_slots:
            if slot.effect_type in effect_classes:
                slot.effect_class = effect_classes[slot.effect_type]
    
    def adjust_roulette_weights(self):
        """거래 횟수에 따른 룰렛 weight 조정"""
        for slot in self.roulette_slots:
            if slot.effect_type in effects.GOOD_EFFECTS:
                # 좋은 효과: weight 감소
                slot.weight *= max(
                    config.ROULETTE_WEIGHT_MIN,
                    1 - self.traded_times * config.ROULETTE_WEIGHT_DECAY_RATE
                )
            elif slot.effect_type in effects.BAD_EFFECTS:
                # 나쁜 효과: weight 증가
                slot.weight *= (1 + self.traded_times * config.ROULETTE_WEIGHT_INCREASE_RATE)
    
    def spin_roulette(self):
        """룰렛 돌리기"""
        # weight 조정
        self.adjust_roulette_weights()
        
        # weight 기반 확률 계산
        total_weight = sum(slot.weight for slot in self.roulette_slots)
        r = random.uniform(0, total_weight)
        
        current_weight = 0
        selected_slot = None
        for slot in self.roulette_slots:
            current_weight += slot.weight
            if r <= current_weight:
                selected_slot = slot
                break
        
        if selected_slot and selected_slot.effect_class:
            # Effect 인스턴스 생성
            effect = selected_slot.effect_class()
            return effect
        
        return None
    
    def safe_trade(self):
        """안전 거래"""
        r = random.random()
        
        if r < config.SAFE_TRADE_FOOD_CHANCE:
            # Food 아이템 (여기서는 HungerInstantUp으로 대체)
            return effects.HungerInstantUp(value=25)
        elif r < config.SAFE_TRADE_FOOD_CHANCE + config.SAFE_TRADE_HUNGER_RATE_DOWN_CHANCE:
            return effects.HungerRateDown()
        elif r < (config.SAFE_TRADE_FOOD_CHANCE + config.SAFE_TRADE_HUNGER_RATE_DOWN_CHANCE + 
                  config.SAFE_TRADE_SPEED_UP_CHANCE):
            return effects.SpeedUp(duration=20.0, value=0.1)  # 소폭 증가
        else:
            return effects.HungerInstantUp(value=10)  # 소량 회복
    
    def trade_roulette(self, player):
        """룰렛 거래"""
        if player.eggs < config.ROULETTE_EGG_COST:
            return None, "황금알이 부족합니다."
        
        player.eggs -= config.ROULETTE_EGG_COST
        self.traded_times += 1
        
        effect = self.spin_roulette()
        if effect:
            player.apply_effect(effect)
            
            # 나쁜 효과인지 체크
            if effect.type in effects.BAD_EFFECTS:
                player.stats.bad_effects_count += 1
            
            return effect, None
        
        return None, "룰렛 오류"
    
    def trade_safe(self, player):
        """안전 거래"""
        if player.eggs < config.SAFE_TRADE_EGG_COST:
            return None, "황금알이 부족합니다."
        
        player.eggs -= config.SAFE_TRADE_EGG_COST
        self.traded_times += 1
        
        effect = self.safe_trade()
        if effect:
            player.apply_effect(effect)
            return effect, None
        
        return None, "거래 오류"
    
    def get_tile_pos(self):
        """타일 좌표 반환"""
        return (int(self.x / config.TILE_SIZE), int(self.y / config.TILE_SIZE))
    
    def get_pixel_pos(self):
        """픽셀 좌표 반환"""
        return (self.x, self.y)

