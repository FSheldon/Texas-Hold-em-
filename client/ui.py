# client/ui.py
# 客户端用户界面

import tkinter as tk
from turtle import update
from PIL import Image, ImageTk
import os

class PokerUI:
    def __init__(self, root, client):
        self.root = root
        self.root.title("德州扑克")
        self.root.geometry("800x600")

        # 保存客户端对象，用于后续的交互
        self.client = client

        # 获取当前文件的目录路径
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # 加载背景图片
        self.load_background(os.path.join(self.base_path, "resources/table/table.jpg"))

        # 初始化界面布局
        self.setup_layout()
        
        # 添加显示座位编号和身份的标签
        self.seat_info_label = tk.Label(self.root, text="", font=("Helvetica", 10), bg="lightgray")
        self.seat_info_label.place(relx=0.85, rely=0.05, anchor="ne")
        
        # 初始化手牌显示区域和公共牌显示区域
        self.card_images = []
        self.community_card_images = []  # 存储公共牌图片标签
        # 初始化玩家操作区域
        self.setup_action_panel()
        
        # 添加历史行动记录区域
        self.history_display = tk.Text(self.root, height=10, width=10, bg="white", state="disabled", font=("Helvetica", 10))
        self.history_display.place(relx=0.05, rely=0.85, anchor="sw")  

    def load_background(self, image_path):
        """加载并显示背景图片"""
        image = Image.open(image_path)
        image = image.resize((800, 600), Image.LANCZOS)
        self.background_image = ImageTk.PhotoImage(image)

        background_label = tk.Label(self.root, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def add_action_to_history(self, nickname, action, chips=None):
        """将玩家的行动记录添加到历史显示框中"""
        self.history_display.config(state="normal")  # 解锁文本框编辑
        if chips:
            message = f"{nickname} {action}。\n"
        else:
            message = f"{nickname} {action}。\n"
        self.history_display.insert(tk.END, message)  # 添加记录
        self.history_display.config(state="disabled")  # 锁定文本框，避免用户修改
        self.history_display.see(tk.END)  # 滚动到最新记录

    def setup_layout(self):
        """设置布局和各个区域"""

        # 顶部区域：用于显示昵称、IP 输入和连接按钮
        self.top_frame = tk.Frame(self.root, bg="white")
        self.top_frame.pack(side=tk.TOP, pady=10)

        # 昵称输入框和标签
        self.nickname_label = tk.Label(self.top_frame, text="请输入昵称：", bg="white", font=("Helvetica", 12))
        self.nickname_label.pack(side=tk.LEFT, padx=5)

        self.nickname_entry = tk.Entry(self.top_frame, font=("Helvetica", 12))
        self.nickname_entry.pack(side=tk.LEFT, padx=5)

        # IP 输入框和标签
        self.ip_label = tk.Label(self.top_frame, text="请输入服务器的 IP 地址：", bg="white", font=("Helvetica", 12))
        self.ip_label.pack(side=tk.LEFT, padx=5)

        self.ip_entry = tk.Entry(self.top_frame, font=("Helvetica", 12))
        self.ip_entry.pack(side=tk.LEFT, padx=5)

        # 连接按钮
        self.connect_button = tk.Button(self.top_frame, text="连接服务器", command=self.connect_to_server, font=("Helvetica", 12))
        self.connect_button.pack(side=tk.LEFT, padx=5)

        # 底部区域：用于显示准备按钮
        self.bottom_frame = tk.Frame(self.root, bg="white")
        self.bottom_frame.pack(side=tk.BOTTOM, pady=10)

        # 右下角区域：用于显示消息
        self.message_display = tk.Text(self.root, height=8, width=30, bg="lightgray", state="disabled", font=("Helvetica", 10))
        self.message_display.place(relx=0.85, rely=0.85, anchor="se")


    def setup_action_panel(self):
        """设置左侧的操作面板"""
        self.action_panel = tk.Frame(self.root, bg="lightgray", width=100)
        self.action_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Call 按钮
        self.call_button = tk.Button(self.action_panel, text="Call", command=self.call_action)
        self.call_button.pack(pady=5, fill=tk.X)

        # Raise 按钮和输入框
        self.raise_frame = tk.Frame(self.action_panel, bg="lightgray")
        self.raise_frame.pack(pady=5, fill=tk.X)
        
        self.raise_label = tk.Label(self.raise_frame, text="Raise")
        self.raise_label.pack(side=tk.LEFT)
        
        self.raise_entry = tk.Entry(self.raise_frame, width=5)
        self.raise_entry.pack(side=tk.LEFT, padx=5)
        
        self.raise_button = tk.Button(self.raise_frame, text="Raise", command=self.raise_action)
        self.raise_button.pack(side=tk.LEFT)

        # Bet 按钮和输入框
        self.bet_frame = tk.Frame(self.action_panel, bg="lightgray")
        self.bet_frame.pack(pady=5, fill=tk.X)
        
        self.bet_label = tk.Label(self.bet_frame, text="Bet")
        self.bet_label.pack(side=tk.LEFT)
        
        self.bet_entry = tk.Entry(self.bet_frame, width=5)
        self.bet_entry.pack(side=tk.LEFT, padx=5)
        
        self.bet_button = tk.Button(self.bet_frame, text="Bet", command=self.bet_action)
        self.bet_button.pack(side=tk.LEFT)

        # All-in 按钮
        self.allin_button = tk.Button(self.action_panel, text="All-in", command=self.allin_action)
        self.allin_button.pack(pady=5, fill=tk.X)

        # Fold 按钮
        self.fold_button = tk.Button(self.action_panel, text="Fold", command=self.fold_action)
        self.fold_button.pack(pady=5, fill=tk.X)
        
        # Check 按钮
        self.check_button = tk.Button(self.action_panel, text="Check", command=self.check_action)
        self.check_button.pack(pady=5, fill=tk.X)

    def clear_connection_ui(self):
        """连接成功后清除连接相关的UI组件"""
        self.ip_label.pack_forget()     # 隐藏 IP 地址标签
        self.ip_entry.pack_forget()     # 隐藏 IP 输入框
        self.nickname_label.pack_forget()  # 隐藏昵称标签
        self.nickname_entry.pack_forget()  # 隐藏昵称输入框
        self.connect_button.pack_forget()  # 隐藏连接按钮


    def show_ready_prompt(self):
        """显示准备按钮供用户确认准备状态"""
        # 创建“准备”按钮并放置在底部面板中
        self.ready_button = tk.Button(self.bottom_frame, text="准备", command=self.client.send_ready, font=("Helvetica", 12))
        self.ready_button.pack(pady=5)

    def connect_to_server(self):
        """连接到服务器并显示提示信息"""
        nickname = self.nickname_entry.get().strip()
        ip_address = self.ip_entry.get().strip()
        self.client.connect_to_server(ip_address, nickname)

    def display_seat_info(self, seat_number, role):
        """在右上角显示玩家的座位编号和身份"""
        seat_info = f"座位编号: {seat_number} | 身份: {role}"
        self.seat_info_label.config(text=seat_info)

    def display_community_cards(self, community_cards):
        """在中心区域显示公共牌"""
        # 清除之前的公共牌显示
        for img_label in self.community_card_images:
            img_label.destroy()
        self.community_card_images = []

        # 设置中心位置
        center_x = 400  # 窗口宽度的一半
        center_y = 250  # 窗口高度中心稍微偏上

        for index, card in enumerate(community_cards):
            # 生成文件名，根据 card 对象的 suit 和 rank
            image_path = os.path.join(self.base_path, f"resources/cards/{card.suit.lower()}_{card.rank}.png")

            if os.path.exists(image_path):
                # 加载图片并缩放
                card_image = Image.open(image_path).resize((100, 140), Image.LANCZOS)
                card_photo = ImageTk.PhotoImage(card_image)

                # 创建标签以显示卡片图像
                card_label = tk.Label(self.root, image=card_photo, bg="white")
                card_label.image = card_photo  # 保存对图片的引用

                # 设置每张牌的水平偏移量，使公共牌并排排列
                offset_x = (index - 2) * 110  # 偏移量，调整公共牌之间的间距
                x_position = center_x + offset_x
                y_position = center_y
                card_label.place(x=x_position, y=y_position)
                self.community_card_images.append(card_label)
                                
        self.update_current_bet_display(0)

    def call_action(self):
        """执行 Call 操作"""
        self.client.send_action("call")

    def raise_action(self):
        """执行 Raise 操作，获取输入的金额"""
        amount = self.raise_entry.get()
        self.client.send_action("raise", amount)

    def bet_action(self):
        """执行 Bet 操作，获取输入的金额"""
        amount = self.bet_entry.get()
        self.client.send_action("bet", amount)

    def allin_action(self):
        """执行 All-in 操作"""
        self.client.send_action("allin")

    def fold_action(self):
        """执行 Fold 操作"""
        self.client.send_action("fold")

    def check_action(self):
        """执行 Check 操作"""
        self.client.send_action("check")

    def display_message(self, message):
        """在右下角消息区域显示服务器消息"""
        self.message_display.config(state="normal")
        self.message_display.insert(tk.END, message + "\n")
        self.message_display.config(state="disabled")
        self.message_display.see(tk.END)

    def display_hand(self, cards):
        """根据手牌信息在底部居中显示手牌图片"""
        # 清除之前的手牌显示
        for img_label in self.card_images:
            img_label.destroy()
        self.card_images = []

        # 设置底部居中位置
        bottom_center_y = 400  # 靠下的 y 位置，可以根据需求调整
        center_x = 400  # 窗口宽度的一半

        for index, card in enumerate(cards):
            image_path = os.path.join(self.base_path, f"resources/cards/{card.suit.lower()}_{card.rank}.png")
            if os.path.exists(image_path):
                card_image = Image.open(image_path).resize((100, 140), Image.LANCZOS)
                card_photo = ImageTk.PhotoImage(card_image)
                card_label = tk.Label(self.root, image=card_photo, bg="white")
                card_label.image = card_photo  # 保存对图片的引用
                offset_x = (index - 0.5) * 120
                x_position = center_x + offset_x
                y_position = bottom_center_y
                card_label.place(x=x_position, y=y_position)
                self.card_images.append(card_label)

    def clear_community_cards(self):
        """清除公共牌的显示"""
        for img_label in self.community_card_images:
            img_label.destroy()
        self.community_card_images = []  # 清空公共牌列表
         
        
    def display_turn_notification(self):
        """在 UI 上显示轮到玩家行动的提示"""
        self.turn_label = tk.Label(self.root, text="轮到您行动！", font=("Helvetica", 16, "bold"), fg="red", bg="white")
        self.turn_label.place(relx=0.5, rely=0.1, anchor="center")

    def clear_turn_notification(self):
        """清除轮到玩家行动的提示"""
        if hasattr(self, 'turn_label'):
            self.turn_label.destroy()       
       
    def display_game_over_popup(self, winner_name, chips_won):
        """显示游戏结束弹窗，提示获胜玩家和赢得的筹码"""
        message = f"游戏结束！\n获胜者：{winner_name}\n赢得筹码：{chips_won}"
        tk.messagebox.showinfo("游戏结束", message) 
            
    def update_pot_display(self, pot_total):
        """在右上角显示底池总额"""
        if hasattr(self, 'pot_label'):
            self.pot_label.config(text=f"底池总额：{pot_total} 筹码")
        else:
            self.pot_label = tk.Label(self.root, text=f"底池总额：{pot_total} 筹码", font=("Helvetica", 12, "bold"), fg="blue")
            self.pot_label.place(relx=0.85, rely=0.1, anchor="ne")
            
    def update_current_bet_display(self, current_bet):
        """在右上角显示本轮下注额"""
        if hasattr(self, 'current_bet_label'):
            self.current_bet_label.config(text=f"本轮下注额：{current_bet} 筹码")
        else:
            self.current_bet_label = tk.Label(self.root, text=f"本轮下注额：{current_bet} 筹码", font=("Helvetica", 12, "bold"), fg="green")
            self.current_bet_label.place(relx=0.85, rely=0.15, anchor="ne")
            
    def update_chips_display(self, chips):
        """在右上角显示当前筹码数额"""
        if hasattr(self, 'chips_label'):
            self.chips_label.config(text=f"当前筹码数额：{chips} 筹码")
        else:
            self.chips_label = tk.Label(self.root, text=f"当前筹码数额：{chips} 筹码", font=("Helvetica", 12, "bold"), fg="black")
            self.chips_label.place(relx=0.85, rely=0.2, anchor="ne")
