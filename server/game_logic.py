# server/game_logic.py
# 游戏规则及逻辑

import random
from deck import Deck
from player import Player
import collections

class PokerGame:
    def __init__(self, players, big_blind):
        """初始化游戏，包括玩家列表和当前轮次等"""
        self.players = players          # 玩家列表
        self.seated_players = []        # 座位顺序的玩家列表
        self.current_bets = []          # 当前下注额
        self.pot = 0                    # 底池
        self.side_pots = []             # 副池
        self.deck = None                # 扑克牌对象
        self.community_cards = []       # 公共牌
        self.player_hands = {}          # 玩家手牌
        self.blinds = {}                # 记录小盲注和大盲注玩家
        self.big_blind = big_blind      # 大盲注数额
        self.small_blind = big_blind // 2  # 小盲注数额
        self.current_bet_amount = big_blind  # 当前最大下注额
        self.player_current_bets = {player: 0 for player in players}  # 记录每位玩家本轮的下注额
        self.first_bet_round_complete = False  # 第一轮下注是否完成
        self.small_blind_index = 0      # 小盲注玩家的索引
        self.big_blind_index = 1        # 大盲注玩家的索引

    def start_game(self):
        """开始游戏的主循环"""
        while True:
            # 如果是首次游戏，初始化 seated_players
            if not self.seated_players:
                self.seated_players = self.players.copy()

            # 移除筹码为零的玩家
            self.remove_bankrupt_players()

            # 检查是否有足够的玩家进行游戏
            if len(self.seated_players) < 2:
                if len(self.seated_players) == 1:
                    winner = self.seated_players[0]
                    message = f"游戏结束，{winner.nickname} 赢得了所有筹码！"
                    self.broadcast(message)
                else:
                    self.broadcast("游戏结束，玩家人数不足。")
                break  # 结束游戏循环

            # 分配座位和确定盲注
            self.assign_seats()

            # 重置游戏状态
            self.reset_game()

            self.deck = Deck()              # 创建扑克牌
            self.deck.shuffle()             # 洗牌

            self.deal_hole_cards()          # 发底牌
            self.collect_blinds()           # 扣除小盲注和大盲注
            self.play_round()               # 进行游戏轮次

            # 游戏轮结束后，继续下一轮循环

    def assign_seats(self):
        """分配座位，并确定小盲注和大盲注玩家"""
        if not self.seated_players:
            # 首次游戏，随机分配座位
            random.shuffle(self.players)
            self.seated_players = self.players.copy()
            # 初始化盲注位置
            self.small_blind_index = 0
            self.big_blind_index = 1
        else:
            # 轮换座位和盲注位置
            num_players = len(self.seated_players)
            self.small_blind_index = (self.big_blind_index) % num_players
            self.big_blind_index = (self.small_blind_index + 1) % num_players

        self.blinds = {}
        for index, player in enumerate(self.seated_players):
            player.seat_number = index + 1  # 设置座位编号，从1开始
            if index == self.small_blind_index:
                self.blinds[player] = '小盲注'
            elif index == self.big_blind_index:
                self.blinds[player] = '大盲注'
            else:
                self.blinds[player] = '普通玩家'
            # 通知玩家他们的座位和身份
            message = f"您的座位编号为：{player.seat_number}，身份为：{self.blinds[player]}。"
            player.socket.send(message.encode())

    def notify_chip_counts(self):
        """通知所有玩家当前筹码数额"""
        for player in self.seated_players:
            message = f"您的当前筹码数额为：{player.chips}。"
            player.socket.send(message.encode())

    def collect_blinds(self):
        """扣除小盲注和大盲注"""
        for player in self.seated_players:
            if self.blinds[player] == '小盲注':
                message = f"您是小盲注，扣除小盲注数额的筹码。"
                player.socket.send(message.encode())
                player.chips -= self.small_blind
                self.pot += self.small_blind
                self.player_current_bets[player] = self.small_blind
            elif self.blinds[player] == '大盲注':
                message = f"您是大盲注，扣除大盲注数额的筹码。"
                player.socket.send(message.encode())
                player.chips -= self.big_blind
                self.pot += self.big_blind
                self.player_current_bets[player] = self.big_blind

    def deduct_chips(self, player, amount):
        """扣除玩家筹码并通知玩家"""
        player.chips -= amount
        self.pot += amount
        message = (f"您已扣除 {amount} 筹码")
        player.socket.send(message.encode())
        message = (f"您本轮下注额为：{self.player_current_bets[player]}。")
        player.socket.send(message.encode())
        self.notify_chip_counts()
        message = (f"目前底池总额为：{self.pot}。")
        self.broadcast(message)

    def deal_hole_cards(self):
        """发放每位玩家的底牌"""
        for player in self.seated_players:
            hand = self.deck.deal(2)  # 发两张手牌
            self.player_hands[player] = hand  # 保存玩家手牌
            # 使用 "|" 分隔每张牌的信息
            hand_str = "|".join(f"{card.rank} {card.suit}" for card in hand)
            message = f"您的手牌为：{hand_str}。"
            player.socket.send(message.encode())  # 使用 socket 发送手牌


    def play_round(self):
        """进行一轮游戏"""
        # Pre-flop 下注阶段
        self.betting_phase_for_all()

        # 判断是否有玩家胜出（如果只剩一个玩家）
        if self.check_only_one_player():
            return

        # Flop 阶段 - 发三张公共牌
        self.deal_community_cards('flop')
        self.betting_phase_for_all()

        if self.check_only_one_player():
            return

        # Turn 阶段 - 发第四张公共牌
        self.deal_community_cards('turn')
        self.betting_phase_for_all()

        if self.check_only_one_player():
            return

        # River 阶段 - 发第五张公共牌
        self.deal_community_cards('river')
        self.betting_phase_for_all()

        if self.check_only_one_player():
            return

        # Showdown - 最终摊牌，确定胜者
        self.determine_winner()

    def betting_phase_for_all(self):
        """遍历所有玩家进行下注"""
        if not self.first_bet_round_complete:
            self.betting_phase_preflop()
            self.first_bet_round_complete = True
        else:
            self.betting_phase_postflop()

    def betting_phase_preflop(self):
        """处理第一轮（Pre-flop）的下注逻辑"""
        big_blind_player = self.seated_players[self.big_blind_index]
        small_blind_player = self.seated_players[self.small_blind_index]

        sorted_players = self.seated_players
        start_index = (self.big_blind_index + 1) % len(sorted_players)

        current_player_index = start_index
        first_round_complete = False

        while True:
            player = sorted_players[current_player_index]

            # 跳过弃牌玩家
            if player.is_folded:
                current_player_index = (current_player_index + 1) % len(sorted_players)
                continue

            is_big_blind = (current_player_index == self.big_blind_index) and not first_round_complete

            try:
                # 针对大盲注玩家的特殊处理
                if is_big_blind and first_round_complete:
                    if self.player_current_bets[player] < self.current_bet_amount:
                        self.betting_phase(player, first_round_complete=True, is_big_blind=True)
                else:
                    self.betting_phase(player, first_round_complete, is_big_blind)
            except Exception as e:
                print(f"下注阶段出错: {e}")

            current_player_index = (current_player_index + 1) % len(sorted_players)

            # 完成第一圈下注
            if current_player_index == start_index:
                first_round_complete = True

            # 判断所有未弃牌玩家下注是否相等
            all_bets_equal = all(self.player_current_bets[p] == self.current_bet_amount
                                 for p in self.seated_players if not p.is_folded)

            # 判断是否只剩下一个玩家未弃牌
            only_one_player_remaining = sum(not p.is_folded for p in self.seated_players) == 1

            # 下注阶段结束条件
            if only_one_player_remaining or (first_round_complete and all_bets_equal):
                break

        self.broadcast(f"本轮下注结束。当前底池总额为：{self.pot}。")
        self.reset_bets()

    def betting_phase_postflop(self):
        """处理后续轮次（Flop、Turn、River）的下注逻辑"""
        sorted_players = self.seated_players
        start_index = self.small_blind_index  # 从小盲注位置开始

        current_player_index = start_index
        round_complete = False

        while True:
            # 检查是否只剩下一个玩家未弃牌
            only_one_player_remaining = sum(not p.is_folded for p in self.seated_players) == 1
            if only_one_player_remaining:
                break

            player = sorted_players[current_player_index]

            if player.is_folded:
                current_player_index = (current_player_index + 1) % len(sorted_players)
                continue

            try:
                self.betting_phase(player, round_complete)
            except Exception as e:
                raise RuntimeError(f"下注阶段出错: {e}")

            current_player_index = (current_player_index + 1) % len(sorted_players)

            if current_player_index == start_index:
                round_complete = True

            all_bets_equal = all(
                (self.player_current_bets[p] == self.current_bet_amount or p.is_all_in)
                for p in self.seated_players if not p.is_folded
            )

            if round_complete and all_bets_equal:
                break

        self.broadcast(f"本轮下注结束。当前底池总额为：{self.pot}。")
        self.reset_bets()

    def reset_bets(self):
        """重置下注状态"""
        self.current_bet_amount = 0
        for player in self.seated_players:
            self.player_current_bets[player] = 0

    def call(self, player):
        """处理跟注"""
        amount_to_call = self.current_bet_amount - self.player_current_bets[player]

        if player.chips < amount_to_call:
            # 玩家筹码不足，询问是否全压
            player.socket.send("你的筹码不足，是否选择all-in？(yes/no)".encode())
            response = player.socket.recv(1024).decode().strip().lower()
            if response == "yes":
                self.all_in(player)
                return
            else:
                raise Exception("筹码不足，无法跟注！")

        self.deduct_chips(player, amount_to_call)
        self.player_current_bets[player] += amount_to_call

        message = f"行动记录|{player.nickname}|跟注|{amount_to_call}"
        self.broadcast(message)


    def bet(self, player, bet_amount):
        """处理下注行为"""
        if not self.first_bet_round_complete and self.current_bet_amount != 0:
            raise Exception("目前不能使用bet行为")
        if player.chips < bet_amount:
            # 玩家筹码不足，询问是否全压
            player.socket.send("你的筹码不足，是否选择all-in？(yes/no)".encode())
            response = player.socket.recv(1024).decode().strip().lower()
            if response == "yes":
                self.all_in(player)
                return
            else:
                raise Exception("筹码不足，无法下注！")

        self.deduct_chips(player, bet_amount)
        self.current_bet_amount = bet_amount
        self.player_current_bets[player] += bet_amount

        message = f"行动记录|{player.nickname}|下注|{bet_amount}"
        self.broadcast(message)

    def raise_bet(self, player, raise_amount):
        """处理加注"""
        total_bet = self.current_bet_amount + raise_amount
        if player.chips < total_bet:
            # 玩家筹码不足，询问是否全压
            player.socket.send("你的筹码不足，是否选择all-in？(yes/no)".encode())
            response = player.socket.recv(1024).decode().strip().lower()
            if response == "yes":
                self.all_in(player)
                return
            else:
                raise Exception("筹码不足，无法加注！")

        self.deduct_chips(player, total_bet)
        self.current_bet_amount = total_bet + self.player_current_bets[player]
        self.player_current_bets[player] += total_bet

        message = f"行动记录|{player.nickname}|加注|{raise_amount}"
        self.broadcast(message)

    def all_in(self, player):
        """处理全压"""
        if player.chips == 0:
            raise Exception("筹码不足，无法全压！")

        all_in_amount = player.chips
        self.deduct_chips(player, all_in_amount)
        self.player_current_bets[player] += all_in_amount

        player.is_all_in = True

        # 更新主池和副池
        if self.player_current_bets[player] > self.current_bet_amount:
            self.current_bet_amount = self.player_current_bets[player]

        self.update_side_pots(player, all_in_amount)

        message = f"行动记录|{player.nickname}|全压|{all_in_amount}"
        self.broadcast(message)


    def fold(self, player):
        """处理弃牌"""
        player.is_folded = True
        message = f"行动记录|{player.nickname}|弃牌"
        self.broadcast(message)

    def check(self, player):
        """处理过牌"""
        if self.current_bet_amount != self.player_current_bets[player]:
            raise Exception("目前不能过牌")
        message = f"行动记录|{player.nickname}|过牌"
        self.broadcast(message)

    def betting_phase(self, player, first_round_complete=False, is_big_blind=False):
        """处理单个玩家的下注阶段"""  
        while True:
            # 向玩家发送当前下注情况
            player.socket.send(f"当前最大下注额为 {self.current_bet_amount}，您本轮下注额为： {self.player_current_bets[player]}。".encode())
            player.socket.send("请做出您的选择：(call, raise <amount>, bet <amount>, allin, fold, check)".encode())

            # 获取玩家的行动
            action = player.socket.recv(1024).decode().strip().lower()

            try:
                # 处理下注行为
                if action.startswith('bet'):
                    try:
                        bet_amount = int(action.split()[1])
                        self.bet(player, bet_amount)
                    except (ValueError, IndexError):
                        player.socket.send("无效的下注数额，请重新输入。".encode())
                        continue

                # 处理跟注行为
                elif action == 'call':
                    self.call(player)

                # 处理加注行为
                elif action.startswith('raise'):
                    try:
                        raise_amount = int(action.split()[1])
                        self.raise_bet(player, raise_amount)
                    except (ValueError, IndexError):
                        player.socket.send("无效的加注数额，请重新输入。".encode())
                        continue

                # 处理全压行为
                elif action == 'allin':
                    self.all_in(player)

                # 处理弃牌行为
                elif action == 'fold':
                    self.fold(player)

                # 处理过牌行为
                elif action == 'check':
                    self.check(player)

                else:
                    player.socket.send("无效的行动，请重新输入。".encode())
                    continue

                # 如果行为成功，跳出循环
                break

            except Exception as e:
                # 如果有异常（例如筹码不足），返回错误信息并让玩家重新选择
                player.socket.send(f"错误：{str(e)}，请重新选择您的行动。".encode())
                continue

    def deal_community_cards(self, round_type):
        """发放公共牌"""
        if round_type == 'flop':
            new_cards = self.deck.deal(3)
            self.community_cards.extend(new_cards)
        elif round_type == 'turn':
            new_cards = self.deck.deal(1)
            self.community_cards.extend(new_cards)
        elif round_type == 'river':
            new_cards = self.deck.deal(1)
            self.community_cards.extend(new_cards)
        else:
            raise ValueError("无效的公共牌轮次类型。")

        community_cards_str = ", ".join(str(card) for card in self.community_cards)
        message = f"当前公共牌为：{community_cards_str}。"
        self.broadcast(message)

    def check_only_one_player(self):
        """检查是否只剩一个玩家"""
        players_remaining = [player for player in self.seated_players if not player.is_folded]
        if len(players_remaining) == 1:
            winner = players_remaining[0]
            message = f"{winner.nickname} 是唯一剩下的玩家，赢得了本轮所有的底池筹码：{self.pot}。"
            self.broadcast(message)
            winner.chips += self.pot
            self.pot = 0
            self.broadcast("游戏结束")
            return True
        return False

    def update_side_pots(self, player, all_in_amount):
        """处理副池逻辑"""
        # 这里可以根据您的具体副池逻辑进行实现
        pass  # 暂时保留原来的功能

    def determine_winner(self):
        """通过比较牌力确定本轮游戏的胜者，并根据副池逻辑分配筹码"""
        # 判断胜利者
        players_in_showdown = [player for player in self.seated_players if not player.is_folded]
        player_hands_strength = {player: self.evaluate_hand(self.player_hands[player] + self.community_cards) for player in players_in_showdown}
        sorted_players = sorted(players_in_showdown, key=lambda p: player_hands_strength[p], reverse=True)

        # 将底池全部给予牌力最强的玩家
        winner = sorted_players[0]
        winner.chips += self.pot
        message = f"{winner.nickname} 赢得了底池，金额为：{self.pot} 筹码。"
        self.broadcast(message)
        self.pot = 0

        # 移除筹码为零的玩家
        self.remove_bankrupt_players()
        self.broadcast("游戏结束")

    def evaluate_hand(self, cards):
        """评估玩家的手牌组合，返回手牌类型和用于比较的牌值"""
        # 检查各个牌型，从高到低
        if self.is_Royal_Flush(cards):
            return (100, self.get_high_card(cards))
        if self.is_Straight_Flush(cards):
            return (90, self.get_straight_high(cards))
        if self.is_Four_of_a_Kind(cards):
            return (80, self.get_four_of_a_kind(cards))
        if self.is_Full_House(cards):
            return (70, self.get_full_house(cards))
        if self.is_Flush(cards):
            return (60, *self.get_flush_high(cards))
        if self.is_Straight(cards):
            return (50, self.get_straight_high(cards))
        if self.is_Three_of_a_Kind(cards):
            return (40, self.get_three_of_a_kind(cards))
        if self.is_Two_Pair(cards):
            return (30, *self.get_two_pair(cards))
        if self.is_One_Pair(cards):
            return (20, *self.get_one_pair(cards))
        return (10, *self.get_high_cards(cards))

    def is_Royal_Flush(self, cards):
        if self.is_Straight_Flush(cards):
            ranks = [card.rank for card in cards]
            royal_ranks = {'A', 'K', 'Q', 'J', '10'}
            return royal_ranks.issubset(set(ranks))
        return False

    def is_Straight_Flush(self, cards):
        return self.is_Flush(cards) and self.is_Straight(cards)

    def is_Four_of_a_Kind(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        return 4 in value_counts.values()

    def get_four_of_a_kind(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        quad_value = self.card_value([value for value, count in value_counts.items() if count == 4][0])
        remaining_value = max([self.card_value(value) for value, count in value_counts.items() if count != 4])
        return (quad_value, remaining_value)

    def is_Full_House(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        has_three = any(count == 3 for count in value_counts.values())
        has_pair = any(count == 2 for count in value_counts.values())
        return has_three and has_pair

    def get_full_house(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        three_value = max([self.card_value(value) for value, count in value_counts.items() if count == 3])
        pair_value = max([self.card_value(value) for value, count in value_counts.items() if count == 2])
        return (three_value, pair_value)

    def is_Flush(self, cards):
        suits = [card.suit for card in cards]
        suit_counts = collections.Counter(suits)
        for suit, count in suit_counts.items():
            if count >= 5:
                return True
        return False

    def get_flush_high(self, cards):
        suits = [card.suit for card in cards]
        suit_counts = collections.Counter(suits)
        flush_suit = max(suit_counts, key=suit_counts.get)
        flush_cards = [card for card in cards if card.suit == flush_suit]
        values = sorted([self.card_value(card.rank) for card in flush_cards], reverse=True)[:5]
        return values

    def is_Straight(self, cards):
        ranks = [self.card_value(card.rank) for card in cards]
        ranks = list(set(ranks))  # 去重
        ranks.sort()
        # 检查顺子
        for i in range(len(ranks) - 4):
            if ranks[i + 4] - ranks[i] == 4:
                return True
        # 特殊顺子 A,2,3,4,5
        if set([14, 2, 3, 4, 5]).issubset(ranks):
            return True
        return False

    def get_straight_high(self, cards):
        ranks = [self.card_value(card.rank) for card in cards]
        ranks = list(set(ranks))  # 去重
        ranks.sort()
    
        # 如果牌值不足 5 张，直接返回 0
        if len(ranks) < 5:
            return 0
    
        # 检查顺子
        for i in range(len(ranks) - 4):  # 遍历到倒数第 5 个元素
            if ranks[i + 4] - ranks[i] == 4:  # 检查是否是顺子
                return ranks[i + 4]
    
        # 检查特殊顺子 A,2,3,4,5
        if set([14, 2, 3, 4, 5]).issubset(ranks):
            return 5
    
        return 0


    def is_Three_of_a_Kind(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        return 3 in value_counts.values()

    def get_three_of_a_kind(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        three_value = max([self.card_value(value) for value, count in value_counts.items() if count == 3])
        remaining_values = sorted([self.card_value(value) for value, count in value_counts.items() if count != 3], reverse=True)[:2]
        return (three_value, *remaining_values)

    def is_Two_Pair(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        pairs = [value for value, count in value_counts.items() if count == 2]
        return len(pairs) >= 2

    def get_two_pair(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        pairs = sorted([self.card_value(value) for value, count in value_counts.items() if count == 2], reverse=True)[:2]
        remaining_values = [self.card_value(value) for value, count in value_counts.items() if count == 1]
        high_card = max(remaining_values) if remaining_values else 0
        return (*pairs, high_card)

    def is_One_Pair(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        pairs = [value for value, count in value_counts.items() if count == 2]
        return len(pairs) == 1

    def get_one_pair(self, cards):
        values = [card.rank for card in cards]
        value_counts = collections.Counter(values)
        pair_value = self.card_value([value for value, count in value_counts.items() if count == 2][0])
        remaining_values = sorted([self.card_value(value) for value, count in value_counts.items() if count == 1], reverse=True)[:3]
        return (pair_value, *remaining_values)

    def get_high_cards(self, cards):
        values = sorted([self.card_value(card.rank) for card in cards], reverse=True)[:5]
        return values

    def get_high_card(self, cards):
        return max([self.card_value(card.rank) for card in cards])

    def card_value(self, value):
        """将卡牌值转换为整数，用于比较"""
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                       '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return rank_values.get(value, 0)

    def reset_game(self):
        """重置游戏状态以便进行下一局"""
        self.pot = 0
        self.side_pots = []
        self.community_cards = []
        self.player_hands = {}
        self.player_current_bets = {player: 0 for player in self.seated_players}
        self.current_bet_amount = self.big_blind
        self.first_bet_round_complete = False
        # 重置玩家状态
        for player in self.seated_players:
            player.is_folded = False
            player.is_all_in = False

    def remove_bankrupt_players(self):
        """移除筹码为零的玩家"""
        bankrupt_players = [player for player in self.seated_players if player.chips <= 0]
        for player in bankrupt_players:
            message = "您的筹码已耗尽，您已被淘汰出局。"
            player.socket.send(message.encode())
            self.seated_players.remove(player)
            self.players.remove(player)  # 如果需要的话

    def broadcast(self, message):
        """广播消息给所有玩家"""
        for player in self.seated_players:
            player.socket.send(message.encode())
            
            
    if __name__ == "__main__":
        pass        