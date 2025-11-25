"""
UI 시스템 - HUD, 메뉴, 튜토리얼, 상점 UI, 팝업
"""

import pygame
import math
from game.core import config

class UI:
    """UI 유틸리티 클래스"""
    @staticmethod
    def draw_hunger_bar(screen, resources, hunger, max_hunger, x, y, width, height):
        """배고픔 게이지 바 그리기"""
        font = resources.get_font("main_small")
        
        # 배경
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        
        # 배고픔 비율
        hunger_ratio = hunger / max_hunger if max_hunger > 0 else 0
        
        # 색상 결정
        if hunger_ratio > 0.8:
            color = (200, 0, 0)  # 빨강
        elif hunger_ratio > 0.5:
            color = (200, 150, 0)  # 주황
        else:
            color = (0, 200, 0)  # 초록
        
        # 게이지
        bar_width = int(width * hunger_ratio)
        pygame.draw.rect(screen, color, (x, y, bar_width, height))
        
        # 테두리
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
        
        # 텍스트
        text = font.render(f"배고픔: {int(hunger)}/{max_hunger}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text, text_rect)
    
    @staticmethod
    def draw_eggs_count(screen, resources, eggs, x, y):
        """황금알 개수 표시"""
        font = resources.get_font("main_medium")
        text = font.render(f"황금알: {eggs}", True, (255, 215, 0))
        screen.blit(text, (x, y))
    
    @staticmethod
    def draw_effects_list(screen, resources, effects, x, y):
        """활성 효과 리스트 표시"""
        font = resources.get_font("main_small")
        
        effect_names = {
            "speed_up": "속도↑",
            "speed_down": "속도↓",
            "vision_up": "시야↑",
            "vision_down": "시야↓",
            "hunger_rate_down": "배고픔↓",
            "hunger_instant_up": "회복",
            "food_boost": "음식↑",
            "double_reward": "보상2배",
            "invincible_on_max_hunger": "무적"
        }
        
        y_offset = 0
        for effect in effects:
            if effect.active:
                name = effect_names.get(effect.type, effect.type)
                if effect.duration > 0:
                    time_text = f"{int(effect.time_remaining)}초"
                else:
                    time_text = "영구"
                
                text = font.render(f"{name} ({time_text})", True, (200, 200, 255))
                screen.blit(text, (x, y + y_offset))
                y_offset += 20
    
    @staticmethod
    def draw_hunger_warning(screen, hunger_ratio):
        """배고픔 80%↑ 시 붉은 화면 외곽 연출"""
        if hunger_ratio >= config.HUNGER_WARNING_THRESHOLD:
            # 알파 값 계산 (80%에서 시작, 100%에서 최대)
            alpha = int(255 * min(1.0, (hunger_ratio - config.HUNGER_WARNING_THRESHOLD) / 0.2))
            
            # 반투명 빨간색 오버레이
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(alpha // 3)  # 너무 강하지 않게
            overlay.fill((200, 0, 0))
            screen.blit(overlay, (0, 0))
    
    @staticmethod
    def draw_menu(screen, resources, menu_items, selected_index, x, y, spacing=40):
        """메뉴 그리기"""
        font = resources.get_font("main_medium")
        
        for i, item in enumerate(menu_items):
            if i == selected_index:
                color = (255, 255, 0)  # 선택된 항목은 노란색
                prefix = "> "
            else:
                color = (255, 255, 255)
                prefix = "  "
            
            text = font.render(prefix + item, True, color)
            screen.blit(text, (x, y + i * spacing))
    
    @staticmethod
    def draw_tutorial_panel(screen, resources, text_lines, alpha=200):
        """튜토리얼 패널 그리기"""
        font = resources.get_font("main_small")
        
        # 반투명 패널
        panel_height = len(text_lines) * 30 + 40
        panel = pygame.Surface((config.SCREEN_WIDTH - 100, panel_height))
        panel.set_alpha(alpha)
        panel.fill((0, 0, 0))
        
        panel_x = 50
        panel_y = (config.SCREEN_HEIGHT - panel_height) // 2
        
        screen.blit(panel, (panel_x, panel_y))
        
        # 텍스트
        y_offset = 20
        for line in text_lines:
            text = font.render(line, True, (255, 255, 255))
            text_x = panel_x + (panel.get_width() - text.get_width()) // 2
            screen.blit(text, (text_x, panel_y + y_offset))
            y_offset += 30
    
    @staticmethod
    def draw_shop_menu(screen, resources, merchant, player, selected_index):
        """상점 메뉴 그리기"""
        font_medium = resources.get_font("main_medium")
        font_small = resources.get_font("main_small")
        
        # 반투명 배경
        panel = pygame.Surface((400, 300))
        panel.set_alpha(230)
        panel.fill((30, 30, 30))
        panel_x = (config.SCREEN_WIDTH - 400) // 2
        panel_y = (config.SCREEN_HEIGHT - 300) // 2
        screen.blit(panel, (panel_x, panel_y))
        
        # 제목
        title = font_medium.render("상인", True, (255, 255, 255))
        screen.blit(title, (panel_x + 20, panel_y + 20))
        
        # 메뉴 항목
        menu_items = [
            f"룰렛 돌리기 ({config.ROULETTE_EGG_COST}알)",
            f"안전 거래 ({config.SAFE_TRADE_EGG_COST}알)",
            "그만두기"
        ]
        
        y_offset = 60
        for i, item in enumerate(menu_items):
            if i == selected_index:
                color = (255, 255, 0)
                prefix = "> "
            else:
                color = (255, 255, 255)
                prefix = "  "
            
            text = font_small.render(prefix + item, True, color)
            screen.blit(text, (panel_x + 30, panel_y + y_offset))
            y_offset += 35
        
        # 황금알 개수
        eggs_text = font_small.render(f"보유: {player.eggs}알", True, (255, 215, 0))
        screen.blit(eggs_text, (panel_x + 20, panel_y + 250))
    
    @staticmethod
    def draw_roulette(screen, resources, roulette_slots, current_index, spin_time, total_spin_time):
        """룰렛 그리기"""
        font_medium = resources.get_font("main_medium")
        font_small = resources.get_font("main_small")
        
        # 룰렛 패널
        panel_size = 400
        panel = pygame.Surface((panel_size, panel_size))
        panel.set_alpha(240)
        panel.fill((20, 20, 20))
        panel_x = (config.SCREEN_WIDTH - panel_size) // 2
        panel_y = (config.SCREEN_HEIGHT - panel_size) // 2
        screen.blit(panel, (panel_x, panel_y))
        
        # 제목
        title = font_medium.render("룰렛", True, (255, 255, 255))
        screen.blit(title, (panel_x + 20, panel_y + 20))
        
        # 룰렛 원형 (간단한 도형으로 표현)
        center_x = panel_x + panel_size // 2
        center_y = panel_y + panel_size // 2
        radius = 120
        
        # 슬롯 수
        slot_count = len(roulette_slots)
        angle_per_slot = 360 / slot_count
        
        # 현재 선택된 슬롯 계산 (회전 중)
        if spin_time > 0:
            # 회전 속도 계산 (빠르게 시작 → 점차 감속)
            progress = spin_time / total_spin_time
            speed_factor = 1.0 - progress  # 1.0에서 0.0으로
            rotation = current_index * angle_per_slot + (360 * 3 * speed_factor)  # 3바퀴 회전
        else:
            rotation = current_index * angle_per_slot
        
        # 슬롯 그리기
        for i, slot in enumerate(roulette_slots):
            start_angle = i * angle_per_slot + rotation
            end_angle = (i + 1) * angle_per_slot + rotation
            
            # 색상 (좋은 효과는 초록, 나쁜 효과는 빨강)
            if slot.effect_type in ["speed_up", "vision_up", "hunger_rate_down", 
                                    "hunger_instant_up", "food_boost", "double_reward"]:
                color = (0, 200, 0)
            else:
                color = (200, 0, 0)
            
            # 호 그리기
            points = []
            points.append((center_x, center_y))
            for angle in range(int(start_angle), int(end_angle) + 1, 5):
                rad = math.radians(angle)
                x = center_x + radius * math.cos(rad)
                y = center_y + radius * math.sin(rad)
                points.append((x, y))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        
        # 화살표 (현재 선택)
        arrow_angle = rotation + 90
        arrow_rad = math.radians(arrow_angle)
        arrow_x = center_x + (radius + 20) * math.cos(arrow_rad)
        arrow_y = center_y + (radius + 20) * math.sin(arrow_rad)
        pygame.draw.polygon(screen, (255, 255, 0), [
            (arrow_x, arrow_y - 10),
            (arrow_x + 15, arrow_y),
            (arrow_x, arrow_y + 10)
        ])
    
    @staticmethod
    def draw_popup(screen, resources, message, duration, elapsed_time):
        """팝업 메시지 그리기"""
        if elapsed_time >= duration:
            return
        
        font = resources.get_font("main_medium")
        
        # 알파 계산 (페이드 인/아웃)
        if elapsed_time < 0.3:
            alpha = int(255 * (elapsed_time / 0.3))
        elif elapsed_time > duration - 0.3:
            alpha = int(255 * ((duration - elapsed_time) / 0.3))
        else:
            alpha = 255
        
        # 텍스트 렌더링
        text = font.render(message, True, (255, 255, 255))
        text.set_alpha(alpha)
        
        # 중앙 배치
        text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    
    @staticmethod
    def draw_death_screen(screen, fade_alpha):
        """사망 화면 (어두워지는 효과)"""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(fade_alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        if fade_alpha >= 200:  # 충분히 어두워지면 텍스트 표시
            font = pygame.font.Font(None, 48)
            text = font.render("배고픔으로 쓰러졌습니다", True, (255, 255, 255))
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

