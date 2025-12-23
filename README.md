# Dogfight Sandbox HG2

这是一个基于 **Harfang 3D** 引擎开发的空战模拟沙盒系统（Dogfight Sandbox）。项目集成了高性能的 3D 渲染、复杂的飞行物理模拟（JSBSim）以及 AI 训练环境。

## 🚀 快速开始

### 1. 环境准备
项目建议使用 **Anaconda** 或 **Miniconda** 进行环境管理。
```bash
# 创建并激活环境（示例）
conda create -n dogfight python=3.8
conda activate dogfight
```

### 2. 安装依赖
在项目根目录下，安装必要的 Python 包：
```bash
pip install -r source/requirements.txt
```
*主要依赖包括：`harfang`, `tqdm`, `numpy` 等。*

### 3. 运行项目
你可以通过根目录下的 `start.bat` 启动（请根据你的 conda 环境名称修改脚本内容），或者直接运行：
```bash
cd source
python main.py
```

## 🛠 配置说明

可以通过修改根目录下的 `config.json` 文件来调整运行参数：
- `Resolution`: 屏幕分辨率，例如 `[1920, 1080]`
- `FullScreen`: 是否全屏
- `VR`: 是否开启 VR 模式
- `UseJSBSim`: 是否使用 JSBSim 高级物理引擎
- `JSBSimAircraft`: 默认使用的 JSBSim 机型（如 `f16`）

## 🎮 操作快捷键

在飞行阶段，可以使用以下按键：

| 按键 | 功能 |
| :--- | :--- |
| `+` (或 `Plus`/`Add`) | **仿真加速** (2x, 4x...) |
| `-` (或 `Minus`/`Sub`) | **仿真减速** (0.5x, 0.25x...) |
| `0` | **恢复正常仿真速度** (1.0x) |
| `Space` | 开始游戏 / 武器发射 |
| `Tab` | 结束当前任务 / 返回菜单 |
| `T` | 开启/关闭飞行轨迹显示 |
| `R` | 切换渲染模式 (Renderless Mode) |
| `Y` | 切换自定义物理模式 |
| `P` | 开启/关闭性能监控显示 |

## 📂 项目结构

- `source/`: 核心源代码目录。
  - `main.py`: 程序入口。
  - `master.py`: 主逻辑控制。
  - `states.py`: 游戏状态机（菜单、飞行阶段等）。
  - `Missions.py`: 任务系统。
  - `JSBSimAdapter.py`: JSBSim 物理引擎适配器。
- `Agent/`: AI 训练相关代码，包含强化学习环境。
- `bin/`: 包含 Harfang 运行时需要的二进制库和工具。
- `config.json`: 全局配置文件。
- `screenshots/`: 项目截图及资源说明。

## ⚖️ 版权信息
Copyright (C) 2018-2021 Eric Kernin, NWNC HARFANG.

