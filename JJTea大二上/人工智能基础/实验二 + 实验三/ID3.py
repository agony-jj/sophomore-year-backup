import math
from collections import Counter
import matplotlib.pyplot as plt

# 定义计算熵的函数
def entropy(data):
    labels = [row[-1] for row in data]
    label_counts = Counter(labels)
    total = len(data)
    return -sum((count/total) * math.log2(count/total) for count in label_counts.values())

# 按特征划分
def split_dataset(data, feature_index, value):
    return [row for row in data if row[feature_index] == value]

# 定义计算信息增益的函数
def info_gain(data, feature_index):
    base_entropy = entropy(data)
    values = set(row[feature_index] for row in data)
    new_entropy = 0.0
    for v in values:
        subset = split_dataset(data, feature_index, v)
        prob = len(subset) / len(data)
        new_entropy += prob * entropy(subset)
    return base_entropy - new_entropy

# 选择最佳特征
def choose_best_feature(data):
    num_features = len(data[0]) - 1
    best_gain = -1
    best_feature = -1
    for i in range(num_features):
        gain = info_gain(data, i)
        if gain > best_gain:
            best_gain = gain
            best_feature = i
    return best_feature, best_gain

# 多数类
def majority_class(data):
    labels = [row[-1] for row in data]
    return Counter(labels).most_common(1)[0][0]

# 构建树（带深度限制和预剪枝）
def build_tree(data, features, depth=0, max_depth=5, min_gain=0.01):
    labels = [row[-1] for row in data]
    if labels.count(labels[0]) == len(labels):
        return labels[0]
    if len(data[0]) == 1 or depth >= max_depth:
        return majority_class(data)

    best_feature, gain = choose_best_feature(data)
    if gain < min_gain:  # 预剪枝：信息增益太小就停止
        return majority_class(data)

    best_feature_name = features[best_feature]
    tree = {best_feature_name: {}}

    values = set(row[best_feature] for row in data)
    for v in values:
        subset = split_dataset(data, best_feature, v)
        sub_features = features[:best_feature] + features[best_feature+1:]
        subtree = build_tree([row[:best_feature] + row[best_feature+1:] for row in subset],
                             sub_features, depth+1, max_depth, min_gain)
        tree[best_feature_name][v] = subtree
    return tree

# 分类
def classify(tree, features, sample):
    if not isinstance(tree, dict):
        return tree
    root = next(iter(tree))
    feature_index = features.index(root)
    feature_value = sample[feature_index]
    if feature_value in tree[root]:
        subtree = tree[root][feature_value]
        new_features = features[:feature_index] + features[feature_index+1:]
        new_sample = sample[:feature_index] + sample[feature_index+1:]
        return classify(subtree, new_features, new_sample)
    else:
        return None

# 数据加载
def load_dataset(filename):
    dataset = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("traindata") or line.startswith("];"):
                continue
            parts = line.split()
            features = list(map(float, parts[:-1]))
            label = int(parts[-1])
            dataset.append(features + [label])
    return dataset

# 计算子树宽度
def get_tree_width(tree):
    if not isinstance(tree, dict):
        return 1
    root = next(iter(tree))
    return sum(get_tree_width(subtree) for subtree in tree[root].values())

# 绘制树（带分裂值标注）
def plot_tree(tree, x, y, dx, dy, ax):
    if not isinstance(tree, dict):
        ax.text(x, y, str(tree), ha="center", va="center",
                bbox=dict(boxstyle="round", facecolor="lightblue"))
        return
    root = next(iter(tree))
    ax.text(x, y, root, ha="center", va="center",
            bbox=dict(boxstyle="round", facecolor="lightgreen"))
    children = list(tree[root].items())
    total_width = sum(get_tree_width(subtree) for _, subtree in children)
    cur_x = x - total_width/2 * dx
    for val, subtree in children:
        w = get_tree_width(subtree)
        child_x = cur_x + w*dx/2
        child_y = y - dy
        ax.plot([x, child_x], [y, child_y], "k-")
        ax.text((x+child_x)/2, (y+child_y)/2, str(val), ha="center", va="center", fontsize=8, color="red")
        plot_tree(subtree, child_x, child_y, dx, dy, ax)
        cur_x += w*dx

# 运行主程序
if __name__ == "__main__":
    traindata = load_dataset("pypy\\traindata.txt")
    testdata = load_dataset("pypy\\testdata.txt")

    features = ["f0", "f1", "f2", "f3"]
    tree = build_tree(traindata, features, max_depth=5, min_gain=0.01)

    # 准确率
    correct = sum(1 for sample in testdata if classify(tree, features, sample[:-1]) == sample[-1])
    accuracy = correct / len(testdata)
    print("测试集准确率:", accuracy)

    # 绘制树
    fig, ax = plt.subplots(figsize=(12, 8))
    plot_tree(tree, 0, 0, 2, 2, ax)
    ax.axis("off")
    plt.show()