# server/core/deck.py
# 扑克牌管理类

import random

class Card:
    """表示一张扑克牌"""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} {self.suit}"

    def __repr__(self):
        return self.__str__()

class Deck:
    """表示一副扑克牌"""
    def __init__(self):
        self.cards = self.generate_deck()

    def generate_deck(self):
        """生成52张无鬼牌的扑克牌"""
        suits = ['♠', '♣', '♥', '♦']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'ACE']
        return [Card(suit, rank) for suit in suits for rank in ranks]

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)

    def deal(self, number_of_cards):
        """发牌"""
        return [self.cards.pop() for _ in range(number_of_cards)] if number_of_cards <= len(self.cards) else []
    
if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()
    print(deck.deal(5))

