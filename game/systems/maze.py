"""
미로 생성 및 오브젝트 배치
"""

import random
from game.core import config
from game.systems import items
from game.systems import merchant

class SecretRoom:
    """비밀 방"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.items = []
        self.found = False

class Maze:
    """미로 클래스"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []  # 0=벽, 1=길
        self.start_pos = (1, 1)
        self.exit_pos = (width - 2, height - 2)
        self.items_list = []
        self.merchants = []
        self.secret_rooms = []
    
    def generate(self, stats):
        """미로 생성 (seed 기반)"""
        # seed 설정
        if stats.random_seed is not None:
            random.seed(stats.random_seed)
        else:
            stats.random_seed = random.randint(0, 2**31 - 1)
            random.seed(stats.random_seed)
        
        # 그리드 초기화 (모두 벽)
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # DFS로 미로 생성
        self._generate_dfs()
        
        # 오브젝트 배치
        self._place_items(stats)
        self._place_merchants(stats)
        self._place_secret_rooms(stats)
    
    def _generate_dfs(self):
        """DFS 알고리즘으로 미로 생성"""
        stack = [self.start_pos]
        visited = set([self.start_pos])
        
        # 시작점을 길로
        self.grid[self.start_pos[1]][self.start_pos[0]] = 1
        
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # 상하좌우 (2칸씩)
        
        while stack:
            current = stack[-1]
            x, y = current
            
            # 인접한 미방문 셀 찾기
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 < nx < self.width - 1 and 0 < ny < self.height - 1 and 
                    (nx, ny) not in visited):
                    neighbors.append((nx, ny))
            
            if neighbors:
                # 랜덤하게 선택
                next_cell = random.choice(neighbors)
                nx, ny = next_cell
                
                # 중간 벽 제거
                mid_x, mid_y = (x + nx) // 2, (y + ny) // 2
                self.grid[mid_y][mid_x] = 1
                self.grid[ny][nx] = 1
                
                visited.add(next_cell)
                stack.append(next_cell)
            else:
                stack.pop()
        
        # 출구 확보
        self.grid[self.exit_pos[1]][self.exit_pos[0]] = 1
    
    def _place_items(self, stats):
        """아이템 배치"""
        self.items_list = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 1:  # 길인 경우
                    if random.random() < config.ITEM_DENSITY:
                        # 황금알 또는 음식 랜덤 배치
                        if random.random() < 0.3:  # 30% 확률로 황금알
                            item = items.GoldenEgg(x * config.TILE_SIZE, y * config.TILE_SIZE)
                        else:
                            item = items.Food(x * config.TILE_SIZE, y * config.TILE_SIZE)
                        self.items_list.append(item)
    
    def _place_merchants(self, stats):
        """상인 배치"""
        self.merchants = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 1:  # 길인 경우
                    # 시작점과 출구 근처는 제외
                    if (abs(x - self.start_pos[0]) < 3 and abs(y - self.start_pos[1]) < 3):
                        continue
                    if (abs(x - self.exit_pos[0]) < 3 and abs(y - self.exit_pos[1]) < 3):
                        continue
                    
                    if random.random() < config.MERCHANT_DENSITY:
                        m = merchant.Merchant(x * config.TILE_SIZE, y * config.TILE_SIZE)
                        self.merchants.append(m)
    
    def _place_secret_rooms(self, stats):
        """비밀 방 배치"""
        self.secret_rooms = []
        
        # 벽 후보 찾기
        wall_candidates = []
        for y in range(2, self.height - 2):
            for x in range(2, self.width - 2):
                if self.grid[y][x] == 0:  # 벽
                    # 주변에 길이 있는지 확인
                    has_path_nearby = False
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.grid[ny][nx] == 1:
                                has_path_nearby = True
                                break
                    
                    if has_path_nearby and random.random() < config.SECRET_ROOM_CHANCE:
                        wall_candidates.append((x, y))
        
        # 비밀 방 생성
        for x, y in wall_candidates[:3]:  # 최대 3개
            secret_room = SecretRoom(x * config.TILE_SIZE, y * config.TILE_SIZE)
            # 비밀 방에 SecretItem 배치
            secret_item = items.SecretItem(x * config.TILE_SIZE, y * config.TILE_SIZE)
            secret_room.items.append(secret_item)
            self.secret_rooms.append(secret_room)
            # 비밀 방 위치의 아이템 리스트에도 추가
            self.items_list.append(secret_item)
    
    def is_walkable(self, tile_x, tile_y):
        """타일이 이동 가능한지 확인"""
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False
        return self.grid[tile_y][tile_x] == 1
    
    def get_item_at(self, x, y):
        """위치의 아이템 가져오기"""
        tile_x = int(x / config.TILE_SIZE)
        tile_y = int(y / config.TILE_SIZE)
        
        for item in self.items_list:
            item_tile_x = int(item.x / config.TILE_SIZE)
            item_tile_y = int(item.y / config.TILE_SIZE)
            if item_tile_x == tile_x and item_tile_y == tile_y and not item.picked:
                return item
        return None
    
    def get_merchant_at(self, x, y, radius=1):
        """위치 근처의 상인 가져오기"""
        tile_x = int(x / config.TILE_SIZE)
        tile_y = int(y / config.TILE_SIZE)
        
        for m in self.merchants:
            m_tile_x, m_tile_y = m.get_tile_pos()
            if abs(m_tile_x - tile_x) <= radius and abs(m_tile_y - tile_y) <= radius:
                return m
        return None
    
    def get_secret_room_at(self, x, y):
        """위치의 비밀 방 가져오기"""
        tile_x = int(x / config.TILE_SIZE)
        tile_y = int(y / config.TILE_SIZE)
        
        for room in self.secret_rooms:
            room_tile_x = int(room.x / config.TILE_SIZE)
            room_tile_y = int(room.y / config.TILE_SIZE)
            if room_tile_x == tile_x and room_tile_y == tile_y:
                return room
        return None
    
    def is_exit(self, tile_x, tile_y):
        """출구인지 확인"""
        return tile_x == self.exit_pos[0] and tile_y == self.exit_pos[1]

