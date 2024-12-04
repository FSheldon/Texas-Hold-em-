from game_logic import PokerGame

class Card:
    """简单定义一个卡牌类用于测试"""
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"


def test_is_straight():
    """测试 is_Straight 方法"""
    game = PokerGame(players=[], big_blind=10)  # 创建游戏实例

    # 定义七张测试用的牌
    cards = [
        Card('J', 'Hearts'),
        Card('8', 'Hearts'),
        Card('A', 'Hearts'),
        Card('9', 'Spades'),
        Card('K', 'Clubs'),
        Card('J', 'Spades'),
        Card('3', 'Spades'),
    ]

    # 调用 is_Straight 方法
    print(f"DEBUG: 调用 is_Straight 方法，输入牌: {[str(card) for card in cards]}")
    result = game.is_Straight(cards)
    print(f"是否存在顺子: {result}")


def test_get_straight_high():
    """测试 get_straight_high 方法"""
    game = PokerGame(players=[], big_blind=10)  # 创建游戏实例

    # 定义七张测试用的牌
    cards = [
        Card('J', 'Hearts'),
        Card('8', 'Hearts'),
        Card('A', 'Hearts'),
        Card('9', 'Spades'),
        Card('Q', 'Clubs'),
        Card('J', 'Spades'),
        Card('10', 'Diamonds'),
    ]

    print(f"DEBUG: 调用 get_straight_high 方法，输入牌: {[str(card) for card in cards]}")
    
    try:
        # 调用 get_straight_high 方法并跟踪执行流程
        ranks = [game.card_value(card.rank) for card in cards]
        print(f"DEBUG: 原始牌值: {ranks}")
        
        ranks = list(set(ranks))  # 去重
        print(f"DEBUG: 去重后的牌值: {ranks}")
        
        ranks.sort()
        print(f"DEBUG: 排序后的牌值: {ranks}")

        high_card = game.get_straight_high(cards)
        print(f"DEBUG: 最高顺子牌: {high_card if high_card > 0 else '没有顺子'}")
    except Exception as e:
        print(f"ERROR: 调用 get_straight_high 时发生错误: {e}")
        print("DEBUG: ranks 列表的长度和内容:")
        print(f"DEBUG: ranks = {ranks}, len(ranks) = {len(ranks)}")


if __name__ == "__main__":
    print("测试 is_Straight 方法:")
    test_is_straight()
    print("\n测试 get_straight_high 方法:")
    test_get_straight_high()
