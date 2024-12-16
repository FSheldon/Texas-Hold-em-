# client/client.py
# 客户端主程序

import socket
import threading
from ui import PokerUI
import tkinter as tk
import re

class PokerClient:
    def __init__(self):
        # 创建 Tkinter 主窗口
        self.root = tk.Tk()
        
        # 创建 UI 界面，并传入 self（PokerClient 实例）
        self.ui = PokerUI(self.root, self)

        self.client = None  # 用于连接的 socket

    def connect_to_server(self, host, nickname):
        """尝试连接服务器"""
        port = 12345  # 固定端口号
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect((host, port))
            self.client.send(nickname.encode())
            self.ui.display_message("成功连接到服务器")
            self.ui.clear_connection_ui()  # 隐藏连接界面组件
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.ui.display_message(f"连接到服务器失败: {e}")

    def receive_messages(self):
        """接收服务器消息并显示在 GUI 中"""
        while True:
            try:
                message = self.client.recv(1024).decode()
                if not message:
                    self.ui.display_message("服务器断开连接")
                    break
                self.ui.display_message(message)

                # 检查消息是否包含座位编号和身份
                if "您的座位编号为：" in message:
                    seat_number, role = self.parse_seat_info(message)
                    if seat_number and role:
                        self.ui.display_seat_info(seat_number, role)

                # 检查消息是否包含手牌信息
                if "您的手牌为：" in message:
                    cards = self.parse_hand_message(message)
                    self.ui.display_hand(cards)

                # 检查消息是否包含公共牌信息
                if "当前公共牌为：" in message:
                    community_cards = self.parse_community_cards(message)
                    self.ui.display_community_cards(community_cards)

                # 如果接收到准备消息，则显示准备按钮
                if "是否开始游戏" in message:
                    self.ui.show_ready_prompt()
                                                  
                # 检查是否为游戏结束消息，清除公共牌
                if "游戏结束" in message:
                    self.ui.clear_community_cards()
                    self.ui.update_pot_display(0)
                    
                    # 提取获胜玩家和筹码信息并显示弹窗
                    winner_info = self.parse_winner_info(message)
                    if winner_info:
                        winner_name, chips_won = winner_info
                        self.ui.display_game_over_popup(winner_name, chips_won)
                    
                # 检查是否为轮到玩家行动的消息
                if "请做出您的选择：" in message:
                    self.ui.display_turn_notification()
                    
                # 检查是否包含底池总额信息
                if "底池总额为：" in message:
                    pot_total = self.parse_pot_total(message)
                    if pot_total is not None:
                        self.ui.update_pot_display(pot_total)
                        
                 # 检查是否包含本轮下注额信息
                if "您本轮下注额为：" in message:
                    current_bet = self.parse_current_bet(message)
                    if current_bet is not None:
                        self.ui.update_current_bet_display(current_bet)
                        
                if "当前筹码数额为：" in message:
                    chips = self.parse_chip_info(message)
                    if chips is not None:
                        self.ui.update_chips_display(chips)
                        
                # 检查是否为行动记录消息
                if "行动记录" in message:
                    # 假设服务器发送的格式为：行动记录|玩家昵称|玩家动作|下注筹码（可选）
                    parts = message.split("|")
                    if len(parts) >= 3:
                        nickname, action = parts[1], parts[2]
                        chips = parts[3] if len(parts) == 4 else None
                        self.ui.add_action_to_history(nickname, action, chips)
                    continue
                       
            except Exception as e:
                self.ui.display_message("连接中断: " + str(e))
                break
        self.client.close()

    def send_ready(self):
        """向服务器发送准备消息"""
        try:
            self.client.send("yes".encode())
            self.ui.display_message("您已准备完毕，等待其余玩家准备！")
        except Exception as e:
            self.ui.display_message("发送准备请求失败: " + str(e))

    def request_chips(self):
        """请求服务器提供所有玩家的筹码信息"""
        try:
            self.client.sendall("REQUEST_CHIPS".encode())  # 发送筹码请求
        except Exception as e:
            self.ui.display_message(f"请求筹码信息失败: {e}")

    def send_action(self, action, amount=None):
        """发送玩家操作到服务器"""
        try:
            if amount:
                message = f"{action} {amount}"
            else:
                message = action
            self.client.send(message.encode())
            self.ui.display_message(f"您已选择操作: {message}")
            self.ui.clear_turn_notification()
        except Exception as e:
            self.ui.display_message(f"发送操作请求失败: {e}")

    def parse_seat_info(self, message):
        """解析服务器发来的座位编号和身份信息"""
        try:
            match = re.search(r"您的座位编号为：(\d+)，身份为：(.*?)。", message)
            if match:
                seat_number = match.group(1)
                role = match.group(2)
                return seat_number, role
        except Exception as e:
            print(f"解析座位信息时出错: {e}")
        return None, None

    def parse_chip_info(self, message):
        """解析服务器发来的筹码信息"""
        try:
            match = re.search(r"当前筹码数额为：(\d+)", message)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"解析筹码信息时出错: {e}")

    def parse_hand_message(self, message):
        """解析服务器发来的手牌信息，返回手牌对象列表"""
        try:
            match = re.search(r"您的手牌为：(.*?)(?=\。|$)", message)
            if not match:
                print("未找到手牌信息")
                return []
    
            hand_str = match.group(1).strip()
            cards = []
    
            for card_str in hand_str.split("|"):
                parts = card_str.strip().split(" ")
                if len(parts) == 2:
                    rank, suit = parts
                    suit_map = {"♠": "spade", "♣": "club", "♥": "heart", "♦": "diamond"}
                    suit = suit_map.get(suit, suit)  # 使用映射，确保兼容性
                    cards.append(Card(suit=suit, rank=rank))
                else:
                    print(f"无法解析的手牌格式：{card_str}")
            return cards
        except Exception as e:
            print(f"解析手牌信息时出错: {e}")
            return []

    def parse_community_cards(self, message):
        """解析服务器发来的公共牌信息，返回公共牌对象列表"""
        try:
            match = re.search(r"当前公共牌为：(.*?)(?=\。|$)", message)
            if not match:
                print("未找到公共牌信息")
                return []
            
            community_str = match.group(1).strip()
            community_cards = []

            for card_str in community_str.split(", "):
                parts = card_str.strip().split(" ")
                if len(parts) == 2:
                    rank, suit = parts
                    suit_map = {"♠": "spade", "♣": "club", "♥": "heart", "♦": "diamond"}
                    suit = suit_map.get(suit, suit)  # 使用映射，确保兼容性
                    community_cards.append(Card(suit=suit, rank=rank))
                else:
                    print(f"无法解析的公共牌格式：{card_str}")
            return community_cards
        except Exception as e:
            print(f"解析公共牌信息时出错: {e}")
            return []
        
    def parse_pot_total(self, message):
        """解析服务器发来的底池总额"""
        try:
            match = re.search(r"底池总额为：(\d+)", message)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"解析底池总额信息时出错: {e}")
        return None
    
    def parse_current_bet(self, message):
        """解析服务器发来的本轮下注额"""
        try:
            match = re.search(r"您本轮下注额为：(\d+)", message)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"解析本轮下注额信息时出错: {e}")
        return None
    
    def parse_winner_info(self, message):
        """解析游戏结束时的获胜玩家和赢得筹码数"""
        try:
            match = re.search(r"游戏结束，(.*?) 赢得了 (\d+) 筹码", message)
            if match:
                winner_name = match.group(1)
                chips_won = int(match.group(2))
                return winner_name, chips_won
        except Exception as e:
            print(f"解析获胜信息出错: {e}")
        return None

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

if __name__ == "__main__":
    client = PokerClient()
    client.root.mainloop()  # 启动 Tkinter 主循环
