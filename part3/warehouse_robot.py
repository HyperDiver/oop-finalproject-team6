import pygame
import os # 需要導入 os 來處理路徑
from enum import Enum

# --- 新增：取得目前這個檔案 (warehouse_robot.py) 所在的資料夾路徑 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# --- 新增：組合出 sprites 資料夾的絕對路徑 ---
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")
class RobotAction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class WarehouseRobot:
    def __init__(self, render_mode=None):
        self.cell_size = 64 # 稍微加大一點格子尺寸看起來較舒服
        self.render_mode = render_mode
        self.window = None
        self.clock = None
        self.robot_pos = [0, 0]
        # 用來儲存載入後的圖片 Surface
        self.sprites = {}

    def _load_sprite(self, filename, rotate_angle=0):
        """輔助函式：從 sprites 資料夾載入圖片並縮放到格子大小"""
        
        # --- 修改：使用絕對路徑來組合圖片路徑 ---
        path = os.path.join(SPRITES_DIR, filename)
        
        try:
            # convert_alpha() 對於有透明度的 PNG 很重要，能提升渲染速度
            img = pygame.image.load(path).convert_alpha()
            # 縮放到格子大小
            scaled_img = pygame.transform.scale(img, (self.cell_size, self.cell_size))
            if rotate_angle != 0:
                scaled_img = pygame.transform.rotate(scaled_img, rotate_angle)
            return scaled_img
        except FileNotFoundError:
            # 這裡會印出它試圖尋找的完整路徑，方便你除錯
            print(f"警告: 找不到圖片，路徑為: {path}")
            print("請確認 'sprites' 資料夾是否存在，且裡面有對應的 PNG 檔案。")
            
            # 如果找不到圖片，建立一個亮粉色方塊作為錯誤提示
            fallback = pygame.Surface((self.cell_size, self.cell_size))
            fallback.fill((255, 0, 255)) 
            return fallback

    def _init_pygame(self, rows, cols):
        if self.render_mode == "human" and self.window is None:
            pygame.init()
            # 設定視窗標題
            pygame.display.set_caption("Warehouse Robot RL")
            self.window = pygame.display.set_mode((cols * self.cell_size, rows * self.cell_size))
            self.clock = pygame.time.Clock()

            # --- 載入 Sprites ---
            # 這裡的 Key 對應到 GridObject 的 type_id
            # 請確保你的 sprites 資料夾中有這些圖片
            self.sprites = {
                'robot': self._load_sprite("bot_blue.png"),
                0: self._load_sprite("floor.png"),      # Empty ID
                1: self._load_sprite("wall.png"),       # Obstacle ID
                # 傳送帶需要根據方向預先載入旋轉後的版本
                'conv_right': self._load_sprite("conveyor.png", 0),
                'conv_down':  self._load_sprite("conveyor.png", -90),
                'conv_left':  self._load_sprite("conveyor.png", 180),
                'conv_up':    self._load_sprite("conveyor.png", 90),
                3: self._load_sprite("package.png"),     # Target ID
            }

    def compute_next_pos(self, pos, action: RobotAction):
        r, c = pos
        if action == RobotAction.UP: r -= 1
        elif action == RobotAction.DOWN: r += 1
        elif action == RobotAction.LEFT: c -= 1
        elif action == RobotAction.RIGHT: c += 1
        return [r, c]

    def render_base(self, grid_map):
        if self.render_mode != "human": return
        
        # 填充背景色 (如果地板圖片有透明度才看得到)
        self.window.fill((30, 30, 30))
        
        # 1. 渲染地圖物件
        for r in range(grid_map.rows):
            for c in range(grid_map.cols):
                obj = grid_map.grid[r][c]
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                
                # 根據物件類型取得對應圖片
                sprite_img = None
                if obj.type_id == 2: # 如果是傳送帶，需要特殊處理方向
                    if obj.direction == (0, 1): sprite_img = self.sprites['conv_right']
                    elif obj.direction == (1, 0): sprite_img = self.sprites['conv_down']
                    elif obj.direction == (0, -1): sprite_img = self.sprites['conv_left']
                    elif obj.direction == (-1, 0): sprite_img = self.sprites['conv_up']
                else:
                    # 其他物件直接用 type_id 取圖
                    sprite_img = self.sprites.get(obj.type_id)
                
                # 將圖片傳遞給物件進行渲染
                obj.render(self.window, rect, sprite_img)

        # 2. 渲染機器人 Sprite
        rr, rc = self.robot_pos
        robot_rect = pygame.Rect(rc * self.cell_size, rr * self.cell_size, self.cell_size, self.cell_size)
        self.window.blit(self.sprites['robot'], robot_rect)

        pygame.event.pump()
        pygame.display.flip()
        self.clock.tick(10)