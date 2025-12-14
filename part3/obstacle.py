import random
from collections import deque
import numpy as np
import pygame
from os import path

import warehouse_robot as wr


class Obstacles(wr.WarehouseRobot):
    """
    World with static obstacles.
    Inherits basic robot movement and extends collision rules.
    """

    def __init__(self, grid_rows=4, grid_cols=5, fps=4, num_obstacles=3):
        self.num_obstacles = num_obstacles
        self.obstacles = set()
        super().__init__(grid_rows=grid_rows, grid_cols=grid_cols, fps=fps)

    # ===============================
    # Init / Reset
    # ===============================

    def reset(self, seed=None):
        super().reset(seed=seed)
        self._generate_obstacles()
        return self.get_observation()

    # ===============================
    # Obstacle generation
    # ===============================

    def _generate_obstacles(self):
        """
        Randomly generate obstacles,
        ensure robot can still reach target.
        """
        while True:
            self.obstacles.clear()

            while len(self.obstacles) < self.num_obstacles:
                r = random.randint(0, self.grid_rows - 1)
                c = random.randint(0, self.grid_cols - 1)

                if [r, c] != self.robot_pos and [r, c] != self.target_pos:
                    self.obstacles.add((r, c))

            if self._is_reachable():
                break

    def _is_reachable(self):
        """BFS check reachability"""
        q = deque([tuple(self.robot_pos)])
        visited = set(q)

        while q:
            r, c = q.popleft()
            if [r, c] == self.target_pos:
                return True

            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < self.grid_rows and
                    0 <= nc < self.grid_cols and
                    (nr, nc) not in visited and
                    (nr, nc) not in self.obstacles
                ):
                    visited.add((nr, nc))
                    q.append((nr, nc))

        return False

    # ===============================
    # Movement (核心多型)
    # ===============================

    def perform_action(self, robot_action: wr.RobotAction) -> bool:
        r, c = self.robot_pos
        new_r, new_c = r, c

        if robot_action == wr.RobotAction.LEFT:
            new_c -= 1
        elif robot_action == wr.RobotAction.RIGHT:
            new_c += 1
        elif robot_action == wr.RobotAction.UP:
            new_r -= 1
        elif robot_action == wr.RobotAction.DOWN:
            new_r += 1

        # 邊界限制
        new_r = max(0, min(self.grid_rows - 1, new_r))
        new_c = max(0, min(self.grid_cols - 1, new_c))

        # 碰到障礙物 → 不動
        if (new_r, new_c) not in self.obstacles:
            self.robot_pos = [new_r, new_c]

        return self.robot_pos == self.target_pos

    # ===============================
    # Observation
    # ===============================

    def get_observation(self):
        """
        Observation for debugging or extended training
        """
        obs = [
            self.robot_pos[0],
            self.robot_pos[1],
            self.target_pos[0],
            self.target_pos[1],
        ]
        return np.array(obs, dtype=np.int32)

    # ===============================
    # Rendering
    # ===============================

    def _init_pygame(self):
        super()._init_pygame()
        img_path = path.join(path.dirname(__file__), "sprites/obstacle.png")
        img = pygame.image.load(img_path)
        self.obstacle_img = pygame.transform.scale(img, self.cell_size)

    def render(self):
        super().render()
        for (r, c) in self.obstacles:
            pos = (c * self.cell_width, r * self.cell_height)
            self.window_surface.blit(self.obstacle_img, pos)

        pygame.display.update()
        self.clock.tick(self.fps)
