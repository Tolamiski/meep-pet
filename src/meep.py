import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
import sys

# ============================================
#  配置区域
# ============================================
CONFIG = {
    "step_size": 10,
    "move_interval": 200,
    "action_duration": 1800,
    "window_width": 130,
    "window_height": 130,
    "vertical_step": 0,
}

# ============================================
#  关键：获取资源路径（支持打包和开发两种模式）
# ============================================
def resource_path(relative_path):
    """获取资源的绝对路径，支持PyInstaller打包"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # PyInstaller打包后，_MEIPASS是临时解压目录
        base_path = Path(sys._MEIPASS)
    else:
        # 开发模式下，资源位于项目根目录的 assets/ 中
        base_path = Path(__file__).resolve().parent.parent
    return os.path.join(base_path, relative_path)

# ============================================
#  桌面宠物类
# ============================================
class DesktopPet:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面宠物")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.wm_attributes('-transparentcolor', 'white')

        self.width = CONFIG["window_width"]
        self.height = CONFIG["window_height"]
        self.root.geometry(f"{self.width}x{self.height}+100+100")

        self.label = tk.Label(self.root, bg='white')
        self.label.pack()

        # ---------- 加载GIF ----------
        self.frames = {
            'idle_right': self.load_gif_frames(resource_path("assets/idle_right.gif")),
            'idle_left': self.load_gif_frames(resource_path("assets/idle_left.gif")),
            'action_right': self.load_gif_frames(resource_path("assets/action_right.gif")),
            'action_left': self.load_gif_frames(resource_path("assets/action_left.gif")),
        }

        if not self.frames['idle_right'] or not self.frames['idle_left']:
            messagebox.showerror("错误", "待机GIF加载失败，请检查路径")
            self.root.destroy()
            return

        for key in ['action_right', 'action_left']:
            if not self.frames[key]:
                print(f"⚠️ {key}未找到，使用待机GIF替代")
                self.frames[key] = self.frames['idle_right' if 'right' in key else 'idle_left']

        # ---------- 状态管理 ----------
        self.is_action = False
        self.action_timer = None
        self.current_frame_idx = 0
        self.frames_completed = False
        self.direction = 1
        self.x_pos = 100
        self.y_pos = 100

        # ---------- 鼠标事件 ----------
        # 左键：触发动作 + 拖拽
        self.label.bind("<Button-1>", self.on_mouse_click)      # 左键点击触发动作
        self.label.bind("<B1-Motion>", self.drag_move)          # 左键拖拽移动
        self.label.bind("<ButtonRelease-1>", self.stop_drag)    # 松开左键停止拖拽
        
        # 右键：询问退出
        self.label.bind("<Button-3>", self.exit_pet)            # 右键退出
        
        # 鼠标移入：触发动作
        self.label.bind("<Enter>", self.on_mouse_enter)

        # 拖拽状态
        self.drag_data = {"x": 0, "y": 0, "dragging": False}

        # 启动动画
        self.update_animation()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- 加载GIF ----------
    def load_gif_frames(self, path):
        if not os.path.exists(path):
            print(f"⚠️ 文件不存在: {path}")
            return []
        try:
            img = Image.open(path)
            frames = []
            while True:
                frame = img.convert("RGBA")
                frame = frame.resize((self.width, self.height), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(frame)
                frames.append(tk_img)
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        except Exception as e:
            print(f"❌ 加载GIF出错: {e}")
            return []
        return frames

    # ---------- 获取当前帧组 ----------
    def get_current_frames(self):
        if self.is_action:
            return self.frames['action_right'] if self.direction == 1 else self.frames['action_left']
        else:
            return self.frames['idle_right'] if self.direction == 1 else self.frames['idle_left']

    # ---------- 动画循环 ----------
    def update_animation(self):
        frames = self.get_current_frames()
        if not frames:
            self.root.after(CONFIG["move_interval"], self.update_animation)
            return

        current_frame = frames[self.current_frame_idx]
        self.label.config(image=current_frame)
        self.label.image = current_frame

        self.current_frame_idx += 1
        if self.current_frame_idx >= len(frames):
            self.current_frame_idx = 0
            self.frames_completed = True
        else:
            self.frames_completed = False

        if not self.is_action and self.frames_completed:
            self.move_one_step()

        self.root.after(CONFIG["move_interval"], self.update_animation)

    # ---------- 移动 ----------
    def move_one_step(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.x_pos += CONFIG["step_size"] * self.direction

        if self.x_pos + self.width > screen_width:
            self.x_pos = screen_width - self.width
            self.flip_direction()
        elif self.x_pos < 0:
            self.x_pos = 0
            self.flip_direction()

        if CONFIG["vertical_step"] != 0:
            if not hasattr(self, 'y_direction'):
                self.y_direction = 1
            self.y_pos += CONFIG["vertical_step"] * self.y_direction
            if self.y_pos + self.height > screen_height - 50:
                self.y_pos = screen_height - 50 - self.height
                self.y_direction *= -1
            elif self.y_pos < 0:
                self.y_pos = 0
                self.y_direction *= -1

        self.root.geometry(f"+{int(self.x_pos)}+{int(self.y_pos)}")

    def flip_direction(self):
        self.direction *= -1

    # ---------- 触发动作 ----------
    def trigger_action(self):
        if self.is_action:
            if self.action_timer:
                self.root.after_cancel(self.action_timer)
        else:
            self.is_action = True
            self.current_frame_idx = 0
            self.frames_completed = False

        self.action_timer = self.root.after(
            CONFIG["action_duration"],
            self.stop_action
        )

    def stop_action(self):
        self.is_action = False
        self.current_frame_idx = 0
        self.frames_completed = False
        self.action_timer = None

    # ---------- 鼠标事件 ----------
    def on_mouse_enter(self, event):
        """鼠标移入 -> 触发动作"""
        # 如果正在拖拽，不触发动作
        if not self.drag_data["dragging"]:
            self.trigger_action()

    def on_mouse_click(self, event):
        """左键点击 -> 触发动作"""
        # 如果正在拖拽，不触发动作（避免拖拽结束时的误触）
        if not self.drag_data["dragging"]:
            self.trigger_action()
        # 重置拖拽状态（防止点击后残留拖拽状态）
        self.drag_data["dragging"] = False

    # ---------- 左键拖拽 ----------
    def start_drag(self, event):
        """开始拖拽（左键按下时调用）"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["dragging"] = True

    def drag_move(self, event):
        """拖拽移动（左键按住移动时调用）"""
        # 如果还没有开始拖拽，先初始化（防止从点击直接进入拖拽）
        if not self.drag_data["dragging"]:
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["dragging"] = True
            return
        
        # 计算移动距离
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.x_pos += dx
        self.y_pos += dy
        self.root.geometry(f"+{int(self.x_pos)}+{int(self.y_pos)}")

    def stop_drag(self, event):
        """停止拖拽（松开左键时调用）"""
        # 如果之前正在拖拽，重置状态
        if self.drag_data["dragging"]:
            self.drag_data["dragging"] = False

    # ---------- 退出（右键） ----------
    def exit_pet(self, event):
        """右键点击 -> 询问是否退出"""
        # 弹出确认对话框
        result = messagebox.askyesno(
            "MEEP",
            "确定要退出吗？",
            icon='question',
            parent=self.root
        )
        
        if result:  # 用户点击"是"
            self.on_close()
        else:       # 用户点击"否"
            # 保持运行，可以给个反馈（可选）
            pass

    # ---------- 退出清理 ----------
    def on_close(self):
        """关闭窗口时清理资源"""
        if self.action_timer:
            self.root.after_cancel(self.action_timer)
        self.root.destroy()

# ============================================
#  启动
# ============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopPet(root)
    root.mainloop()
