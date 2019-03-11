from itertools import combinations 
from treys import Deck, Card, Evaluator
evaluator = Evaluator()
class Cards():

    def __init__(self):
        self.deck_of_cards = self.create_cards_for_game()
        self.our_cards = None
        self.board = None
        self.opp_cards = None
        self._combinations = self.make_combinations()

    def make_combinations(self):
        _combinations = list(combinations(self.deck_of_cards, 2))
        for combo in _combinations:
            combo = self.parse_cards(combo[0], combo[1])
        return _combinations        

    def parse_cards(self, a, b):
        a_rank, a_suit = a
        b_rank, b_suit = b
        a_card = Card.new(str(a_rank) + str(a_suit))
        b_card = Card.new(str(b_rank) + str(b_suit))
        return [a_card, b_card]

    def create_cards_for_game(self):
        suits = ['h','c','s','d']
        li = []
        
        for rank in range(13):
            for suit in suits:
                if(rank == 8):
                    card_r = 'T'
                elif(rank == 9):
                    card_r = 'J'
                elif(rank == 10):
                    card_r = 'Q'
                elif(rank == 11):
                    card_r = 'K'
                elif(rank == 12):
                    card_r = 'A'
                else:
                    card_r = str(rank+2)
                card_str = card_r+suit
                li.append(card_str)
                
        return li

    def setup_board(self, board):
        a_rank, a_suit = board[0]
        b_rank, b_suit = board[1]
        c_rank, c_suit = board[2]
        a_card = Card.new(str(a_rank) + str(a_suit))
        b_card = Card.new(str(b_rank) + str(b_suit))
        c_card = Card.new(str(c_rank) + str(c_suit))
        self.board = [a_card, b_card, c_card]
        return [a_card, b_card, c_card]

    def take(self, num_take):
        import random
        cards = []
        for num in range(num_take):
            c = random.choice(self.deck_of_cards)
            assert c not in cards
            cards.append(c)
            self.deck_of_cards.remove(c)
        return cards
    
    def shares_duplicate(self, a, b):
        check_cards = self.our_cards + self.board
        for card in check_cards:
            if a in check_cards or b in check_cards:
                return True
            else:
                return False

    def handStrength(self):
        ahead, tied, behind = 0, 0, 0
        a, b = None, None
        ourRank = evaluator.evaluate(self.our_cards, self.board)
        # Consider all two card combinations of remaining cards
        for potential_opp_cards in (self._combinations):
            a, b = Card.new(potential_opp_cards[0]), Card.new(potential_opp_cards[1])
            if self.shares_duplicate(a,b):
                continue
            oppRank = evaluator.evaluate([a,b], self.board)
            if(ourRank < oppRank): # Note: With treys evaluation, lower number means better hand
                ahead = ahead + 1 
            elif ourRank == oppRank:
                tied = tied + 1
            else:
                behind = behind + 1
        hand_strength = (ahead+tied/2) / (ahead+tied+behind)
        return hand_strength

deck = Cards()

deck.our_cards = deck.take(2)
deck.board = deck.take(3)
deck.our_cards = deck.parse_cards(deck.our_cards[0], deck.our_cards[1])
deck.board = deck.setup_board(deck.board)

hand_strength = deck.handStrength()
print("Our_cards")
print(Card.print_pretty_cards(deck.our_cards))
print("Board")
print(Card.print_pretty_cards(deck.board))

print("\nHand Strength: ", hand_strength)




