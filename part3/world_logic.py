import random
import pygame
from warehouse_robot import WarehouseRobot, RobotAction

class ConveyorWorld(WarehouseRobot):
    def __init__(self, grid_rows=4, grid_cols=5, num_obstacles=3, num_conveyors=2, fps=10):
        super().__init__(grid_rows, grid_cols, fps)
        self.num_obstacles = num_obstacles
        self.num_conveyors = num_conveyors
        self.obstacles = set()
        self.conveyors = {} # (r,c) -> (dr, dc)

    def reset(self, seed=None):
        super().reset(seed)
        self._generate_map()
        return self.robot_pos

    def _generate_map(self):
        """Generates random obstacles and conveyors ensuring paths exist"""
        self.obstacles.clear()
        self.conveyors.clear()
        
        # 1. Generate Obstacles
        attempts = 0
        while len(self.obstacles) < self.num_obstacles and attempts < 100:
            r = random.randint(0, self.grid_rows - 1)
            c = random.randint(0, self.grid_cols - 1)
            pos = [r, c]
            if pos != self.robot_pos and pos != self.target_pos:
                self.obstacles.add((r, c))
            attempts += 1
            
        # 2. Generate Conveyors
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # R, L, D, U
        while len(self.conveyors) < self.num_conveyors:
            r = random.randint(0, self.grid_rows - 1)
            c = random.randint(0, self.grid_cols - 1)
            if (r, c) not in self.obstacles and [r, c] != self.robot_pos and [r, c] != self.target_pos:
                self.conveyors[(r, c)] = random.choice(directions)

    def perform_action(self, action: RobotAction):
        # 1. Intended movement
        old_r, old_c = self.robot_pos
        dr, dc = 0, 0
        if action == RobotAction.LEFT: dc = -1
        elif action == RobotAction.RIGHT: dc = 1
        elif action == RobotAction.UP: dr = -1
        elif action == RobotAction.DOWN: dr = 1

        new_r, new_c = old_r + dr, old_c + dc
        
        # Bounds check
        new_r = max(0, min(self.grid_rows - 1, new_r))
        new_c = max(0, min(self.grid_cols - 1, new_c))

        # 2. Obstacle Collision Check
        hit_obstacle = False
        if (new_r, new_c) in self.obstacles:
            new_r, new_c = old_r, old_c # Bounce back
            hit_obstacle = True

        # Update position temporarily
        self.robot_pos = [new_r, new_c]

        # 3. Apply Conveyor Belt Effect
        on_conveyor = False
        if (new_r, new_c) in self.conveyors:
            on_conveyor = True
            cdr, cdc = self.conveyors[(new_r, new_c)]
            cr, cc = new_r + cdr, new_c + cdc
            
            # Check bounds for conveyor push
            if 0 <= cr < self.grid_rows and 0 <= cc < self.grid_cols:
                # Conveyor cannot push into obstacle
                if (cr, cc) not in self.obstacles:
                    self.robot_pos = [cr, cc]

        # Return status for Reward calculation
        return {
            'pos': self.robot_pos,
            'hit_obstacle': hit_obstacle,
            'reached_target': self.robot_pos == self.target_pos,
            'on_conveyor': on_conveyor
        }

    def _render_custom_layers(self):
        # Draw Obstacles (Red squares)
        for (r, c) in self.obstacles:
            x = c * self.cell_width
            y = r * self.cell_height
            pygame.draw.rect(self.window_surface, (150, 0, 0), (x+5, y+5, 54, 54))

        # Draw Conveyors (Cyan Arrows)
        for (r, c), (dr, dc) in self.conveyors.items():
            cx = c * self.cell_width + 32
            cy = r * self.cell_height + 32
            # Draw base circle
            pygame.draw.circle(self.window_surface, (0, 200, 255), (cx, cy), 15)
            # Draw simple direction indicator
            ex, ey = cx + dc*20, cy + dr*20
            pygame.draw.line(self.window_surface, (0, 0, 100), (cx, cy), (ex, ey), 4)