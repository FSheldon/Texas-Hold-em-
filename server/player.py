# server/player.py
# 玩家类定义（服务端用）

class Player:
    def __init__(self, socket, address, chips):
        """初始化玩家实例        
        :param socket: 玩家连接的socket对象
        :param address: 玩家地址（IP和端口）
        :param chips: 玩家初始筹码
        """
        self.socket = socket            # 玩家连接的socket
        self.address = address          # 玩家地址
        self.nickname = None            # 玩家昵称
        self.hand = []                  # 玩家手牌
        self.seat_number = None         # 座位编号
        self.role = None                # 玩家身份（小盲注、大盲注、普通玩家）
        self.chips = chips              # 玩家初始筹码
        self.is_folded = False          # 是否已弃牌，默认为 False
        self.is_all_in = False          # 是否已全压，默认为 False

    def clear_hand(self):
        """清空玩家手牌"""
        self.hand = []

    def __str__(self):
        """返回玩家信息"""
        return f"Player {self.address}, Seat: {self.seat_number}, Role: {self.role}, Chips: {self.chips}, Folded: {self.is_folded}"
