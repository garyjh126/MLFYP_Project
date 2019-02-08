import regret_matching_poker as rm_poker
from treys import *
import Player as p
from low_level_functions import from_num_to_cardstring
class HandEvaluation():

    def __init__(self, card_holding, playerID, evaluation = None, event = "Preflop"):
        self.card_holding = card_holding
        self.card_a, self.card_b = self.parse_cards()
        self.summary = self.evaluate(event)
        self.evaluation = self.summary[0]
        self.rc = self.summary[1]
        self.event = self.summary[3]
        self.playerID = playerID  # player name

    def __str__(self):
        st = "{}\t\t Player ID: {}\n".format(self.event, self.playerID) if self.event=="Preflop" else "{}\t\t\t Player ID: {}\n".format(self.event, self.playerID) 
        st += "Cards: {}{}\n".format(Card.int_to_pretty_str(self.hand[0]), Card.int_to_pretty_str(self.hand[1]))
        st += "Board {}{}{}\n".format(Card.int_to_pretty_str(self.board[0]), Card.int_to_pretty_str(self.board[1]), Card.int_to_pretty_str(self.board[2]))
        st += "Evaluation: {} ({}), Rank_Class: {}, \n".format(self.evaluation[0], self.evaluation[2], self.evaluation[1]) if self.event=="Preflop" else "Evaluation: {} ({}), Rank_Class: {}, \n-----------------".format(self.evaluation[0], self.evaluation[2], self.evaluation[1])
        return st

    def parse_cards(self):
        a, b = self.card_holding.get_card(0) , self.card_holding.get_card(1)
        a_rank, a_suit = a
        b_rank, b_suit = b
        
        a_card = Card.new(str(a_rank) + str(a_suit))
        b_card = Card.new(str(b_rank) + str(b_suit))
    
        return [a_card, b_card]

    def parse_flop_cards(self):
        #work on this parsing Saturday Feb 02
        a, b, c = p.Player.game_state['flop1'], p.Player.game_state['flop2'], p.Player.game_state['flop3']
        card1 = from_num_to_cardstring(a)
        card2 = from_num_to_cardstring(b)
        card3 = from_num_to_cardstring(c)
        if card1 == '' or card2 == '' or card3 == '':
            deck = Deck()
            b = deck.draw(3)
            return Card.int_to_str(b[0]), Card.int_to_str(b[1]), Card.int_to_str(b[2])
        else:
            return card1, card2, card3
        
    def setup_board(self, board, random, hand = None):
        
            
        #Example board -- DEBUG
        b = []
        if random == 'False': #FLOP
            #import from file giving hand status
            for card in board:
                c = Card.new(card)
                b.append(c)
        if board == None and random == 'True': #PREFLOP
            deck = Deck()
            b = deck.draw(3)
        return b

    def evaluate(self, event):
        evaluator = Evaluator()
        self.hand = self.parse_cards()
        self.board = ''
        if event == "Preflop":
            self.board = self.setup_board(None, 'True', self.hand)
        else:
            self.flop_cards = self.parse_flop_cards()
            if(self.flop_cards != 'Blank'):
                self.board = self.setup_board(self.flop_cards, 'False', self.hand)   
        evaluation = evaluator.evaluate(self.hand, self.board)
        rc = self.rank_class(evaluator, evaluation)
        score_desc = evaluator.class_to_string(rc)
        return evaluation, rc, score_desc, self.hand, self.board
        
    def rank_class(self, evaluator, evaluation):
        rc = evaluator.get_rank_class(evaluation)
        return rc

    def get_evaluation(self):
        return self.summary
