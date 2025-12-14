import gymnasium as gym
import robot_env # Trigger register
from trainer import QTrainer

if __name__ == "__main__":
    # 1. 訓練
    # random_reset=True: 每次地圖都不同，強迫學習局部規則
    env_train = gym.make('WarehouseRobot-v0', render_mode=None, random_reset=True)
    
    trainer = QTrainer(env_train)
    # 局部觀察的狀態組合約 1024 種，建議訓練 5000 次讓它看過各種排列組合
    trainer.train(episodes=5000)
    env_train.close()

    # 2. 測試
    env_test = gym.make('WarehouseRobot-v0', render_mode="human", random_reset=True)
    trainer.env = env_test
    trainer.test(episodes=10)
    env_test.close()