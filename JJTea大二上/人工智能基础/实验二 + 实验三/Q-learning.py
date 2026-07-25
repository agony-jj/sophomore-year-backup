import numpy as np
import random
import matplotlib.pyplot as plt
from dataclasses import dataclass

# 动作编码
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
ACTIONS = [UP, DOWN, LEFT, RIGHT]
ACTION_DIR = {UP: (-1, 0), DOWN: (1, 0), LEFT: (0, -1), RIGHT: (0, 1)}

@dataclass
class StepResult:
    next_state: tuple
    reward: int
    done: bool

class GridMazeEnv:
    def __init__(self, rows=6, cols=12):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)
        # 底行大部分为陷阱，右下角为终点
        for c in range(cols - 1):
            self.grid[rows - 1, c] = -1
        self.grid[rows - 1, cols - 1] = 2
        # 起点：左下角第二行第一列
        self.start = (rows - 2, 0)
        self.agent = self.start

    def reset(self):
        self.agent = self.start
        return self.agent

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def step(self, action):
        dr, dc = ACTION_DIR[action]
        nr, nc = self.agent[0] + dr, self.agent[1] + dc
        if not self.in_bounds(nr, nc):
            return StepResult(self.agent, -1, False)
        cell = self.grid[nr, nc]
        if cell == 2:  # 终点
            self.agent = (nr, nc)
            return StepResult(self.agent, -1, True)
        if cell == -1:  # 陷阱
            self.agent = (nr, nc)
            return StepResult(self.agent, -100, True)
        self.agent = (nr, nc)
        return StepResult(self.agent, -1, False)

    def render_ascii(self, path=None):
        grid = []
        path_set = set(path or [])
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                if (r, c) == self.start:
                    ch = 'S'
                elif self.grid[r, c] == 2:
                    ch = 'G'
                elif self.grid[r, c] == -1:
                    ch = '#'
                else:
                    ch = '.'
                if (r, c) in path_set and ch not in ('S', 'G'):
                    ch = '*'
                row.append(ch)
            grid.append(' '.join(row))
        print('\n'.join(grid))


class QLearningAgent:
    def __init__(self, env: GridMazeEnv, alpha=0.1, gamma=0.95, epsilon=0.2):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = np.zeros((env.rows, env.cols, len(ACTIONS)), dtype=float)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        r, c = state
        return int(np.argmax(self.Q[r, c]))

    def update(self, s, a, r, s_next, done):
        r0, c0 = s
        r1, c1 = s_next
        best_next = 0.0 if done else np.max(self.Q[r1, c1])
        td_target = r + self.gamma * best_next
        td_error = td_target - self.Q[r0, c0, a]
        self.Q[r0, c0, a] += self.alpha * td_error

    def train(self, episodes=3000, max_steps=200):
        rewards = []
        for ep in range(episodes):
            s = self.env.reset()
            total = 0
            for _ in range(max_steps):
                a = self.choose_action(s)
                result = self.env.step(a)
                self.update(s, a, result.reward, result.next_state, result.done)
                s = result.next_state
                total += result.reward
                if result.done:
                    break
            self.epsilon = max(0.01, self.epsilon * 0.999)
            rewards.append(total)
        return rewards

    def greedy_path(self, max_steps=100):
        s = self.env.reset()
        path = [s]
        total = 0
        for _ in range(max_steps):
            r, c = s
            a = int(np.argmax(self.Q[r, c]))
            result = self.env.step(a)
            path.append(result.next_state)
            total += result.reward
            s = result.next_state
            if result.done:
                break
        return path, total



env = GridMazeEnv(rows=6, cols=12)
agent = QLearningAgent(env, alpha=0.2, gamma=0.98, epsilon=0.3)

print("Training...")
rewards = agent.train(episodes=5000, max_steps=200)

# 绘制奖励曲线（英文坐标）
running_avg = np.convolve(rewards, np.ones(50)/50, mode='valid')
plt.plot(range(len(rewards)), rewards, label="Rewards", color="blue")
plt.plot(range(len(running_avg)), running_avg, label="Running Average", color="orange")
plt.title("Average Learning Curve of Q-learning in Maze Environment")
plt.xlabel("Episodes")
plt.ylabel("Reward")
plt.legend()
plt.show()

print("Greedy rollout (best learned policy):")
path, total_reward = agent.greedy_path(max_steps=50)
env.render_ascii(path=path)
print("Total reward:", total_reward)
print("Steps:", len(path) )