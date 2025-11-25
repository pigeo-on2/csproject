"""
엔딩 시스템 - 엔딩 결정, 점수/랭크 계산, 저장/로드
"""

import os
from game.core import config

# 엔딩 타입
ENDING_HELL = "HELL"
ENDING_KING = "KING"
ENDING_NOBLE = "NOBLE"
ENDING_FARMER = "FARMER"
ENDING_BEGGAR = "BEGGAR"
ENDING_HEAVEN_WORKER = "HEAVEN_WORKER"

ENDING_NAMES = {
    ENDING_HELL: "지옥",
    ENDING_KING: "왕",
    ENDING_NOBLE: "귀족",
    ENDING_FARMER: "농부",
    ENDING_BEGGAR: "거지",
    ENDING_HEAVEN_WORKER: "천국의 일꾼"
}

ENDING_DESCRIPTIONS = {
    ENDING_HELL: "욕심에 빠져 타락한 영혼은 지옥으로 떨어졌습니다.",
    ENDING_KING: "황금알을 많이 모았지만 욕심을 절제하여 왕이 되었습니다.",
    ENDING_NOBLE: "적당한 욕심과 절제의 균형으로 귀족이 되었습니다.",
    ENDING_FARMER: "욕심 없이 성실하게 살아 농부가 되었습니다.",
    ENDING_BEGGAR: "거의 아무것도 얻지 못하고 거지가 되었습니다.",
    ENDING_HEAVEN_WORKER: "계약을 거절하고 천국의 일꾼이 되었습니다."
}

class EndingManager:
    """엔딩 관리자"""
    def __init__(self):
        self.endings_count = {}
        self.load()
    
    def determine_ending(self, stats):
        """엔딩 결정"""
        # 배고픔으로 사망
        if stats.died_by_hunger:
            return ENDING_HELL
        
        # 계약 거절
        if stats.intro_greedy_choice is False and stats.trader_count == 0:
            # IntroScene에서 계약 거절 선택 시 HEAVEN_WORKER로 즉시 이동하지만,
            # 여기서는 일반적인 경우를 처리
            if stats.total_eggs == 0:
                return ENDING_HEAVEN_WORKER
        
        eggs = stats.total_eggs
        bad_effects = stats.bad_effects_count
        
        # 황금알이 매우 많고 나쁜 효과도 많음 → HELL
        if eggs >= 30 and bad_effects >= 3:
            return ENDING_HELL
        
        # 황금알이 많고 나쁜 효과가 적음 → KING
        if eggs >= 20 and bad_effects <= 1:
            return ENDING_KING
        
        # 황금알이 중간, 균형 → NOBLE
        if 5 <= eggs < 20:
            return ENDING_NOBLE
        
        # 황금알이 적고 욕심 선택 안 함 → FARMER
        if eggs < 5 and not stats.intro_greedy_choice:
            return ENDING_FARMER
        
        # 황금알이 거의 없음 → BEGGAR
        if eggs <= 1:
            return ENDING_BEGGAR
        
        # 기본값
        return ENDING_NOBLE
    
    def calculate_score(self, stats):
        """점수 계산"""
        score = 0
        
        # 황금알 점수
        score += stats.total_eggs * config.SCORE_EGG_VALUE
        
        # 비밀 방 보너스
        score += stats.secret_rooms_found * config.SCORE_SECRET_ROOM_BONUS
        
        # 시간 보너스 (최대 시간 제한이 있다고 가정, 예: 10분)
        time_limit = 600  # 10분
        if stats.time_elapsed < time_limit:
            time_bonus = int((time_limit - stats.time_elapsed) * config.SCORE_TIME_BONUS)
            score += max(0, time_bonus)
        
        return score
    
    def calculate_rank(self, score):
        """랭크 계산"""
        if score >= config.RANK_S_THRESHOLD:
            return "S"
        elif score >= config.RANK_A_THRESHOLD:
            return "A"
        elif score >= config.RANK_B_THRESHOLD:
            return "B"
        else:
            return "C"
    
    def record_ending(self, ending_type):
        """엔딩 기록"""
        if ending_type not in self.endings_count:
            self.endings_count[ending_type] = 0
        self.endings_count[ending_type] += 1
        self.save()
    
    def get_ending_count(self, ending_type):
        """엔딩 횟수 가져오기"""
        return self.endings_count.get(ending_type, 0)
    
    def save(self):
        """엔딩 저장"""
        try:
            with open("data/endings.txt", "w", encoding="utf-8") as f:
                for ending_type, count in self.endings_count.items():
                    f.write(f"{ending_type}:{count}\n")
        except Exception as e:
            print(f"엔딩 저장 실패: {e}")
    
    def load(self):
        """엔딩 로드"""
        if not os.path.exists("data/endings.txt"):
            return
        
        try:
            with open("data/endings.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        ending_type, count_str = line.split(":", 1)
                        try:
                            count = int(count_str)
                            self.endings_count[ending_type] = count
                        except ValueError:
                            pass
        except Exception as e:
            print(f"엔딩 로드 실패: {e}")

