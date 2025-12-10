#!/usr/bin/env python3
"""
命令行脚本，用于初始化env_controller并循环接受命令，每个命令后2秒获取截图并展示给用户。
"""
import argparse
import time
import os
import subprocess
import platform
from env_controller.controller import PythonController

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Env Controller命令行工具")
    parser.add_argument("--ip", default="localhost", help="服务器IP地址")
    parser.add_argument("--port", type=int, default=5000, help="服务器端口")
    args = parser.parse_args()
    
    # 初始化PythonController
    print(f"正在连接到服务器 {args.ip}:{args.port}...")
    controller = PythonController(vm_ip=args.ip, server_port=args.port)
    print("连接成功！")
    
    print("\n=== Env Controller命令行工具 ===")
    print("输入 'exit' 或 'quit' 退出程序")
    print("输入命令以执行操作，支持以下命令格式：")
    print("- 直接输入Python表达式（将在服务器上执行）")
    print("- 输入JSON格式的动作指令（如：{\"action_type\": \"CLICK\", \"x\": 100, \"y\": 100}")
    
    # 创建截图保存目录
    screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    screenshot_counter = 1
    
    while True:
        try:
            # 读取用户输入
            command = input("\n请输入命令: ").strip()
            
            # 检查退出条件
            if command.lower() in ["exit", "quit"]:
                print("退出程序...")
                break
            
            if not command:
                continue
            
            # 执行命令
            print(f"正在执行命令: {command}")
            
            try:
                # 尝试解析为JSON动作指令
                import json
                action = json.loads(command)
                controller.execute_action(action)
                print("动作执行成功！")
            except json.JSONDecodeError:
                # 如果不是JSON，则作为Python命令执行
                result = controller.execute_python_command(command)
                print(f"命令执行结果: {result}")
            
            # 等待2秒
            print("等待2秒...")
            time.sleep(2)
            
            # 获取并展示截图
            print("正在获取截图...")
            screenshot_data = controller.get_screenshot()
            
            if screenshot_data:
                # 保存截图
                screenshot_path = os.path.join(screenshots_dir, f"screenshot_{screenshot_counter}.png")
                with open(screenshot_path, "wb") as f:
                    f.write(screenshot_data)
                
                print(f"截图已保存到: {screenshot_path}")
                screenshot_counter += 1
                
                # 展示截图（使用系统默认图像查看器）
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(screenshot_path)
                    elif os.name == 'posix':  # macOS 或 Linux
                        subprocess.run(['open' if platform.system() == 'Darwin' else 'xdg-open', screenshot_path])
                except Exception as e:
                    print(f"无法打开截图查看器: {e}")
                    print(f"请手动查看截图文件: {screenshot_path}")
            else:
                print("获取截图失败！")
                
        except KeyboardInterrupt:
            print("\n程序被中断，退出...")
            break
        except Exception as e:
            print(f"执行命令时发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
