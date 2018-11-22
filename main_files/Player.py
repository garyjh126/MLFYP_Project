from abc import abstractmethod, ABCMeta
import re
import Hand
class Player():

    def __init__(self, ID, name, card_holding, position, GHB_file, cards,mwm,stack_size = 50):
        self.cards = cards
        self.ID = ID
        self.name = name
        self.card_holding = card_holding
        self.position = position
        self.GHB_file = GHB_file 
        self.mwm = mwm
        self.stack_size = stack_size
        self.game_state = []
        
    def __str__(self):
        st = self.ID, self.name, self.position, self.stack_size
        return 'ID: {}, Name: {}, Position: {}, Stack Size: {}'.format(str(self.ID), str(self.name), str(self.position), str(self.stack_size))
        
    def hand_evaluate_preflop(self, card_holding, name):
        he = Hand.HandEvaluation(card_holding, name, event = 'Preflop') #Unique to player instance
        evaluation, rc, score_desc, event = he.get_evaluation()
        
        self.take_action_flop(he, evaluation, rc, score_desc)
        return he, evaluation, rc, score_desc, event 

    def take_action_flop(self, he, evaluation, rc, score_desc):
        # Hand strength is valued on a scale of 1 to 7462, where 1 is a Royal Flush and 7462 is unsuited 7-5-4-3-2, as there are only 7642 
        # distinctly ranked hands in poker. Once again, refer to my blog post for a more mathematically complete explanation of why this is so.
        limit = 5
        act = Action()
        position = self.position
        game_state = self.game_state
        #print(position, game_state)

        #self.CFR_table[]
        cut_lower = 3000
        cut_upper = 7000

        # How tight do I want to play? This will determine the cut values. 
        # It depends on my current position and values from the CFR table. 
        # If a hand has a low evaluation but negative regret, then it may 
        # be preferable to fold.

        if evaluation < cut_lower:  ## Account for position
            act = Bet(limit, self)
        elif evaluation >= cut_lower and evaluation < cut_upper:
            act = Call(limit, self)
        else:
            #First check if free to fold but do this in subclass
            act = Fold()

    def hand_evaluate_flop(self, card_holding, name):
        limit = 5
        he = Hand.HandEvaluation(self.card_holding, name, event = 'Flop') #Unique to player instance
        #print(he)   

        #  for starting training, if hand is "sufficiently good" (If evaluation score is good), then c/r. 
        # Otherwise fold. 
        my_eval_score = he.get_evaluation()[0]
        if my_eval_score < 3000:  ## Account for position
            act = Bet(limit, self)
        elif my_eval_score >= 3000 and my_eval_score < 7000:
            act = Call(limit, self)
        else:
            #First check if free to fold but do this in subclass
            act = Fold()

    def GHB_Parsing(self, GHB_Status):
        
        # GHB_STATUS = <hand number>D<button position>A<holecard1>B<holecard2>
        # cards are 4 * rank + suit where rank is 0 .. 12 for deuce to ace, and suits is 0 .. 3

        #restrict to just give_hand_bot files
        deck_size = 52
        arr = re.split(r'[DAB]',GHB_Status)
        suits = ['h','c','s','d']
        card_a = arr[2] #card from file / REPRESENTS INDEX OF SELF.CARDS
        card_a_suit = ''
        card_a_rank = ''
        card_b = arr[3] #card from file / REPRESENTS INDEX OF SELF.CARDS
        card_b_suit = ''
        card_b_rank = ''
        a,b,c,x,y,z = ('', '', '', '', '', '')
        for card in self.cards:
            if(str(self.cards.index(card)) == card_a):
                if(len(card) == 2):
                    a,b = card
                # elif(len(card) == 3):
                #     a,b,c = card
                #     a = a+b
                #     b = c
            elif(str(self.cards.index(card))== card_b):
                if(len(card) == 2):
                    x,y = card
                elif(len(card) == 3):
                    x,y,z = card
                    x = x+y
                    y = z
        card_a_rank = a
        card_a_suit = b
        card_b_rank = x
        card_b_suit = y
        self.card_holding = CardHolding(self.name,card_a_suit,card_a_rank,card_b_suit, card_b_rank)
       
        return self.card_holding

class CardHolding(Player):

    def __init__(self, name, first_card_suit, first_card_rank, second_card_suit, second_card_rank):
        self.name = name
        self.first_card_suit = first_card_suit
        self.first_card_rank = first_card_rank
        self.second_card_suit = second_card_suit
        self.second_card_rank = second_card_rank

    def __str__(self):
        first_card = self.first_card_suit, self.first_card_rank
        second_card = self.second_card_suit, self.second_card_rank
        st = 'Name: {}'.format(self.name) + '\tFirst Card: {}'.format(str(first_card)) + '\tSecond Card: {}\n'.format(str(second_card))
        return (str(st))
    
    def get_card(self, card_no):
        if card_no == 0:
            return self.first_card_rank + self.first_card_suit
            
        else:
            return self.second_card_rank,self.second_card_suit

#INTERFACE
class Action(object):

    __metaclass_ = ABCMeta

    communication_files_directory='/usr/local/home/u180455/Desktop/Project/MLFYP_Project/MLFYP_Project/pokercasino/botfiles'
    @abstractmethod
    def determine_action(self): pass

    @abstractmethod
    def determine_table_stats(self): pass

    @abstractmethod
    def send_file(self): pass

    @abstractmethod
    def get_action_of_preceding_player(self): pass

    @abstractmethod
    def populate_regret_table(self): pass


class Bet(Action):

    def __init__(self, amount, player):
        self.amount = amount
        self.player = player

    def determine_table_stats(self):
        pass

    def send_file(self):
        btc_file = "botToCasino0" if self.player.name == "Adam" else "botToCasino1"
        file_name = self.communication_files_directory + btc_file 
        with open(file_name, 'wt') as f:
            f.write('r')

    def populate_regret_table(self):
        pass


class Call(Action):
    def __init__(self, amount, player):
        self.amount = amount
        self.player = player

    def determine_if_this_action_works(self):
        pass

    def determine_table_stats(self):
        pass

    def send_file(self):
        btc_file = "botToCasino0" if self.player.name == "Adam" else "botToCasino1"
        file_name = self.communication_files_directory + btc_file 
        with open(file_name, 'wt') as f:
            f.write('c')

    def get_action_of_preceding_player(self):
        pass

    def populate_regret_table(self):
        pass


class Fold(Action):

    def __init__(self):
        pass

    def determine_action(self):
        pass

    def determine_table_stats(self):
        pass

    def send_file(self):
        pass

    def get_action_of_preceding_player(self):
        pass

    def populate_regret_table(self):
        pass