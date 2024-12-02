import tkinter as tk
import subprocess
import os
import threading
from PIL import Image, ImageTk
import sys

class PokerLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("德州扑克游戏")
        self.root.geometry("800x600")
        

        # 加载背景图片
        self.load_background(os.path.join("test","poker.png"))

        # 添加按钮
        self.create_room_button = tk.Button(
            self.root, text="创建房间", command=self.start_server, width=40, height=4
        )
        self.create_room_button.pack(pady=40)

        self.join_room_button = tk.Button(
            self.root, text="加入房间", command=self.start_client, width=40, height=4
        )
        self.join_room_button.pack(pady=40)

        self.exit_button = tk.Button(
            self.root, text="退出游戏", command=self.exit_game, width=40, height=4
        )
        self.exit_button.pack(pady=40)

    def load_background(self, image_path):
        """加载并显示背景图片"""
        image = Image.open(image_path)
        image = image.resize((800, 600), Image.LANCZOS)
        self.background_image = ImageTk.PhotoImage(image)

        background_label = tk.Label(self.root, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def start_server(self):
        """启动服务端，创建房间"""
        def run_server():
            # 使用 subprocess 调用 server.py
            subprocess.Popen(["server/dist/server.exe"])

        threading.Thread(target=run_server, daemon=True).start()

    def start_client(self):
        """启动客户端，加入房间"""
        def run_client():
            # 使用 subprocess 调用 client.py
            subprocess.Popen(["client/dist/client.exe"])

        threading.Thread(target=run_client, daemon=True).start()

    def exit_game(self):
        """退出游戏"""
        self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # 启动主界面
    launcher = PokerLauncher()
    launcher.run()
