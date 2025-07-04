from treys import Card, Deck, Evaluator

class PokerSimulator:
    def __init__(self, player_profiles):
        self.player_profiles = player_profiles
        self.deck = Deck()
        self.deck.shuffle()
        self.evaluator = Evaluator()

    def deal_hands(self):
        return {player: [self.deck.draw(1)[0], self.deck.draw(1)[0]] 
            for player in self.player_profiles}
    
    def deal_board(self):
        return self.deck.draw(5)

    def evaluate_hands(self, hands, board):
        return {player: self.evaluator.evaluate(board, hand)
                for player, hand in hands.items()}

    def find_winner(self, scores):
        return min(scores, key=scores.get)

    def simulate_hand(self):
        hands = self.deal_hands()
        board = self.deal_board()
        scores = self.evaluate_hands(hands, board)
        winner = self.find_winner(scores)

        readable_board = [Card.int_to_pretty_str(c) for c in board]
        readable_hands = {
            player: [Card.int_to_pretty_str(c) for c in hand]
            for player, hand in hands.items()
        }

        return {
            "board": readable_board,
            "hands": readable_hands,
            "scores": scores,
            "winner": winner
        }