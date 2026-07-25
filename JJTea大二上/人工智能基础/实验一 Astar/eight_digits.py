#人工智能基础实验1：用A*算法8数码问题
#使用time模块计算每种算法的运行时间
import time
from collections import deque
import heapq

#以元组存储每个数子的位置，空格以0表示
#表示出初始状态和目标状态
start_s = [(2,2),(3,3),(1,2),(3,2),(1,3),(2,1),(2,3),(1,1),(3,1)]
goal_s = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3)]


#启发函数第一种定义为当前状态与目标状态中每个数字的曼哈顿距离之和
#证明一致性：
#每次移动的代价c(n, n') = 1
#|h(n) - h(n')| <= 1
#所以 h(n) <= c(n, n') + h(n')
def h1(s):
    distance = 0
    for i in range(0,9):
        curr_pos = s[i]
        goal_pos = goal_s[i]
        distance += abs(curr_pos[0] - goal_pos[0]) + abs(curr_pos[1] - goal_pos[1])
    return distance


#启发函数的第二种定义为当前状态与目标状态中每个数字的欧几里得距离之和
#证明一致性：
#每次移动的代价 c(n, n') = 1
#根据三角形不等式可知：|h(n) - h(n')| <= 1
#所以 h(n) <= c(n, n') + h(n')
def h2(s):
    distance = 0
    for i in range(0,9):
        curr_pos = s[i]
        goal_pos = goal_s[i]
        distance += ((curr_pos[0] - goal_pos[0])**2 + (curr_pos[1] - goal_pos[1])**2)**0.5
    return distance


#启发函数第三种定义为当前状态与目标状态中不在同一位置的数子个数
#证明一致性：
#每次移动的代价 c(n, n') = 1
#-1 <= h(n) - h(n') <= 1
#所以 h(n) <= c(n, n') + h(n')
def h3(s):
    count = 0
    for i in range(0,9):
        if s[i] != goal_s[i]:
            count += 1
    return count



#每次移动空格与其上下左右的数字交换位置，实现状态转移
# 生成所有合法邻居状态
def get_neighbors(s):
    neighbors = []
    moves = [(-1,0),(1,0),(0,-1),(0,1)]  # 上下左右
    zero_pos = s[0]
    for dx, dy in moves:
        nx, ny = zero_pos[0] + dx, zero_pos[1] + dy
        # 筛选出合法的位置
        if 1 <= nx <= 3 and 1 <= ny <= 3:
            # 找到要与空格交换的数字下标
            k = next(i for i, p in enumerate(s) if p == (nx, ny))
            #ns means next state
            ns = list(s)
            ns[0], ns[k] = ns[k], ns[0]
            neighbors.append(tuple(ns))
    return neighbors



# A* 搜索 + 启发函数h1
def astarh1(start):
    start = tuple(start)
    pq = [(h1(list(start)), 0, [start])]  # (f=g+h, g, 路径)
    visited_cost = {start: 0}
    while pq:
        f, g, path = heapq.heappop(pq)
        cur = path[-1]
        if list(cur) == goal_s:
            return [list(p) for p in path]
        for nbr in get_neighbors(list(cur)):
            ng = g + 1 #每一步的代价为1，以此更新g
            if nbr not in visited_cost or ng < visited_cost[nbr]:
                visited_cost[nbr] = ng
                heapq.heappush(pq, (ng + h1(list(nbr)), ng, path + [nbr]))
    return []


# A* 搜索 + 启发式函数h2
def astarh2(start):
    start = tuple(start)
    pq = [(h2(list(start)), 0, [start])]  # (f=g+h, g, 路径)
    visited_cost = {start: 0}
    while pq:
        f, g, path = heapq.heappop(pq)
        cur = path[-1]
        if list(cur) == goal_s:
            return [list(p) for p in path]
        for nbr in get_neighbors(list(cur)):
            ng = g + 1 #每一步的代价为1，以此更新g
            if nbr not in visited_cost or ng < visited_cost[nbr]:
                visited_cost[nbr] = ng
                heapq.heappush(pq, (ng + h2(list(nbr)), ng, path + [nbr]))
    return []


# A* 搜索 + 启发式函数h3
def astarh3(start):
    start = tuple(start)
    pq = [(h3(list(start)), 0, [start])]  # (f=g+h, g, 路径)
    visited_cost = {start: 0}
    while pq:
        f, g, path = heapq.heappop(pq)
        cur = path[-1]
        if list(cur) == goal_s:
            return [list(p) for p in path]
        for nbr in get_neighbors(list(cur)):
            ng = g + 1 #每一步的代价为1，以此更新g
            if nbr not in visited_cost or ng < visited_cost[nbr]:
                visited_cost[nbr] = ng
                heapq.heappush(pq, (ng + h3(list(nbr)), ng, path + [nbr]))
    return []



# 定义打印结果的函数
def print_state(s):
    start = 0
    target = [[0 for i in range(3)] for j in range(3)] 
    for i,j in s:
        target[i-1][j-1] = start
        start += 1
    print("-------------")
    for i in range(3):
        print("|",end="")
        for j in range(3):
            if target[i][j] == 0:
                print("   |",end="")
            else:
                print(" %d |"%target[i][j],end="")
        print("\n-------------")


def print_path(path):
    print(f"初始状态为:")
    print_state(path[0])
    print("搜索路径如下：")
    for i in range(len(path)):
        if i == 0:
            continue
        print(f"Step {i}:")
        print_state(path[i])
        if i != len(path) - 1: 
            print("      |      ")
            print("      V      ")



# 运行并计时
algos = [
    ("A* + h1", astarh1),
    ("A* + h2", astarh2),
    ("A* + h3", astarh3),

]

for name, func in algos:
    #得到时间戳
    t0 = time.perf_counter()
    path = func(start_s)
    t1 = time.perf_counter()
    print(f"\n>>> {name} 用时 {t1 - t0:.4f} 秒，步数 {len(path)-1 if path else '未找到'}")
    # 可选择的打印路径
    printpath = True if func == astarh3 else False
    if path and printpath:
        print_path(path)

