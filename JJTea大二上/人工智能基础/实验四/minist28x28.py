import torch
import torch.nn as nn
from torchvision import datasets
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
from PIL import Image
import torchvision.transforms as transforms
import pygame
import sys ;sys.setrecursionlimit(sys.getrecursionlimit() * 5)
from pygame.locals import *

class Lenet5(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, (5,5), padding=2)
        self.pool1 = nn.MaxPool2d((2,2))
        self.conv2 = nn.Conv2d(6, 16, (5,5))
        self.pool2 = nn.AvgPool2d((2, 2))
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        # --- 在这里定义前向传播逻辑 ---
        x = self.pool1(torch.relu(self.conv1(x)))
        x = self.pool2(torch.relu(self.conv2(x)))
        x = nn.Flatten()(x)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
training_data = datasets.MNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
)

test_data = datasets.MNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor(),
)

# 训练模型和测试模型的函数
def train(dataloader, model, loss_fn, optimizer):
    model.train()
    for X, y in dataloader:
        X, y = X.to(device), y.to(device)
        pred = model.forward(X)
        loss = loss_fn(pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loss = loss.item()
    print(f"loss: {loss:>7f}")


def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model.forward(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f"Test result: \n Accuracy: {(100 * correct)}%, Avg loss: {test_loss}")


# 检查是否支持CUDA，然后选择设备
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using {device} device")

# 创建数据加载器
train_dataloader = DataLoader(training_data, batch_size=64)
test_dataloader = DataLoader(test_data, batch_size=64)

# 创建模型并传入设备
model = Lenet5().to(device)

# 定义损失函数和优化器
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

# 训练模型
for epoch in range(10):#训练次数
    print(f"Epoch {epoch + 1}\n-------------------------------")
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)

# 定义一个函数来识别手写数字
def recognize_handwritten_digit(image_path, model):
    image = Image.open(image_path).convert('L')

    preprocess = transforms.Compose([
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
    ])
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)
    input_batch = input_batch.to(device)

    with torch.no_grad():
        output = model(input_batch)
    
    _, predicted_class = torch.max(output, 1)
    return predicted_class.item()

# 识别手写数字
def get_handwritten_input():
    pygame.init()

    # 设置窗口
    window = pygame.display.set_mode((280, 280))
    pygame.display.set_caption('Handwritten Input')
    window.fill((0, 0, 0))  # 设置背景为黑色

    drawing = False
    last_pos = None

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                drawing = True
            elif event.type == MOUSEMOTION:
                if drawing:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if last_pos:
                        pygame.draw.line(window, (255, 255, 255), last_pos, (mouse_x, mouse_y), 15)  # 设置绘画颜色为白色
                    last_pos = (mouse_x, mouse_y)
            elif event.type == MOUSEBUTTONUP:
                drawing = False
                last_pos = None
            pygame.display.update()
            if event.type == KEYDOWN and event.key == K_RETURN:
                pygame.image.save(window, 'handwritten_input.png')
                return 'handwritten_input.png'

while True:  # 死循环保证程序一直运行，直到关闭
    image_path = get_handwritten_input()
    predicted_digit = recognize_handwritten_digit(image_path, model)
    print(f"The predicted digit is: {predicted_digit}")