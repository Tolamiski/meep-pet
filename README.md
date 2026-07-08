# MEEP

MEEP 是一个轻量的 Windows 桌面宠物应用。它使用 Python、Tkinter 和 Pillow 播放透明背景 GIF 动画，支持自动移动、鼠标移入/点击触发动作、左键拖拽和右键退出。

## 下载和使用

如果只想直接运行程序，请到项目的 [Releases](../../releases) 页面下载最新版本中的 `meep.exe`。

下载后双击 `meep.exe` 即可启动。右键点击桌面宠物可以退出程序。

如果 Windows 提示“无法确认发布者”或 SmartScreen 警告，这是因为当前可执行文件没有代码签名。确认文件来自本项目 Release 页面后，可以选择继续运行。

## 功能

- 透明、置顶的桌面宠物窗口
- 待机和动作两组左右方向动画
- 自动水平移动，到达屏幕边缘后转向
- 鼠标移入或左键点击触发动作动画
- 左键拖拽移动位置，右键确认退出
- 使用 PyInstaller 打包为 Windows GUI 程序

## 项目结构

```text
.
├── assets/                  # GIF 动画资源
├── src/
│   └── meep.py              # 应用入口
├── meep.spec                # PyInstaller 配置
├── requirements.txt         # 运行依赖
├── requirements-dev.txt     # 打包依赖
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

## 打包 Windows 可执行文件

```powershell
pip install -r requirements-dev.txt
pyinstaller .\meep.spec --noconfirm --clean
```

打包完成后，可执行文件位于 `dist/meep.exe`。

发布 Release 时，建议把这个 `dist/meep.exe` 作为附件上传，让普通用户不需要安装 Python。

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
