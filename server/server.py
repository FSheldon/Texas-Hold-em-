import socket
import threading
import netifaces
from game_logic import PokerGame
from player import Player

class PokerServer:

    def __init__(self, host='0.0.0.0', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.clients = []       # 记录所有客户端连接
        self.players = []       # 记录玩家对象
        self.max_players = 0    # 房间支持的最大玩家数量
        self.ready_players = 0  # 记录准备好的玩家数量
        self.initial_chips = 0  # 每位玩家的初始筹码
        self.big_blind = 0      # 大盲注数额
        self.small_blind = 0    # 小盲注数额

    def get_local_ip(self):
        """尝试获取本地的 IPv4 地址"""
        interfaces = netifaces.interfaces()  # 获取所有网络接口
        potential_ips = []
        for interface in interfaces:
            if_addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in if_addresses:
                ipv4_addresses = if_addresses[netifaces.AF_INET]
                for address_info in ipv4_addresses:
                    ip_address = address_info.get('addr')
                    # 将地址添加到候选列表中，稍后进行筛选
                    potential_ips.append(ip_address)

        # 过滤并选择局域网的 IP 地址
        for ip in potential_ips:
            if ip.startswith('192.168.') or ip.startswith('10.'):
                # 返回匹配的内网 IP
                print(f"找到的IP地址: {potential_ips}")
                return ip

        # 如果没有匹配的局域网 IP，返回回环地址
        return '127.0.0.1'

    def start(self):
        self.server.listen()
        # 显示服务器的 IP 地址
        server_ip = self.get_local_ip()
        print(f"服务器启动，IP 地址为：{server_ip}，等待连接...")
        self.accept_connections()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"玩家 {addr} 已连接")

            # 创建玩家实例并添加到玩家列表
            nickname = client_socket.recv(1024).decode().strip()
            player = Player(client_socket, addr, self.initial_chips)
            player.nickname = nickname
            self.players.append(player)
            self.clients.append(client_socket)

            if len(self.clients) == self.max_players:
                self.broadcast("玩家数量已达到服务器支持人数，是否开始游戏？（yes）")
                self.handle_player_ready()

    def broadcast(self, message):
        for client in self.clients:
            client.send(message.encode())

    def handle_player_ready(self):
        for client in self.clients:
            while True:
                try:
                    # 接收玩家的响应
                    response = client.recv(1024).decode().strip().lower()

                    if response == 'yes':
                        self.ready_players += 1
                        client.send("您已准备完毕，等待其余玩家准备！".encode())
                        break  # 结束当前玩家的等待循环
                    else:
                        client.send("输入有误，请输入 'yes' 以准备游戏：".encode())
                except Exception as e:
                    print(f"玩家响应接收失败: {e}")
                    break

        # 检查是否所有玩家都同意开始游戏
        if self.ready_players == self.max_players:
            self.broadcast("所有玩家均已准备完毕，游戏开始！")
            self.start_game()

    def start_game(self):
        game = PokerGame(self.players, self.big_blind)  # 创建游戏实例并传入玩家对象和大盲注
        game.start_game()  # 开始游戏
"""
if __name__ == "__main__":
    
    while True:
        try:
            max_players = int(input("请输入房间支持人数(推荐游戏人数为2-6人): "))
            if max_players < 2 or max_players > 10:
                print("人数不合法，请重新输入！")
                continue
            initial_chips = int(input("请输入每位玩家初始筹码: "))
            if initial_chips % 2 != 0 or initial_chips < 200 or initial_chips > 10000:
                print("筹码数额不合法，请重新输入！")
                continue
            big_blind = int(input("请输入大盲注数额(推荐为初始筹码的1/100,并且应为偶数): "))
            if big_blind % 2 != 0 or big_blind < 2 or big_blind > initial_chips // 100:
                print("大盲注数值设置不合法，请重新输入！")
                continue
            break
        except ValueError:
            print("输入有误，请重新输入！")      

    server = PokerServer()
    server.max_players = max_players
    server.initial_chips = initial_chips  # 添加初始筹码属性
    server.big_blind = big_blind
    server.small_blind = big_blind // 2  # 小盲注为大盲注的一半
    server.start()
"""