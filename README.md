# MEEP

MEEP 是一个轻量的桌面宠物应用。它使用 GIF 动画显示透明、置顶的桌面宠物，支持自动移动、鼠标移入/点击触发动作、左键拖拽和右键退出。

当前项目包含 Windows/Tkinter 版本和 macOS/AppKit 版本。Windows 用户可以直接下载 `meep.exe`，macOS 用户可以下载 `MEEP.app` 的压缩包或 DMG。

## 下载和使用

如果只想直接运行程序，请到项目的 [Releases](../../releases) 页面下载最新版本。

Windows 用户下载 `meep.exe`，双击即可启动。右键点击桌面宠物可以退出程序。

macOS 用户下载 `MEEP.app.zip`，解压后双击 `MEEP.app`。

如果 Windows 提示“无法确认发布者”或 SmartScreen 警告，这是因为当前可执行文件没有代码签名。确认文件来自本项目 Release 页面后，可以选择继续运行。

如果 macOS 提示“无法验证开发者”，这是因为当前应用没有代码签名和公证。确认文件来自本项目 Release 页面后，可以右键点击 `MEEP.app`，选择“打开”，再确认运行。

## 功能

- 透明、置顶的桌面宠物窗口
- 待机和动作两组左右方向动画
- 自动水平移动，到达屏幕边缘后转向
- 鼠标移入或左键点击触发动作动画
- 左键拖拽移动位置，右键确认退出
- 使用 PyInstaller 打包为 Windows GUI 程序或 macOS App

## 项目结构

```text
.
├── assets/                  # GIF 动画资源
├── src/
│   ├── meep.py              # Windows/Tkinter 应用入口
│   └── meep_macos.py        # macOS/AppKit 应用入口
├── meep.spec                # Windows PyInstaller 配置
├── meep-macos.spec          # macOS PyInstaller 配置
├── requirements.txt         # 运行依赖
├── requirements-dev.txt     # 打包依赖
├── requirements-macos.txt   # macOS 运行依赖
├── requirements-macos-dev.txt
├── LICENSE
└── README.md
```

## 从源码运行

建议使用 Python 3.10 或更新版本。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\src\meep.py
```

## 在 macOS 上运行

macOS 版本使用 PyObjC/AppKit 原生窗口，而不是 Tkinter 的透明窗口能力。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-macos.txt
python src/meep_macos.py
```

macOS 版本会创建透明、无边框、置顶的桌面宠物窗口。左键点击或鼠标移入会触发动作，左键拖拽可以移动位置，右键可以退出。

## 打包 Windows 可执行文件

```powershell
pip install -r requirements-dev.txt
pyinstaller .\meep.spec --noconfirm --clean
```

打包完成后，可执行文件位于 `dist/meep.exe`。

## 打包 macOS 应用

需要在 macOS 上打包：

```bash
pip install -r requirements-macos-dev.txt
pyinstaller meep-macos.spec --noconfirm --clean
```

打包完成后，应用位于 `dist/MEEP.app`。

## 自定义动画

替换 `assets/` 中的 GIF 文件即可自定义宠物形象：

- `idle_right.gif`
- `idle_left.gif`
- `action_right.gif`
- `action_left.gif`

建议四个 GIF 保持相同尺寸和透明背景。程序会在运行时缩放到配置中的窗口大小。

## 配置

可在 `src/meep.py` 顶部的 `CONFIG` 中调整移动速度、动画间隔、动作持续时间和窗口大小。

## 开源协议

本项目使用 MIT License。详见 [LICENSE](LICENSE)。
