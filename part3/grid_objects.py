import pygame
from enum import Enum, auto

class InteractionType(Enum):
    NONE = auto()
    BLOCKED = auto()
    SLIDE = auto()
    WIN = auto()

# --- Base Class ---
class GridObject:
    def __init__(self, type_id, color_fallback):
        self.type_id = type_id 
        self.color_fallback = color_fallback # 如果圖片載入失敗時的備用顏色

    def render(self, surface, rect, img_surface=None):
        """
        接收預先載入好的圖片 Surface 進行渲染。
        如果圖片不存在，則繪製備用顏色方塊。
        """
        if img_surface:
            # 將圖片繪製到指定矩陣位置
            surface.blit(img_surface, rect)
        else:
            # 備用方案
            pygame.draw.rect(surface, self.color_fallback, rect)

    def interact(self) -> dict:
        return {"type": InteractionType.NONE}

# --- Subclasses ---
class Empty(GridObject):
    def __init__(self):
        # 備用顏色: 淺灰
        super().__init__(0, (240, 240, 240))

class Obstacle(GridObject):
    def __init__(self):
        # 備用顏色: 深灰
        super().__init__(1, (100, 100, 100))

    def interact(self):
        return {"type": InteractionType.BLOCKED}

class Conveyor(GridObject):
    def __init__(self, direction):
        # 備用顏色: 淺藍
        super().__init__(2, (200, 200, 255))
        self.direction = direction # (dr, dc)

    def interact(self):
        return {"type": InteractionType.SLIDE, "dir": self.direction}
    
    # 注意：Conveyor 不再需要 override render 方法
    # 因為旋轉邏輯已經在 warehouse_robot 載入圖片時處理好了，
    # 這裡只需要使用基底類別的 blit 即可。

class Target(GridObject):
    def __init__(self):
        # 備用顏色: 綠色
        super().__init__(3, (0, 200, 0))

    def interact(self):
        return {"type": InteractionType.WIN}