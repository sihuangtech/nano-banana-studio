# Nano Banana Studio

[简体中文版](README_zh.md) | English

A modern, lightweight desktop client for generating images using Google's **Gemini 3 Pro Preview** and **Gemini 2.5 Flash** models.

Nano Banana Studio provides a clean Graphical User Interface (GUI) to interact with the powerful Gemini Image Generation API, offering full control over prompts, aspect ratios, and generation settings without writing code.

## ✨ Features

- **🚀 Powered by Gemini**: Utilizes Google's latest Gemini 3 Pro Preview model and Gemini 2.5 Flash high-speed image generation model.
- **🎨 Full Parameter Control**:
  - **Prompt**: Detailed text descriptions.
  - **Negative Prompt**: Specify what you don't want in the image.
  - **Aspect Ratios**: Support for 1:1, 16:9, 4:3, 3:4, and 9:16.
  - **Image Size**: Select from 1K, 2K, 4K resolutions.
  - **Batch Generation**: Generate up to 4 images at once.
  - **Model Selection**: Switch between Gemini 2.5 Flash, Gemini 3 Pro Preview, and Imagen models.
  - **Advanced Settings**:
    - **Person Generation**: Control policies for generating people (e.g., allow adult content).
    - **Safety Filter**: Adjust safety blocking levels.
    - **Seed**: Set a deterministic seed for reproducibility.
    - **Guidance Scale**: Control how closely the image follows the prompt.
- **🖥️ Modern GUI**: Built with PyQt6, featuring a responsive layout and real-time status updates.
- **⚡ Asynchronous Generation**: The interface remains responsive while images are being generated.
- **💾 Auto-Save**: Automatically saves generated images to the `outputs` directory.
- **⚙️ Configuration Management**:
  - API Key management via GUI or `.env` file.
  - Proxy support for regions with restricted access.
  - Settings persistence.

## 📋 Prerequisites

- Python 3.9 or higher.
- A Google Cloud API Key with access to Gemini API (Get it from [Google AI Studio](https://aistudio.google.com/)).

## 📦 Installation

This project uses `uv` for modern Python dependency management, but can also work with standard `pip`.

### Option 1: Using `uv` (Recommended)

1.  **Install uv** (if not installed):
    ```bash
    pip install uv
    ```

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/sihuangtech/nano-banana-studio.git
    cd nano-banana-studio
    ```

3.  **Sync dependencies**:
    ```bash
    uv sync
    ```

### Option 2: Using standard `pip`

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sihuangtech/nano-banana-studio.git
    cd nano-banana-studio
    ```

2.  **Install dependencies**:
    ```bash
    pip install pyqt6 pydantic google-genai pillow python-dotenv
    ```

## ⚙️ Configuration

### 1. API Key (Required)

**Important**: For security reasons, API keys are **only** read from environment variables and are **never** stored in configuration files.

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` and add your Google API Key:
    ```ini
    GOOGLE_API_KEY=your_api_key_here
    ```

You can also enter your API Key directly in the GUI, but it will only be stored in memory during the session.

### 2. Application Settings (Optional)

1.  Copy the example configuration file:
    ```bash
    cp config.json.example config.json
    ```
2.  Edit `config.json` to customize:
    - Output directory
    - Available models
    - Default model selection

**Note**: `config.json` is in `.gitignore` and will not be committed to version control.

### 3. Proxy Settings (Optional)
If you are in a region where Google services are restricted (e.g., China), configure the proxy in `.env`:

```ini
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

## 🚀 Usage

Run the application:

```bash
# If using uv
uv run python main.py

# If using standard python
python main.py
```

1.  **Enter API Key**: If not set in `.env`, enter it in the top-left field.
2.  **Enter Prompt**: Describe the image you want to generate.
3.  **Adjust Settings**: Select aspect ratio and number of images.
4.  **Click Generate**: Wait for the magic to happen!
5.  **View Results**: Images will appear in the right panel and are saved to the `outputs/` folder.

## 📂 Project Structure

- `api/`: Handles communication with Google Gemini API.
- `core/`: Core application logic and settings management.
- `gui/`: PyQt6 user interface components.
- `main.py`: Application entry point.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright © 2025 SK Studio

## 🌈 Contact Us

Welcome to join the SK Studio Open Source Community and explore the infinite possibilities of open source technology with us!

- **QQ Group**: [Join us](https://qm.qq.com/q/Z8eKCVzWAE)
- **Email**: contact@skstudio.cn
- **Website**: [https://www.skstudio.cn](https://www.skstudio.cn)
- **GitHub**: [SK Studio](https://github.com/sihuangtech)
- **More Projects**: Stay tuned for more of our open source projects

Thank you for your support! If you have any questions or suggestions, please feel free to contact us.
