import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
import numpy as np
from warehouse_robot import WarehouseRobot, RobotAction
from grid_map import GridMap
from grid_objects import InteractionType

class RobotEnvironment(WarehouseRobot, gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 10}

    def __init__(self, render_mode=None, rows=5, cols=5, random_reset=True):
        WarehouseRobot.__init__(self, render_mode)
        gym.Env.__init__(self)

        self.rows = rows
        self.cols = cols
        self.random_reset = random_reset
        self.map = GridMap(rows, cols, num_obstacles=4, num_conveyors=2)
        
        self.action_space = spaces.Discrete(4)
        
        # --- 局部觀察空間 ---
        # [目標方向(4), 上(4), 右(4), 下(4), 左(4)]
        # 每個位置的數值範圍是 0~3 (對應 GridObject type_id)
        self.observation_space = spaces.MultiDiscrete([4, 4, 4, 4, 4])

        self._init_pygame(rows, cols)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if self.random_reset:
            self.map.regenerate_map()
            
        self.robot_pos = [0, 0]
        # 使用局部觀察
        obs = self.map.get_local_observation(self.robot_pos)
        
        if self.render_mode == "human": self.render()
        return obs, {}

    def step(self, action_idx):
        action = RobotAction(action_idx)
        reward = 0
        terminated = False
        
        next_pos = self.compute_next_pos(self.robot_pos, action)
        target_obj = self.map.get_object_at(next_pos[0], next_pos[1])
        result = target_obj.interact()
        
        if result["type"] == InteractionType.BLOCKED:
            reward = -2.0 # 撞牆懲罰加重
        
        elif result["type"] == InteractionType.WIN:
            self.robot_pos = next_pos
            reward = 20.0
            terminated = True
            
        elif result["type"] == InteractionType.SLIDE:
            self.robot_pos = next_pos 
            dr, dc = result["dir"]
            slide_pos = [self.robot_pos[0] + dr, self.robot_pos[1] + dc]
            
            # 檢查傳送後是否撞牆
            slide_obj = self.map.get_object_at(slide_pos[0], slide_pos[1])
            slide_res = slide_obj.interact()
            
            if slide_res["type"] != InteractionType.BLOCKED:
                self.robot_pos = slide_pos
            
        else:
            self.robot_pos = next_pos

        # 使用局部觀察
        obs = self.map.get_local_observation(self.robot_pos)
        
        if self.render_mode == "human": self.render()

        return obs, reward, terminated, False, {}

    def render(self):
        super().render_base(self.map)

register(
    id='WarehouseRobot-v0',
    entry_point='robot_env:RobotEnvironment',
    kwargs={'random_reset': True}, # 預設開啟隨機地圖
    max_episode_steps=100,
)