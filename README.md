# Env Controller 命令行工具 （AI generated）

这是一个用于控制远程环境并获取截图的命令行工具。

## 功能特点

- 初始化 env_controller 连接到远程服务器
- 循环接受用户命令并执行
- 支持两种命令格式：
  - 直接执行 Python 表达式
  - JSON 格式的动作指令
- 每个命令执行后等待 2 秒并获取截图
- 自动保存并尝试打开截图

## 项目结构

```
gui/
├── env_controller/          # 环境控制器模块
│   ├── actions.py          # 动作定义
│   └── controller.py       # 控制器实现
├── server/                 # 服务器端代码
│   ├── main.py             # Flask 服务器
│   ├── pyxcursor.py        # 光标处理
│   └── requirements.txt    # 服务器依赖
├── quick_start.py          # 命令行工具脚本
└── README.md               # 项目说明文档
```

## 安装依赖

### 服务器端依赖

```bash
cd server
pip install -r requirements.txt
```

### 客户端依赖

客户端需要安装以下依赖：

```bash
pip install requests
```

若使用gui界面，需要安装pillow库

```bash
pip install pillow
```

## 启动服务器

在服务器端执行以下命令启动 Flask 服务器：

```bash
cd server
python main.py
```

服务器将在 http://0.0.0.0:5000 上运行。

## 使用命令行工具

在客户端执行以下命令启动命令行工具：

```bash
python quick_start.py --ip <服务器IP> --port <服务器端口>
```

参数说明：
- `--ip`: 服务器 IP 地址，默认为 localhost
- `--port`: 服务器端口，默认为 5000

### GUI界面

除了命令行工具外，我们还提供了一个图形用户界面（GUI），具有以下功能：

- 每秒自动更新截图
- 允许直接点击截图执行对应位置的点击操作
- 支持截图缩放
- 实时显示连接状态

### 运行GUI界面

```bash
python gui_interface.py
```

### GUI界面使用说明

1. **连接服务器**：
   - 在顶部输入服务器IP和端口
   - 点击"连接"按钮

2. **截图显示**：
   - 连接成功后，界面会每秒自动更新截图
   - 可以使用缩放滑块调整截图大小

3. **点击操作**：
   - 直接点击截图上的任意位置
   - 系统会自动将点击位置转换为服务器屏幕坐标
   - 在对应位置执行点击操作
   - 点击后会显示红色反馈圆圈

4. **断开连接**：
   - 点击"断开"按钮可以断开与服务器的连接

## 命令行工具使用说明

### 命令格式

1. **执行 Python 表达式**

   直接输入 Python 表达式，将在服务器上执行：

   ```
   pyautogui.moveTo(100, 100)
   pyautogui.click()
   pyautogui.typewrite('Hello World')
   ```

2. **JSON 格式的动作指令**

   输入 JSON 格式的动作指令，支持的动作类型包括：MOVE_TO、CLICK、RIGHT_CLICK、DOUBLE_CLICK、DRAG_TO、SCROLL、TYPING、PRESS、KEY_DOWN、KEY_UP、HOTKEY 等。

   示例：

   ```json
   {"action_type": "CLICK", "x": 100, "y": 100}
   {"action_type": "TYPING", "text": "Hello World"}
   {"action_type": "HOTKEY", "keys": ["ctrl", "c"]}
   ```

### 退出程序

输入 `exit` 或 `quit` 退出程序。

### 截图功能

每个命令执行后，工具将：
1. 等待 2 秒
2. 从服务器获取截图
3. 将截图保存到 `screenshots` 目录
4. 尝试使用系统默认图像查看器打开截图

## 示例使用流程

### 使用GUI界面

1. 启动服务器

   ```bash
   cd server
   python main.py
   ```

2. 启动GUI界面

   ```bash
   python gui_interface.py
   ```

3. 在GUI界面中连接服务器并进行操作

### 使用命令行工具

1. 启动服务器

   ```bash
   cd server
   python main.py
   ```

2. 启动命令行工具

   ```bash
   python quick_start.py --ip localhost --port 5000
   ```

3. 执行命令

   ```
   === Env Controller命令行工具 ===
   输入 'exit' 或 'quit' 退出程序
   输入命令以执行操作，支持以下命令格式：
   - 直接输入Python表达式（将在服务器上执行）
   - 输入JSON格式的动作指令（如：{"action_type": "CLICK", "x": 100, "y": 100}

   请输入命令: pyautogui.moveTo(100, 100)
   正在执行命令: pyautogui.moveTo(100, 100)
   命令执行结果: {'status': 'success', 'output': '', 'error': '', 'returncode': 0}
   等待2秒...
   正在获取截图...
   截图已保存到: /Users/luyuheng/开发/gui/screenshots/screenshot_1.png
   ```

## 注意事项

- 确保服务器和客户端可以互相访问
- 确保服务器上已经安装了所有必要的依赖
- 在某些平台上，截图可能无法显示光标
- 如果无法打开截图查看器，请手动查看 `screenshots` 目录下的截图文件
