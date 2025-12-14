import numpy as np
import pickle
from collections import deque # 用來記錄最近幾步的位置

class QTrainer:
    def __init__(self, env):
        self.env = env
        self.q_table = {} 
        self.actions = [0, 1, 2, 3]
        
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.9995 # 讓它探索更久一點
        self.epsilon_min = 0.05

    def get_state_key(self, observation):
        """將 numpy array 轉為 tuple"""
        return tuple(observation.tolist())

    def get_q(self, state_key, action):
        return self.q_table.get((state_key, action), 0.0)

    def choose_action(self, state_key):
        # 訓練時的 Epsilon-Greedy
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)
        
        q_values = [self.get_q(state_key, a) for a in self.actions]
        if all(q == 0 for q in q_values):
            return np.random.choice(self.actions)
        return np.argmax(q_values)

    def learn(self, state, action, reward, next_state):
        current_q = self.get_q(state, action)
        max_next_q = max([self.get_q(next_state, a) for a in self.actions])
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q

    def train(self, episodes=1000):
        print("Start Training on Random Maps...")
        for ep in range(episodes):
            obs, _ = self.env.reset()
            state_key = self.get_state_key(obs)
            done = False
            total_reward = 0
            
            while not done:
                action = self.choose_action(state_key)
                next_obs, reward, terminated, truncated, _ = self.env.step(action)
                done = terminated or truncated
                
                next_state_key = self.get_state_key(next_obs)
                self.learn(state_key, action, reward, next_state_key)
                
                state_key = next_state_key
                total_reward += reward
            
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                
            if (ep+1) % 500 == 0:
                print(f"Episode {ep+1}: Reward {total_reward:.1f}, Epsilon {self.epsilon:.2f}, Q-Size {len(self.q_table)}")

    def test(self, episodes=5):
        print("\n--- Test Mode (With Stuck Detection) ---")
        self.epsilon = 0 # 測試時原則上不隨機
        sus=0
        for ep in range(episodes):
            obs, _ = self.env.reset()
            state_key = self.get_state_key(obs)
            done = False
            steps = 0
            
            # --- 防卡死機制設定 ---
            # 記錄最近 5 步的機器人位置
            position_history = deque(maxlen=5) 
            stuck_count = 0
            
            print(f"Testing EP {ep+1}...")
            
            while not done and steps < 100: # 稍微放寬最大步數
                # 1. 取得當前機器人位置 (從 env 獲取)
                # 注意：我們要透過 unwrapped 拿到真實環境來讀取位置
                current_pos = tuple(self.env.unwrapped.robot_pos)
                position_history.append(current_pos)
                
                # 2. 判斷是否卡住
                is_stuck = False
                # 如果歷史紀錄滿了，且最近 5 步內只在 1 或 2 個格子間跳動 (例如 A->B->A->B)
                if len(position_history) == 5 and len(set(position_history)) <= 2:
                    is_stuck = True
                
                # 3. 決定動作
                if is_stuck:
                    # 如果卡住了，強制隨機移動 (嘗試打破僵局)
                    # print("  -> Detected STUCK! Forcing random move.")
                    action = np.random.choice(self.actions)
                    position_history.clear() # 清空歷史，避免連續觸發
                    stuck_count += 1
                else:
                    # 沒卡住，正常使用 Q-Table 最優解
                    action = np.argmax([self.get_q(state_key, a) for a in self.actions])
                
                # 4. 執行
                obs, _, terminated, truncated, _ = self.env.step(action)
                done = terminated or truncated
                state_key = self.get_state_key(obs)
                steps += 1
            
            if steps >= 100: 
                print(f" -> FAILED (Timeout). Stuck triggers: {stuck_count}")
            else: 
                print(f" -> SUCCESS. Steps: {steps}, Stuck triggers: {stuck_count}")
                sus+=1
        print(f"Success Rate: {sus*100/episodes}%")