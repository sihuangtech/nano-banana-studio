# Nano Banana Studio (纳米香蕉工作室)

简体中文版 | [English](README.md)

一个现代化的轻量级桌面客户端，用于调用 Google **Gemini 3 Pro Preview** 和 **Gemini 2.5 Flash** 模型生成图像。

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
- **🔄 自动重试与通知**:
  - 自动重试失败的生成任务（例如应对服务器过载）。
  - 可配置的重试间隔（支持时:分:秒设置）和最大尝试次数。
  - **邮件通知**: 生成成功（附带图片）或失败时发送邮件提醒。
- **💻 命令行 (CLI) 支持**: 支持通过命令行运行生成任务，完美适配服务器部署。
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

### 1. API Key 设置（必需）

**重要提示**：出于安全考虑，API 密钥**仅**从环境变量读取，**永远不会**存储在配置文件中。

1.  复制示例环境变量文件:
    ```bash
    cp .env.example .env
    ```
2.  编辑 `.env` 并填入您的 Google API Key:
    ```ini
    GOOGLE_API_KEY=your_api_key_here
    ```

您也可以直接在软件界面中输入 API Key，但它只会在会话期间存储在内存中。

### 2. 应用程序设置（可选）

1.  复制示例配置文件:
    ```bash
    cp config.json.example config.json
    ```
2.  编辑 `config.json` 以自定义:
    - 输出目录
    - 可用模型列表
    - 默认选择的模型

**注意**: `config.json` 已添加到 `.gitignore`，不会被提交到版本控制系统。

### 3. 邮件通知（可选）

要启用生成成功（附带图片）或失败时的邮件通知功能：

1.  编辑 `config.json`:
    ```json
    "email": {
        "enabled": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "receiver_email": "target_email@example.com"
    }
    ```

## 💻 使用说明

### 1. GUI 模式 (桌面端)

启动图形界面：

```bash
python gui.py
```

### 2. 命令行模式 (服务器 / 无头模式)

您可以在没有 GUI 的环境下运行 Nano Banana Studio，非常适合服务器环境或后台任务。

#### 使用配置文件 (YAML)

您可以将参数写入 YAML 文件，方便管理复杂的提示词和设置。

1.  复制示例文件：
    ```bash
    cp generate.yaml.example generate.yaml
    ```
2.  编辑 `generate.yaml`。
3.  运行命令：
    ```bash
    python cli.py -f generate.yaml
    ```
    **或者**，如果当前目录下存在 `generate.yaml`，您可以直接运行不带参数的命令，它会自动加载：
    ```bash
    python cli.py
    ```

**注意**：命令行参数优先级高于 YAML 文件。例如，`python cli.py -f generate.yaml --num-images 4` 会覆盖 YAML 中的数量设置。

#### 基础命令 (不使用配置文件)

快速测试：

```bash
python cli.py --prompt "A futuristic city" --retry --retry-interval 60
```

### 命令行参数

| 参数 | 描述 | 默认值 |
|----------|-------------|---------|
| `--prompt` | **必需**。生成的提示词。 | - |
| `--neg-prompt` | 反向提示词。 | None |
| `--model` | 模型名称。 | gemini-3-pro-image-preview |
| `--retry` | 开启失败自动重试。 | False |
| `--retry-interval` | 重试间隔（秒）。 | 10 |
| `--max-retries` | 最大重试次数（0 为无限）。 | 0 |
| `--num-images` | 生成图片数量。 | 1 |
| `--aspect-ratio` | 宽高比 (例如 1:1, 16:9)。 | 1:1 |

### 作为后台服务运行 (Systemd)

为了让程序在 Linux 服务器后台持续运行：

1.  编辑 `nano-banana-studio.service.example` 文件，修改为您的实际路径和用户。
2.  复制到 systemd 目录:
    ```bash
    sudo cp nano-banana-studio.service.example /etc/systemd/system/nano-banana-studio.service
    ```
3.  启用并启动服务:
    ```bash
    sudo systemctl enable nano-banana-studio
    sudo systemctl start nano-banana-studio
    ```

### 3. 代理设置（可选，中国大陆用户重要）
如果您在中国大陆等无法直接访问 Google 服务的地区，**必须**配置代理。

在 `.env` 文件中添加以下配置：

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

版权所有 © 2025 SK Studio

## 🌈 联系我们

欢迎加入彩旗开源社区，与我们一起探索开源技术的无限可能！

- **彩旗开源QQ交流群**: [点击加入](https://qm.qq.com/q/Z8eKCVzWAE)
- **邮箱**: contact@skstudio.cn
- **官网**: [https://www.skstudio.cn](https://www.skstudio.cn)
- **GitHub**: [SK Studio](https://github.com/sihuangtech)
- **更多项目**: 敬请期待我们的更多开源项目

感谢您的支持！如果您有任何问题或建议，欢迎随时联系我们。
