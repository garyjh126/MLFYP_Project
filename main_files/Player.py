from abc import abstractmethod, ABC, ABCMeta
import re
import Hand
import low_level_functions as llf
from includes import *
import heapq
import main as main


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0
    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1
    def pop(self):
        return heapq.heappop(self._queue)[-1]

   

class Item:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'Item({!r})'.format(self.name)

class Player():
    game_state = []
    def __init__(self, ID, name, card_holding, position, GHB_file, cards,mwm,stack_size = 50):
        self.hand_num = 0
        self.cards = cards
        self.ID = ID
        self.name = name
        self.card_holding = card_holding
        self.position = ''
        self.GHB_file = GHB_file 
        self.mwm = mwm
        self.stack_size = stack_size
        #self.game_state = []
        self.dealer_status = False
        self.perspective_opposing_player = ''
        #self.available_options = []
        
        
    def __str__(self):
        st = self.ID, self.name, self.position, self.stack_size
        return 'ID: {}, Name: {}, Position: {}, Stack Size: {}'.format(str(self.ID), str(self.name), str(self.position), str(self.stack_size))
        
    def get_opposing_player(self):
        g = main.Game
        player_list = g.return_table_list
        for player_num in range(len(player_list)):
            if player_list[player_num] == self:
                if player_num == 0:
                    return player_list[1]
                elif player_num == 1:
                    return player_list[0]
        

    def hand_evaluate_preflop(self, card_holding, name):
        he = Hand.HandEvaluation(card_holding, name, event = 'Preflop') #Unique to player instance
        evaluation, rc, score_desc, event = he.get_evaluation()
        player_action = self.take_action_preflop(he, evaluation, rc, score_desc)
        return he, evaluation, rc, score_desc, player_action

    def take_action_preflop(self, he, evaluation, rc, score_desc):
        # Hand strength is valued on a scale of 1 to 7462, where 1 is a Royal Flush and 7462 is unsuited 7-5-4-3-2, as there are only 7642 
        # distinctly ranked hands in poker. 
        
        q = PriorityQueue()
        #print(self.name, self.game_state)
        def i_am_dealer():

            print("last move: ", Player.game_state[len(Player.game_state)-1])
            # Assuming no 3-bets
            #get preceding move
            
            if(Player.game_state[len(Player.game_state)-1] == 'r'):     
                
                # opposing player is strong/aggresive/trying to win pot
                self.perspective_opposing_player = 'Aggressive'
                # Available options: rcf
                #print("case 1\t", self.game_state[len(self.game_state)-1])
                #print("\n")

                q.push(Item('Raise'), 1)
                q.push(Item('Call'), 3)
                q.push(Item('Fold'), 3)

                act = Call(limit, self)
                return act
                #print("i_am_dealer_preflop_r")
            elif(Player.game_state[len(Player.game_state)-1] == 'c'):
                # is_he_limping/seeing a flop cheaply?
                self.perspective_opposing_player = 'Limping'
                # Available options: rc
                #print("case 2\t", self.game_state[len(self.game_state)-1])
                #print("\n")

                q.push(Item('Raise'), 3)
                q.push(Item('Call'), 2)

                act = Bet(limit, self)
                return act
                #print("i_am_dealer_preflop_c")

            elif(Player.game_state[len(Player.game_state)-1] == 'f'): ## If player folds a free hand, there may be an ISSUE with bots strategy
                # I won game
                #print("case 3\t", self.game_state[len(self.game_state)-1])
                #print("\n")
                pass

        def not_dealer():
            act_string = 'a'
            # Has first move 
            #global act_string
            if evaluation < preflop_range_upper_notdealer: 
                

                act = Bet(limit, self)
                #global act_string
                #print("case 4\n")
                act_string = 'r'
                #print(act_string)
                return act_string

            else:

                act = Call(limit, self)
                #global act_string
                #print("case 5\n")
                act_string = 'c'
                return act_string
            #print("act_string", act_string)
        #act = Bet(limit, self)
            # if evaluation < pref  lop_range_upper_truedealer: 
            #     act = Bet(limit, self)
            # else:
            #     act = Fold(self)
            # if 

        
       

        is_dealer = self.dealer_status
        #dealer is last to move on preflop
        if(is_dealer): #if i_am_first_to_act_in_street == False: ## I am dealer
            action_taken = i_am_dealer()
            return action_taken

        else:
            action_taken = not_dealer()
            return action_taken
            # I am not dealer 
            
        
         
        # elif evaluation >= cut_lower and evaluation < cut_upper:
        #     act = Call(limit, self)
        # else:
        #     #First check if free to fold but do this in subclass
        #     act = Fold()
       
    def take_action_flop(self, he, evaluation, rc, score_desc):
        # Hand strength is valued on a scale of 1 to 7462, where 1 is a Royal Flush and 7462 is unsuited 7-5-4-3-2, as there are only 7642 
        # distinctly ranked hands in poker. 
        act = Action(self)
        position = self.position
       

        #self.CFR_table[]
    

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
class Action(ABC):

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

    @abstractmethod
    def __str__(self): 
        return "A"    


class Bet(Action):

    def __init__(self, amount, player):
        self.amount = amount
        self.player = player
        self.send_file()
        #print("Player: {} bets {}".format(player.ID, amount))

    def __str__(self): 
        return "r"

    def determine_table_stats(self):
        pass

    def send_file(self):
        
        btc_file = "/botToCasino0" if self.player.name == "Adam" else "/botToCasino1"
        #print("printing bet to file", btc_file)
        file_name = self.communication_files_directory + btc_file 
        #print(file_name)
        with open(file_name, 'wt') as f:
            f.write('r')
            f.close()

    def populate_regret_table(self):
        pass

    def determine_action(self): pass

    def get_action_of_preceding_player(self): pass

class Call(Action):
    def __init__(self, amount, player):
        self.amount = amount
        self.player = player
        self.send_file()
        #print("Player: {} calls {}".format(player.ID, amount))
        
    def __str__(self): 
        return "c"

    def determine_action(self): 
        pass

    def determine_if_this_action_works(self):
        pass

    def determine_table_stats(self):
        pass

    def send_file(self):
        
        btc_file = "/botToCasino0" if self.player.name == "Adam" else "/botToCasino1"
        #print("printing call to file", btc_file)
        file_name = self.communication_files_directory + btc_file 
        with open(file_name, 'wt') as f:
            f.write('c')
            f.close()

    def get_action_of_preceding_player(self):
        pass

    def populate_regret_table(self):
        pass


class Fold(Action):

    def __init__(self, player):
        pass#print("Player: {} folds".format(player.ID))

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