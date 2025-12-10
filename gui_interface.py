#!/usr/bin/env python3
"""
Env Controller GUI界面，每秒更新截图，允许直接点击截图以在对应位置点击。
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import requests
from PIL import Image, ImageTk
import json
from env_controller.controller import PythonController


class EnvControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Env Controller GUI")
        self.root.geometry("1000x800")

        # 连接状态
        self.is_connected = False
        self.controller = None

        # 截图数据
        self.current_screenshot = None
        self.screenshot_width = 0
        self.screenshot_height = 0

        # 图片位置信息
        self.image_x_offset = 0
        self.image_y_offset = 0
        self.current_scale = 1.0

        # 服务器信息
        self.server_ip = tk.StringVar(value="localhost")
        self.server_port = tk.StringVar(value="5000")

        # 创建界面
        self.create_widgets()

        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self.on_window_resize)

        # 定时截图线程
        self.screenshot_thread = None
        self.stop_screenshot_event = threading.Event()

    def create_widgets(self):
        # 创建顶部连接栏
        connect_frame = ttk.Frame(self.root, padding="10")
        connect_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(connect_frame, text="服务器IP:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(connect_frame, textvariable=self.server_ip, width=15).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Label(connect_frame, text="端口:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(connect_frame, textvariable=self.server_port, width=8).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Button(connect_frame, text="连接", command=self.connect_server).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(connect_frame, text="断开", command=self.disconnect_server).pack(
            side=tk.LEFT, padx=5
        )

        self.status_label = ttk.Label(connect_frame, text="未连接", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # 创建截图显示区域
        self.screenshot_frame = ttk.Frame(self.root, padding="10")
        self.screenshot_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # 创建画布用于显示截图
        self.canvas = tk.Canvas(self.screenshot_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定点击事件
        self.canvas.bind("<Button-1>", self.on_screenshot_click)

        # 添加缩放控制
        scale_frame = ttk.Frame(self.root, padding="10")
        scale_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(scale_frame, text="缩放:").pack(side=tk.LEFT, padx=5)
        self.scale_var = tk.DoubleVar(value=1.0)
        self.scale_slider = ttk.Scale(
            scale_frame,
            from_=0.1,
            to=2.0,
            variable=self.scale_var,
            orient=tk.HORIZONTAL,
            command=self.on_scale_change,
        )
        self.scale_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.scale_label = ttk.Label(scale_frame, text="100%")
        self.scale_label.pack(side=tk.LEFT, padx=5)

    def connect_server(self):
        """连接到服务器"""
        try:
            ip = self.server_ip.get()
            port = int(self.server_port.get())

            self.controller = PythonController(vm_ip=ip, server_port=port)

            # 测试连接
            screenshot = self.controller.get_screenshot()
            if screenshot:
                self.is_connected = True
                self.status_label.config(text="已连接", foreground="green")
                messagebox.showinfo("成功", "连接服务器成功！")

                # 开始定时获取截图
                self.start_screenshot_thread()
            else:
                raise Exception("无法获取截图")

        except Exception as e:
            messagebox.showerror("错误", f"连接服务器失败: {e}")

    def disconnect_server(self):
        """断开服务器连接"""
        self.is_connected = False
        self.status_label.config(text="未连接", foreground="red")

        # 停止截图线程
        self.stop_screenshot_event.set()
        if self.screenshot_thread:
            self.screenshot_thread.join()

        self.controller = None
        self.canvas.delete("all")
        self.canvas.create_text(
            100, 100, text="已断开连接", fill="white", font=("Arial", 16)
        )

    def start_screenshot_thread(self):
        """启动截图线程"""
        self.stop_screenshot_event.clear()
        self.screenshot_thread = threading.Thread(target=self.update_screenshot_loop)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()

    def update_screenshot_loop(self):
        """定时更新截图的循环"""
        while self.is_connected and not self.stop_screenshot_event.is_set():
            print("正在获取截图...")
            try:
                screenshot = self.controller.get_screenshot()
                if screenshot:
                    # 保存截图数据
                    screenshot_path = os.path.join(
                        os.path.dirname(__file__), "temp_screenshot.png"
                    )
                    with open(screenshot_path, "wb") as f:
                        f.write(screenshot)

                    # 更新GUI
                    self.root.after(0, self.update_screenshot_display, screenshot_path)
            except Exception as e:
                print(f"获取截图失败: {e}")

            # 等待1秒
            time.sleep(5)

    def update_screenshot_display(self, screenshot_path):
        """更新截图显示"""
        try:
            # 打开原始图片
            image = Image.open(screenshot_path)
            self.screenshot_width, self.screenshot_height = image.size

            # 获取窗口可用空间
            self.screenshot_frame.update_idletasks()
            available_width = self.screenshot_frame.winfo_width() - 20  # 减去边距
            available_height = self.screenshot_frame.winfo_height() - 20  # 减去边距

            # 计算适应窗口的最佳缩放比例，保持宽高比
            if available_width <= 0 or available_height <= 0:
                return

            # 计算宽度和高度的缩放比例
            width_scale = available_width / self.screenshot_width
            height_scale = available_height / self.screenshot_height

            # 使用较小的缩放比例，确保图片完全显示
            scale = min(width_scale, height_scale)

            # 应用用户设置的缩放比例
            user_scale = self.scale_var.get()
            final_scale = user_scale * scale

            new_width = int(self.screenshot_width * final_scale)
            new_height = int(self.screenshot_height * final_scale)

            # 保存缩放后的图片
            scaled_image_path = os.path.join(
                os.path.dirname(__file__), "temp_scaled_screenshot.png"
            )
            image.resize((new_width, new_height), Image.LANCZOS).save(scaled_image_path)

            # 使用Tkinter的PhotoImage打开缩放后的图片
            self.current_screenshot = tk.PhotoImage(file=scaled_image_path)

            # 更新画布
            self.canvas.delete("all")
            self.canvas.config(width=available_width, height=available_height)

            # 计算图片居中显示的位置
            x_offset = (available_width - new_width) // 2
            y_offset = (available_height - new_height) // 2

            # 保存图片位置信息，用于点击事件处理
            self.image_x_offset = x_offset
            self.image_y_offset = y_offset
            self.current_scale = final_scale

            # 显示图片
            self.canvas.create_image(
                x_offset, y_offset, image=self.current_screenshot, anchor=tk.NW
            )

            # 更新缩放标签
            self.scale_label.config(text=f"{int(user_scale * 100)}%")

        except Exception as e:
            print(f"更新截图显示失败: {e}")
            import traceback

            traceback.print_exc()

    def on_screenshot_click(self, event):
        """处理截图点击事件"""
        if not self.is_connected or not self.current_screenshot:
            return

        try:
            # 获取点击位置
            click_x = event.x
            click_y = event.y

            # 检查点击是否在图片范围内
            if (
                click_x < self.image_x_offset
                or click_x > self.image_x_offset + self.current_screenshot.width()
                or click_y < self.image_y_offset
                or click_y > self.image_y_offset + self.current_screenshot.height()
            ):
                print("点击位置在图片范围外")
                return

            # 计算图片内的相对坐标
            relative_x = click_x - self.image_x_offset
            relative_y = click_y - self.image_y_offset

            # 应用缩放比例，转换为原始截图坐标
            original_x = int(relative_x / self.current_scale)
            original_y = int(relative_y / self.current_scale)

            # 确保坐标在有效范围内
            original_x = max(0, min(original_x, self.screenshot_width - 1))
            original_y = max(0, min(original_y, self.screenshot_height - 1))

            # 执行点击操作
            action = {"action_type": "CLICK", "x": original_x, "y": original_y}

            self.controller.execute_action(action)
            print(f"执行点击操作: x={original_x}, y={original_y}")

            # 显示点击反馈
            feedback_x = relative_x + self.image_x_offset - 10
            feedback_y = relative_y + self.image_y_offset - 10
            self.canvas.create_oval(
                feedback_x,
                feedback_y,
                feedback_x + 20,
                feedback_y + 20,
                fill="red",
                outline="white",
                width=2,
            )

            # 1秒后移除反馈
            self.root.after(
                1000,
                lambda: self.canvas.delete("all")
                or self.update_screenshot_display(
                    os.path.join(os.path.dirname(__file__), "temp_screenshot.png")
                ),
            )

        except Exception as e:
            messagebox.showerror("错误", f"执行点击操作失败: {e}")
            import traceback

            traceback.print_exc()

    def on_scale_change(self, event):
        """处理缩放变化"""
        if self.current_screenshot and os.path.exists(
            os.path.join(os.path.dirname(__file__), "temp_screenshot.png")
        ):
            self.update_screenshot_display(
                os.path.join(os.path.dirname(__file__), "temp_screenshot.png")
            )

    def on_window_resize(self, event=None):
        """处理窗口大小变化"""
        if self.current_screenshot and os.path.exists(
            os.path.join(os.path.dirname(__file__), "temp_screenshot.png")
        ):
            self.update_screenshot_display(
                os.path.join(os.path.dirname(__file__), "temp_screenshot.png")
            )


def main():
    root = tk.Tk()
    app = EnvControllerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
