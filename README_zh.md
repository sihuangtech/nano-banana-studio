# Nano Banana Studio (纳米香蕉工作室)

中文版 | [English](README.md)

一个现代化的轻量级桌面客户端，用于调用 Google **Gemini 2.5 Flash** 模型（Nano Banana）生成图像。

Nano Banana Studio 提供了一个简洁的图形用户界面 (GUI)，让您可以轻松与强大的 Gemini 图像生成 API 交互，无需编写代码即可完全控制提示词、宽高比和生成设置。

## ✨ 功能特点

- **🚀 核心驱动**: 采用 Google 最新的 Gemini 3 Pro Preview 模型，以及 Gemini 2.5 Flash 高速图像生成模型。
- **🎨 全面的参数控制**:
  - **提示词 (Prompt)**: 支持详细的文本描述。
  - **反向提示词 (Negative Prompt)**: 指定您不希望在图像中出现的内容。
  - **宽高比**: 支持 1:1, 16:9, 4:3, 3:4, 和 9:16。
  - **分辨率 (Image Size)**: 支持 1K, 2K, 4K 分辨率选择。
  - **批量生成**: 一次最多生成 4 张图片。
  - **模型选择**: 支持切换 Gemini 2.5 Flash, Gemini 3 Pro Preview 以及 Imagen 系列模型。
  - **高级设置**:
    - **人物生成 (Person Generation)**: 调整人物生成策略 (如允许成人内容)。
    - **安全过滤 (Safety Filter)**: 自定义安全拦截等级。
    - **随机种子 (Seed)**: 固定种子以复现结果。
    - **引导系数 (Guidance Scale)**: 控制图像对提示词的遵循程度。
- **🖥️ 现代化界面**: 基于 PyQt6 构建，界面响应迅速，实时显示状态。
- **⚡ 异步生成**: 生成过程中界面保持流畅，不会卡顿。
- **💾 自动保存**: 生成的图片会自动保存到 `outputs` 目录。
- **⚙️ 配置管理**:
  - 支持通过 GUI 或 `.env` 文件管理 API Key。
  - **代理支持**: 专为网络受限地区（如中国大陆）优化，支持配置 HTTP/HTTPS 代理。
  - 设置自动持久化。

## 📋 前置要求

- Python 3.9 或更高版本。
- 一个拥有 Gemini API 访问权限的 Google Cloud API Key (可在 [Google AI Studio](https://aistudio.google.com/) 免费获取)。

## 📦 安装指南

本项目使用 `uv` 进行现代化的 Python 依赖管理，同时也支持标准的 `pip`。

### 方法 1: 使用 `uv` (推荐)

1.  **安装 uv** (如果尚未安装):
    ```bash
    pip install uv
    ```

2.  **克隆仓库**:
    ```bash
    git clone https://github.com/sihuangtech/nano-banana-studio.git
    cd nano-banana-studio
    ```

3.  **同步依赖**:
    ```bash
    uv sync
    ```

### 方法 2: 使用标准 `pip`

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/sihuangtech/nano-banana-studio.git
    cd nano-banana-studio
    ```

2.  **安装依赖**:
    ```bash
    pip install pyqt6 pydantic google-genai pillow python-dotenv
    ```

## ⚙️ 配置说明

### 1. API Key 设置
您可以直接在软件界面中输入 API Key，也可以为了方便在 `.env` 文件中预设。

1.  创建 `.env` 文件:
    ```bash
    touch .env
    ```
2.  编辑 `.env` 并填入您的 Key:
    ```ini
    GOOGLE_API_KEY=your_api_key_here
    ```

### 2. 代理设置 (重要)
如果您在中国大陆等无法直接访问 Google 服务的地区，**必须**配置代理。

在 `.env` 文件中取消注释并修改以下行：

```ini
# 请根据您的实际代理软件端口修改（例如 Clash 通常是 7890）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

## 🚀 使用说明

运行程序:

```bash
# 如果使用 uv
uv run python main.py

# 如果使用标准 python
python main.py
```

1.  **输入 API Key**: 如果未在 `.env` 中设置，请在左上角输入框填写。
2.  **输入提示词**: 描述您想要生成的画面。
3.  **调整设置**: 选择合适的图片比例和数量。
4.  **点击生成 (Generate)**: 等待奇迹发生！
5.  **查看结果**: 图片将显示在右侧面板，并自动保存到项目根目录下的 `outputs/` 文件夹中。

## 📂 项目结构

- `api/`: 处理与 Google Gemini API 的通信。
- `core/`: 核心业务逻辑和设置管理。
- `gui/`: PyQt6 用户界面组件。
- `main.py`: 程序入口。

## 📄 许可证

本项目采用 MIT 许可证授权。详情请参阅 [LICENSE](LICENSE) 文件。

版权所有 © 2024 [您的姓名]
