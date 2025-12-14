import random
from collections import deque
import numpy as np
from grid_objects import Empty, Obstacle, Conveyor, Target

class GridMap:
    def __init__(self, rows, cols, num_obstacles=4, num_conveyors=2):
        self.rows = rows
        self.cols = cols
        self.num_obstacles = num_obstacles
        self.num_conveyors = num_conveyors
        self.grid = []
        self.target_pos = None
        self.regenerate_map()

    def regenerate_map(self):
        """生成一張隨機但保證可解的地圖"""
        while True:
            self._generate_random_layout()
            if self._is_reachable((0, 0), self.target_pos):
                break

    def _generate_random_layout(self):
        self.grid = [[Empty() for _ in range(self.cols)] for _ in range(self.rows)]
        available_coords = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        if (0, 0) in available_coords: available_coords.remove((0, 0))
        random.shuffle(available_coords)

        # 放置物件
        for _ in range(self.num_obstacles):
            if available_coords: self.grid[available_coords.pop()[0]][available_coords.pop()[1]] = Obstacle()
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for _ in range(self.num_conveyors):
            if available_coords: 
                r, c = available_coords.pop()
                self.grid[r][c] = Conveyor(random.choice(directions))

        if available_coords:
            r, c = available_coords.pop()
            self.grid[r][c] = Target()
            self.target_pos = (r, c)

    def _is_reachable(self, start, end):
        """BFS 檢查路徑"""
        if not end: return False
        queue = deque([start])
        visited = set([start])
        while queue:
            r, c = queue.popleft()
            if (r, c) == end: return True
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) not in visited and self.grid[nr][nc].type_id != 1:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return False

    def get_object_at(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c]
        return Obstacle() # 邊界外視為牆壁

    def get_local_observation(self, robot_pos):
        """
        局部觀察 (Local Sensing):
        回傳: [目標主要方位, 上方物件ID, 右方物件ID, 下方物件ID, 左方物件ID]
        """
        rr, rc = robot_pos
        tr, tc = self.target_pos

        # 1. 計算目標相對方位 (簡化為 4 個方向)
        # 0:上, 1:右, 2:下, 3:左
        dr = tr - rr
        dc = tc - rc
        if abs(dr) > abs(dc): # 垂直距離較大
            target_dir = 0 if dr < 0 else 2
        else: # 水平距離較大
            target_dir = 3 if dc < 0 else 1

        # 2. 獲取四周物件狀態 (上, 右, 下, 左)
        surroundings = []
        check_dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for cdr, cdc in check_dirs:
            nr, nc = rr + cdr, rc + cdc
            # 邊界外當作牆壁(1)
            obj_type = 1
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                obj_type = self.grid[nr][nc].type_id
            surroundings.append(obj_type)

        # 組合結果 [Dir, Up, Right, Down, Left]
        return np.array([target_dir] + surroundings, dtype=np.int32)