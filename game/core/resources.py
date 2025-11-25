"""
ResourceManager - 이미지/사운드/폰트 키 기반 관리
"""

import pygame
import os
from game.core import config

class ResourceManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        
    def load_image(self, key, path):
        """이미지 로딩"""
        try:
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                self.images[key] = image
                return image
            else:
                # 폴백: 단색 Surface 생성
                fallback = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                fallback.fill((128, 128, 128))  # 회색
                self.images[key] = fallback
                return fallback
        except Exception as e:
            print(f"이미지 로딩 실패 {path}: {e}")
            # 폴백 생성
            fallback = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
            fallback.fill((128, 128, 128))
            self.images[key] = fallback
            return fallback
    
    def get_image(self, key):
        """이미지 가져오기"""
        if key in self.images:
            return self.images[key]
        # 기본 폴백
        fallback = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
        fallback.fill((128, 128, 128))
        self.images[key] = fallback
        return fallback
    
    def load_sound(self, key, path):
        """사운드 로딩"""
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self.sounds[key] = sound
                return sound
            else:
                # 폴백: 무음 사운드 (빈 Sound 객체는 생성 불가하므로 None)
                self.sounds[key] = None
                return None
        except Exception as e:
            print(f"사운드 로딩 실패 {path}: {e}")
            self.sounds[key] = None
            return None
    
    def get_sound(self, key):
        """사운드 가져오기"""
        return self.sounds.get(key, None)
    
    def play_sound(self, key, volume=1.0):
        """사운드 재생"""
        sound = self.get_sound(key)
        if sound:
            sound.set_volume(volume)
            sound.play()
    
    def load_font(self, key, path, size):
        """폰트 로딩"""
        try:
            if os.path.exists(path):
                font = pygame.font.Font(path, size)
                self.fonts[key] = font
                return font
            else:
                # 폴백: 기본 폰트
                font = pygame.font.Font(None, size)
                self.fonts[key] = font
                print(f"폰트 로딩 실패 {path}, 기본 폰트 사용")
                return font
        except Exception as e:
            print(f"폰트 로딩 실패 {path}: {e}")
            # 폴백: 기본 폰트
            font = pygame.font.Font(None, size)
            self.fonts[key] = font
            return font
    
    def get_font(self, key):
        """폰트 가져오기"""
        if key in self.fonts:
            return self.fonts[key]
        # 기본 폴백
        font = pygame.font.Font(None, 24)
        self.fonts[key] = font
        return font
    
    def initialize_defaults(self):
        """기본 리소스 초기화"""
        # 폰트 로딩 (사용자가 제공할 예정)
        font_path = "assets/fonts/kr_main.ttf"
        self.load_font("main_small", font_path, 16)
        self.load_font("main_medium", font_path, 24)
        self.load_font("main_large", font_path, 32)
        self.load_font("main_title", font_path, 48)
        
        # 기본 이미지 (향후 assets/images/에 추가될 예정)
        # 지금은 폴백만 사용

