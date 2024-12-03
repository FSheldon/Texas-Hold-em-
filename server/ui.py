import tkinter as tk
from tkinter import messagebox
import threading
from server import PokerServer  

class ServerUI:

    def __init__(self, root):
        self.root = root
        self.root.title("服务器管理界面")
        self.root.geometry("800x600")

        # 创建输入项
        self.create_label("房间支持人数 (推荐2-6人):")
        self.max_players_entry = self.create_entry()

        self.create_label("每位玩家初始筹码 (200-10000，偶数):")
        self.initial_chips_entry = self.create_entry()

        self.create_label("大盲注数额 (偶数，推荐初始筹码的1/100):")
        self.big_blind_entry = self.create_entry()

        # 创建启动服务器按钮
        self.start_button = self.create_button("启动服务器", self.start_server)

        # 显示服务器状态区域
        self.create_label("服务器状态:")
        self.server_status = tk.Text(self.root, width=80, height=20, state='disabled')
        self.server_status.pack()

        # 服务器实例
        self.server = None

    def create_label(self, text):
        label = tk.Label(self.root, text=text, font=("黑体", 12))
        label.pack()

    def create_entry(self):
        entry = tk.Entry(self.root, width=30, font=("黑体", 12))
        entry.pack()
        return entry

    def create_button(self, text, cmd):
        button = tk.Button(self.root, text=text, command=cmd, font=("黑体", 12))
        button.pack()
        return button

    def start_server(self):
        try:
            # 获取用户输入
            max_players = int(self.max_players_entry.get())
            initial_chips = int(self.initial_chips_entry.get())
            big_blind = int(self.big_blind_entry.get())

            # 参数验证
            if not (2 <= max_players <= 10):
                raise ValueError("房间支持人数应在2-10人之间")
            if initial_chips % 2 != 0 or not (200 <= initial_chips <= 10000):
                raise ValueError("每位玩家初始筹码应为200-10000之间的偶数")
            if big_blind % 2 != 0 or not (2 <= big_blind <= initial_chips // 100):
                raise ValueError("大盲注数额应为初始筹码1/100的偶数")

            # 创建并启动服务器
            self.server = PokerServer()
            self.server.max_players = max_players
            self.server.initial_chips = initial_chips
            self.server.big_blind = big_blind
            self.server.small_blind = big_blind // 2

            # 使用线程启动服务器
            server_thread = threading.Thread(target=self.server.start, daemon=True)
            server_thread.start()

            self.update_status(f"服务器启动成功！IP 地址: {self.server.get_local_ip()}\n")
        except ValueError as e:
            messagebox.showerror("参数错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"无法启动服务器: {e}")

    def update_status(self, message):
        """更新服务器状态显示"""
        self.server_status.config(state='normal')
        self.server_status.insert('end', message + "\n")
        self.server_status.config(state='disabled')
        self.server_status.see('end')


if __name__ == '__main__':
    root = tk.Tk()
    server_ui = ServerUI(root)
    root.mainloop()
