from io import BytesIO
import os
from pathlib import Path
import sys

import objc
from AppKit import (
    NSAlert,
    NSAlertFirstButtonReturn,
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSBackingStoreBuffered,
    NSColor,
    NSFloatingWindowLevel,
    NSImage,
    NSImageScaleAxesIndependently,
    NSImageView,
    NSMakePoint,
    NSMakeRect,
    NSScreen,
    NSTrackingActiveAlways,
    NSTrackingInVisibleRect,
    NSTrackingMouseEnteredAndExited,
    NSTrackingArea,
    NSWindow,
    NSWindowStyleMaskBorderless,
)
from Foundation import NSData, NSObject, NSTimer
from PIL import Image


PET_CONTROLLER = None

CONFIG = {
    "step_size": 10,
    "move_interval": 200,
    "action_duration": 1800,
    "window_width": 130,
    "window_height": 130,
    "vertical_step": 0,
}


def resource_path(relative_path):
    """Return an absolute resource path for source and PyInstaller modes."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent
    return os.path.join(base_path, relative_path)


def pil_frame_to_nsimage(frame, width, height):
    """Convert one PIL frame to an NSImage while preserving alpha."""
    resized = frame.convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    resized.save(buffer, format="PNG")
    payload = buffer.getvalue()
    data = NSData.dataWithBytes_length_(payload, len(payload))
    return NSImage.alloc().initWithData_(data)


class PetImageView(NSImageView):
    controller = objc.ivar()

    def acceptsFirstMouse_(self, event):
        return True

    def mouseDown_(self, event):
        self.controller.trigger_action()
        self.controller.begin_drag(event)

    def mouseDragged_(self, event):
        self.controller.drag_to(event)

    def mouseUp_(self, event):
        self.controller.stop_drag()

    def rightMouseDown_(self, event):
        self.controller.confirm_exit()

    def mouseEntered_(self, event):
        if not self.controller.dragging:
            self.controller.trigger_action()

    def updateTrackingAreas(self):
        objc.super(PetImageView, self).updateTrackingAreas()
        options = (
            NSTrackingMouseEnteredAndExited
            | NSTrackingActiveAlways
            | NSTrackingInVisibleRect
        )
        tracking_area = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(), options, self, None
        )
        self.addTrackingArea_(tracking_area)


class DesktopPetMac(NSObject):
    def init(self):
        self = objc.super(DesktopPetMac, self).init()
        if self is None:
            return None

        self.width = CONFIG["window_width"]
        self.height = CONFIG["window_height"]
        self.x_pos = 100
        self.y_pos = 100
        self.direction = 1
        self.y_direction = 1
        self.dragging = False
        self.drag_offset = (0, 0)
        self.is_action = False
        self.current_frame_idx = 0
        self.frames_completed = False
        self.animation_timer = None
        self.action_timer = None

        self.frames = {
            "idle_right": self.load_gif_frames(resource_path("assets/idle_right.gif")),
            "idle_left": self.load_gif_frames(resource_path("assets/idle_left.gif")),
            "action_right": self.load_gif_frames(resource_path("assets/action_right.gif")),
            "action_left": self.load_gif_frames(resource_path("assets/action_left.gif")),
        }
        for key in ["action_right", "action_left"]:
            if not self.frames[key]:
                fallback = "idle_right" if "right" in key else "idle_left"
                self.frames[key] = self.frames[fallback]

        self.create_window()
        self.start_animation()
        return self

    def create_window(self):
        frame = NSMakeRect(self.x_pos, self.y_pos, self.width, self.height)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setTitle_("MEEP")
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setHasShadow_(False)
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setReleasedWhenClosed_(False)
        self.window.setAcceptsMouseMovedEvents_(True)

        self.image_view = PetImageView.alloc().initWithFrame_(NSMakeRect(0, 0, self.width, self.height))
        self.image_view.controller = self
        self.image_view.setImageScaling_(NSImageScaleAxesIndependently)
        self.window.setContentView_(self.image_view)
        self.window.orderFrontRegardless()

    def load_gif_frames(self, path):
        if not os.path.exists(path):
            print(f"Missing GIF: {path}")
            return []
        frames = []
        try:
            image = Image.open(path)
            while True:
                frames.append(pil_frame_to_nsimage(image, self.width, self.height))
                image.seek(image.tell() + 1)
        except EOFError:
            pass
        except Exception as exc:
            print(f"Failed to load GIF {path}: {exc}")
            return []
        return frames

    def get_current_frames(self):
        if self.is_action:
            return self.frames["action_right"] if self.direction == 1 else self.frames["action_left"]
        return self.frames["idle_right"] if self.direction == 1 else self.frames["idle_left"]

    def start_animation(self):
        interval = CONFIG["move_interval"] / 1000
        self.animation_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            interval,
            self,
            "updateAnimation:",
            None,
            True,
        )

    def updateAnimation_(self, timer):
        frames = self.get_current_frames()
        if not frames:
            return

        current_frame = frames[self.current_frame_idx]
        self.image_view.setImage_(current_frame)

        self.current_frame_idx += 1
        if self.current_frame_idx >= len(frames):
            self.current_frame_idx = 0
            self.frames_completed = True
        else:
            self.frames_completed = False

        if not self.is_action and self.frames_completed and not self.dragging:
            self.move_one_step()

    def move_one_step(self):
        screen_frame = NSScreen.mainScreen().visibleFrame()
        min_x = screen_frame.origin.x
        max_x = screen_frame.origin.x + screen_frame.size.width - self.width
        min_y = screen_frame.origin.y
        max_y = screen_frame.origin.y + screen_frame.size.height - self.height

        self.x_pos += CONFIG["step_size"] * self.direction
        if self.x_pos > max_x:
            self.x_pos = max_x
            self.flip_direction()
        elif self.x_pos < min_x:
            self.x_pos = min_x
            self.flip_direction()

        if CONFIG["vertical_step"] != 0:
            self.y_pos += CONFIG["vertical_step"] * self.y_direction
            if self.y_pos > max_y:
                self.y_pos = max_y
                self.y_direction *= -1
            elif self.y_pos < min_y:
                self.y_pos = min_y
                self.y_direction *= -1

        self.window.setFrameOrigin_(NSMakePoint(self.x_pos, self.y_pos))

    def flip_direction(self):
        self.direction *= -1

    def trigger_action(self):
        if not self.is_action:
            self.is_action = True
            self.current_frame_idx = 0
            self.frames_completed = False
        elif self.action_timer is not None:
            self.action_timer.invalidate()

        delay = CONFIG["action_duration"] / 1000
        self.action_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            delay,
            self,
            "stopAction:",
            None,
            False,
        )

    def stopAction_(self, timer):
        self.is_action = False
        self.current_frame_idx = 0
        self.frames_completed = False
        self.action_timer = None

    def begin_drag(self, event):
        self.dragging = True
        mouse = event.locationInWindow()
        self.drag_offset = (mouse.x, mouse.y)

    def drag_to(self, event):
        if not self.dragging:
            return
        mouse = event.window().convertPointToScreen_(event.locationInWindow())
        self.x_pos = mouse.x - self.drag_offset[0]
        self.y_pos = mouse.y - self.drag_offset[1]
        self.window.setFrameOrigin_(NSMakePoint(self.x_pos, self.y_pos))

    def stop_drag(self):
        self.dragging = False

    def confirm_exit(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("MEEP")
        alert.setInformativeText_("确定要退出吗？")
        alert.addButtonWithTitle_("退出")
        alert.addButtonWithTitle_("取消")
        if alert.runModal() == NSAlertFirstButtonReturn:
            NSApplication.sharedApplication().terminate_(self)


def main():
    global PET_CONTROLLER
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    PET_CONTROLLER = DesktopPetMac.alloc().init()
    app.run()


if __name__ == "__main__":
    main()
