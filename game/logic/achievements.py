"""
도전과제 시스템
"""

import json
import os
from game.core import config

class Achievement:
    """도전과제 클래스"""
    def __init__(self, achievement_id, name, description, hidden=False):
        self.id = achievement_id
        self.name = name
        self.description = description
        self.hidden = hidden
        self.unlocked = False

class AchievementManager:
    """도전과제 관리자"""
    def __init__(self):
        self.achievements = {}
        self.new_achievements = []  # 이번 플레이에서 새로 달성한 도전과제
        self.load()
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """도전과제 초기화"""
        achievements_list = [
            Achievement("first_clear", "첫 걸음", "게임을 처음 클리어했습니다.", False),
            Achievement("no_trader_clear", "독립심", "상인과 거래하지 않고 클리어했습니다.", False),
            Achievement("trader_5plus", "상인 친구", "상인과 5회 이상 거래했습니다.", False),
            Achievement("eggs_30plus", "황금 수집가", "황금알을 30개 이상 모았습니다.", False),
            Achievement("eggs_0to1", "절제의 미덕", "황금알을 0~1개만 가지고 클리어했습니다.", False),
            Achievement("speedrun_5min", "빠른 발", "5분 이내에 클리어했습니다.", False),
            Achievement("hunger_90plus", "절박한 생존", "배고픔이 90% 이상인 상태에서 30초 이상 버텼습니다.", False),
            Achievement("secret_room", "탐험가", "비밀 방을 발견했습니다.", False),
            Achievement("perfect_restraint", "완벽한 절제", "황금알 0개, 상인 거래 0회, 비밀 방 0개로 비지옥 엔딩을 봤습니다.", True),
            Achievement("hell_3times", "타락의 길", "HELL 엔딩을 3회 이상 봤습니다.", False),
        ]
        
        for ach in achievements_list:
            if ach.id not in self.achievements:
                self.achievements[ach.id] = ach
    
    def check_all(self, stats, player):
        """모든 도전과제 체크"""
        self.new_achievements = []
        
        # 첫 클리어 (엔딩 화면에서 체크, 여기서는 플레이어 생존 여부로 간접 체크)
        # 실제로는 엔딩 화면에서 호출
        
        # 상인 거래 0회 클리어
        if not self.achievements["no_trader_clear"].unlocked:
            if stats.trader_count == 0 and player.alive and stats.died_by_hunger == False:
                self.unlock("no_trader_clear")
        
        # 상인 거래 5회 이상
        if not self.achievements["trader_5plus"].unlocked:
            if stats.trader_count >= 5:
                self.unlock("trader_5plus")
        
        # 황금알 30개 이상
        if not self.achievements["eggs_30plus"].unlocked:
            if stats.total_eggs >= 30:
                self.unlock("eggs_30plus")
        
        # 황금알 0~1개 클리어
        if not self.achievements["eggs_0to1"].unlocked:
            if player.eggs <= 1 and player.alive and stats.died_by_hunger == False:
                self.unlock("eggs_0to1")
        
        # 5분 이내 클리어
        if not self.achievements["speedrun_5min"].unlocked:
            if stats.time_elapsed <= 300 and player.alive and stats.died_by_hunger == False:
                self.unlock("speedrun_5min")
        
        # 배고픔 90% 이상에서 버티기 (MazeScene에서 별도로 체크 필요)
        # 여기서는 체크하지 않음
        
        # 비밀 방 발견
        if not self.achievements["secret_room"].unlocked:
            if stats.secret_rooms_found > 0:
                self.unlock("secret_room")
        
        # 완벽한 절제 (엔딩 화면에서 체크)
        # 여기서는 체크하지 않음
        
        # HELL 엔딩 3회 이상 (엔딩 화면에서 체크)
        # 여기서는 체크하지 않음
    
    def check_ending_achievements(self, stats, ending_type):
        """엔딩 관련 도전과제 체크"""
        # 첫 클리어
        if not self.achievements["first_clear"].unlocked:
            if ending_type != "HELL" or not stats.died_by_hunger:
                self.unlock("first_clear")
        
        # 완벽한 절제
        if not self.achievements["perfect_restraint"].unlocked:
            if (stats.total_eggs == 0 and stats.trader_count == 0 and 
                stats.secret_rooms_found == 0 and ending_type != "HELL"):
                self.unlock("perfect_restraint")
    
    def check_hunger_90_achievement(self, time_at_90plus):
        """배고픔 90% 이상 버티기 체크"""
        if not self.achievements["hunger_90plus"].unlocked:
            if time_at_90plus >= 30.0:
                self.unlock("hunger_90plus")
    
    def check_hunger_achievement(self, time_at_90plus):
        """배고픔 90% 이상 버티기 체크 (별칭)"""
        self.check_hunger_90_achievement(time_at_90plus)
    
    def check_hell_achievement(self, hell_count):
        """HELL 엔딩 횟수 체크"""
        if not self.achievements["hell_3times"].unlocked:
            if hell_count >= 3:
                self.unlock("hell_3times")
    
    def unlock(self, achievement_id):
        """도전과제 해금"""
        if achievement_id in self.achievements:
            if not self.achievements[achievement_id].unlocked:
                self.achievements[achievement_id].unlocked = True
                self.new_achievements.append(self.achievements[achievement_id])
                self.save()
    
    def save(self):
        """도전과제 저장"""
        data = {}
        for ach_id, ach in self.achievements.items():
            data[ach_id] = {
                "unlocked": ach.unlocked
            }
        
        try:
            with open("data/achievements.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"도전과제 저장 실패: {e}")
    
    def load(self):
        """도전과제 로드"""
        if not os.path.exists("data/achievements.json"):
            return
        
        try:
            with open("data/achievements.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for ach_id, ach_data in data.items():
                if ach_id in self.achievements:
                    self.achievements[ach_id].unlocked = ach_data.get("unlocked", False)
        except Exception as e:
            print(f"도전과제 로드 실패: {e}")
    
    def get_unlocked_count(self):
        """해금된 도전과제 개수"""
        return sum(1 for ach in self.achievements.values() if ach.unlocked)
    
    def get_total_count(self):
        """전체 도전과제 개수"""
        return len(self.achievements)

