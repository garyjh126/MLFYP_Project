from abc import abstractmethod, ABC, ABCMeta
import re
import Hand
import low_level_functions as llf
from includes import *
import heapq
import main as main
from collections import deque
from treys import Evaluator, Deck

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0
    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1
    def pop(self):
        return heapq.heappop(self._queue)[-1] # pop method returns the smallest item, not the largest

class Item:
    def __init__(self, action, position):
        self.action = action
        self.position = position
    def __repr__(self):
        return 'Item({!r})'.format(self.name)

# class EvaluationData():

#     def __init__(self, table_event):
#         self.table_event = table_event
#         self.he = ''
#         self.evaluation = ''
#         self.rc = '' 
#         self.score_desc = '' 
#         self.player_action = ''
    
    # def setAll(self, he, evaluation, rc, score_desc, player_action):
    #     self.he = he
    #     self.evaluation = evaluation
    #     self.rc = rc
    #     self.score_desc = score_desc
    #     self.player_action = player_action


class Player():
    game_state = {'hand_no': '',
                'dealer_position': '',
                'action_preflop': '',
                'flop1': '',
                'flop2': '',
                'flop3': '',
                'action_flop': '',
                'turn': '',
                'action_turn': '',
                'river': '',
                'action_river': ''}

    def __init__(self, ID, name, card_holding, position, GHB_file, cards,mwm,stack_size = 50):
        
        self.hand_num = 0
        self.cards = cards # cards passed in are all cards used in game
        self.ID = ID  ## acts as position tracker using 0 and 1
        self.name = name
        self.card_holding = card_holding # blank
        self.position = '' # blank
        self.GHB_file = GHB_file # give_hand_bot file
        self.mwm = mwm  ## UNKNOWN PURPOSE
        self.stack_size = stack_size
        #self.game_state = []
        self.dealer_status = False
        self.perspective_opposing_player = ['', ''] ## one for each of the opposing players. First is to left of this player. 
        #self.available_options = []
        self.evaluation_preflop = {'he': '', 'evaluation': '', 'rc': '', 'score_desc': '', 'player_action': ''}
        self.evaluation_flop = {'he': '', 'evaluation': '', 'rc': '', 'score_desc': '', 'player_action': ''}
        self.evaluation_turn = {'he': '', 'evaluation': '', 'rc': '', 'score_desc': '', 'player_action': ''}
        self.evaluation_river = {'he': '', 'evaluation': '', 'rc': '', 'score_desc': '', 'player_action': ''}
        self.round = {'moves_i_made_in_this_round_sofar': '', 'possible_moves': set([]), 'amount_owed_raises': 0}
        
                
    def __str__(self):
        st = self.ID, self.name, self.position, self.stack_size
        return 'ID: {}, Position: {}, \n\tEvaluation-Preflop: {}, \n\tRound: {}'.format(str(self.ID), str(self.position), str(self.evaluation_preflop), str(self.round))

    def debug_print(self, player_action):
        if (str(player_action)) != 'None':
            print(self, "\tplayer_action: ", player_action, "\taction_where: ", player_action.round_game)
            
        else:
            print(self, "\tplayer_action", "f")

        print


    

     # Previewing game_state for raises made previously and counting possible moves can be made as a result. 
    # Also populates player object with possible moves they may make after having seen the moves made so far.
    # Returns: count of raises made so far in current round, 
    def populatePlayerPossibleMoves(self, last_seq_move):
        last_seq_move = self.game_state['action_preflop']

        

        if(llf.count_r(last_seq_move) > 3):
            print("error: num or raises cannot be =", llf.count_r(last_seq_move), "\t", "bot_position",bot_position, "dealer_position", dealer_position)
        elif(llf.count_r(last_seq_move) == 3):
            self.round['possible_moves'].add('c')
            self.round['possible_moves'].add('f')
        else:
            self.round['possible_moves'].add('r')
            self.round['possible_moves'].add('c')
            self.round['possible_moves'].add('f')    

       


    
    
    def numRaisesDebt(self, event):
        dealer_position = self.game_state['dealer_position']
        last_seq_move = self.game_state['action_preflop'] # just for preflop
        bot_position = self.position  
        bot_position_num = self.stposition_to_numposition(bot_position)

        self.populatePlayerPossibleMoves(last_seq_move)
        count_raises_so_far_everyone = llf.count_r(last_seq_move) 
        count_raises_by_me = llf.count_r(self.round['moves_i_made_in_this_round_sofar'])


        self.round['amount_owed_raises'] = count_raises_so_far_everyone - count_raises_by_me
        
        # if(event == "Preflop"):

        #     if(bot_position == 'BTN'):

        #     elif(bot_position == 'SB'):

        #     elif(bot_position == 'BB'):

        
                

    def hand_evaluate_preflop(self, card_holding, name):
        event = 'Preflop'
        he = Hand.HandEvaluation(card_holding, name, event) #Unique to player instance
        evaluation, rc, score_desc, event = he.get_evaluation()
        self.numRaisesDebt(event)
        #self.getPerceivedRange(player1, player2) # Only use this if coming from CTB0 (learner)  
        player_action = self.take_action(he, evaluation, rc, score_desc, event) 
        self.debug_print(player_action)        
        return he, evaluation, rc, score_desc, player_action


    
    def hand_evaluate_flop(self, card_holding, name):
        event = 'Flop'
        he = Hand.HandEvaluation(self.card_holding, name, event) #Unique to player instance
        evaluation, rc, score_desc, event = he.get_evaluation()
        player_action = self.take_action(he, evaluation, rc, score_desc, event) ## FIX: Call correct actions once strategy has been dettermined for each betting round
        self.debug_print(player_action)        
        return he, evaluation, rc, score_desc, player_action

    def hand_evaluate_turn(self, card_holding, name):
        event = 'Turn'
        he = Hand.HandEvaluation(card_holding, name, event) #Unique to player instance
        evaluation, rc, score_desc, event = he.get_evaluation()
        player_action = self.take_action(he, evaluation, rc, score_desc, event) ## FIX: Call correct actions once strategy has been dettermined for each betting round
        self.debug_print(player_action)        
        return he, evaluation, rc, score_desc, player_action

    def hand_evaluate_river(self, card_holding, name):
        event = 'River'
        he = Hand.HandEvaluation(card_holding, name, event) #Unique to player instance
        evaluation, rc, score_desc, event = he.get_evaluation()
        player_action = self.take_action(he, evaluation, rc, score_desc, event) ## FIX: Call correct actions once strategy has been dettermined for each betting round
        self.debug_print(player_action)        
        return he, evaluation, rc, score_desc, player_action
        
    def stposition_to_numposition(self, st_bot_position):
        if st_bot_position == 'BTN':
            return 0
        elif st_bot_position == 'SB': 
            return 1
        elif st_bot_position == 'BB':
            return 2

    def is_possible(self, move):
        move_possible = False
        for item in self.round['possible_moves']:
            if item == move:
                return True
                break
        return move_possible    
        
            
    def take_action(self, he, evaluation, rc, score_desc, round_game):

        dealer_position = self.game_state['dealer_position']
        last_seq_move = self.game_state['action_preflop']
        bot_position = self.position  # DEBUG: self.position has not been assigned
        bot_position_num = self.stposition_to_numposition(bot_position)
        q = PriorityQueue()

        try:
            if (evaluation < preflop_range['betting'][self.round['amount_owed_raises']][bot_position_num]) and (self.is_possible('r')): 
                act = Bet(limit, round_game ,self)
                self.round['moves_i_made_in_this_round_sofar'] += 'r'
                return act
            elif evaluation < preflop_range['calling'][self.round['amount_owed_raises']][bot_position_num] and (self.is_possible('c')): 
                act = Call(limit, round_game,self)
                self.round['moves_i_made_in_this_round_sofar'] += 'c'
                return act
            else: 
                act = Fold(round_game, self)
                self.round['moves_i_made_in_this_round_sofar'] += 'f'
                return act
        except: 
            act = Fold(round_game, self)
            self.round['moves_i_made_in_this_round_sofar'] += 'f'
            return act  
            
        #if(round_game == 'Preflop'):
        # if(bot_position == 'BTN'):
        #     sb_move = ''
        #     bb_move = ''
        #     try: 
        #         sb_move = last_seq_move[-2]
        #     except:
        #         print("Cannot access sb_move with last_seq_move of length: ", len(last_seq_move))
        #     try: 
        #         bb_move = last_seq_move[-1]
        #     except:
        #         print("Cannot access bb_move with last_seq_move of length: ", len(last_seq_move))

        #     if(bb_move == 'r'):     
        #         q.push(Item('Raise', bot_position), 1)
        #         q.push(Item('Call', bot_position), 3) # Design Nueral network to learn these weights
        #         q.push(Item('Fold', bot_position), 3)
        #         act = Call(limit, round_game,self)
        #         return act
                
        #         if(sb_move == 'c'):
        #             q.push(Item('Raise', bot_position), 1)
        #             q.push(Item('Call', bot_position), 3) # Design Nueral network to learn these weights
        #             q.push(Item('Fold', bot_position), 3)
        #             act = Call(limit, round_game,self)
        #             return act

        #     elif(bb_move == 'c'):
        #         # q.push(Item('Raise', bot_position), 3)
        #         # q.push(Item('Call', bot_position), 2)
        #         # act = Bet(limit, round_game ,self)
                
        #         if(sb_move == 'c'):
        #             q.push(Item('Raise', bot_position), 1)
        #             q.push(Item('Call', bot_position), 3) # Design Nueral network to learn these weights
        #             q.push(Item('Fold', bot_position), 3)
        #             act = Call(limit, round_game,self)
        #             return act
                    

        #     if(len(last_seq_move) == 0): # very first move of game
        #         # limp_success_cfr = q.pop()
        #         q.push(Item('Raise', bot_position), 3)
        #         q.push(Item('Call', bot_position), 1) # Design Nueral network to learn these weights
        #         act = Bet(limit, round_game ,self)
        #         return act



        # elif(bot_position == 'SB'):

        #     btn_move = ''
        #     bb_move = ''

        #     try: 
        #         btn_move = last_seq_move[-1]
        #     except:
        #         print("Cannot access btn_move with last_seq_move of length: ", len(last_seq_move))
        #     try: 
        #         bb_move = last_seq_move[-2]
        #     except:
        #         print("Cannot access bb_move with last_seq_move of length: ", len(last_seq_move))
                
        #     if len(last_seq_move) == 1:
                
        #         if(btn_move == 'c'):
                    

        #             if evaluation < preflop_range['upper'][bot_position_num]['sb']: 
                        
        #                 act = Bet(limit, round_game ,self)
        #                 return act
        #             else:
        #                 act = Call(limit, round_game,self)
        #                 return act
        #         elif(btn_move == 'r'):
                    
        #             if evaluation < preflop_range['upper'][bot_position_num]['sb']: 
                        
        #                 act = Bet(limit, round_game ,self)
        #                 return act
        #             else:
        #                 act = Call(limit, round_game,self)
        #                 return act

        #     elif len(last_seq_move) == 2:  
        #         pass
                
            

        # elif(bot_position == 'BB'):
            
            # btn_move = ''
            # sb_move = ''

            # try: 
            #     sb_move = last_seq_move[-1]
            # except:
            #     print("Cannot access sb_move with last_seq_move of length: ", len(last_seq_move))
            # try: 
            #     btn_move = last_seq_move[-2]
            # except:
            #     print("Cannot access btn_move with last_seq_move of length: ", len(last_seq_move))

               

            # if len(last_seq_move) == 1:  ## SB is dealer preflop or btn is dealer postflop?? POSTFLOP because first condition is impossible
                
                # if(sb_move == 'c'):

                #     if evaluation < preflop_range['upper'][bot_position_num]['sb']: 
                        
                #         act = Bet(limit, round_game ,self)
                #         return act
                #     else:
                #         act = Call(limit, round_game,self)
                #         return act

                # elif(sb_move == 'r'):
                    
                #     if evaluation < preflop_range['upper'][bot_position_num]['sb']: 
                        
                #         act = Bet(limit, round_game ,self)
                #         return act
                #     else:
                #         act = Call(limit, round_game,self)
                #         return act

                
            
    

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

    #communication_files_directory='/usr/local/home/u180455/Desktop/Project/MLFYP_Project/MLFYP_Project/pokercasino/botfiles'
    communication_files_directory = main.path_to_file_changed2

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
    count_bets = {"Preflop":0, "Flop":0, "Turn":0, "River":0}
    def __init__(self, amount, round_game, player):
        self.amount = amount
        self.player = player
        self.count_bets[round_game] = self.count_bets[round_game] + 1
        self.round_game =  round_game
        self.send_file()
       # print("Player: {} bets {}".format(player.ID, amount))

    def __str__(self): 
        return "r"

    def determine_table_stats(self):
        pass

    def send_file(self):
        
        btc_file = ''
        if self.player.name == "Adam":
            btc_file = "botToCasino0"
        elif self.player.name == "Bill":
            btc_file = "botToCasino1"
        elif self.player.name == "Chris":
            btc_file = "botToCasino2"
        file_name = self.communication_files_directory + btc_file 
        try:
            with open(file_name, 'wt') as f:
                f.write('r')
                f.close()
        except:
            print("Could not write r to ", btc_file, "from", self.player.name)

    def populate_regret_table(self):
        pass

    def determine_action(self): pass

    def get_action_of_preceding_player(self): pass

class Call(Action):
    count_calls = {"Preflop":0, "Flop":0, "Turn":0, "River":0}
    def __init__(self, amount, round_game, player):
        self.amount = amount
        self.player = player
        self.count_calls[round_game] = self.count_calls[round_game] + 1
        self.round_game =  round_game
        self.send_file()
       # print("Player: {} calls".format(player.ID))
        
    def __str__(self): 
        return "c"

    def determine_action(self): 
        pass

    def determine_if_this_action_works(self):
        pass

    def determine_table_stats(self):
        pass

    def send_file(self):
        
        # btc_file = "/botToCasino0" if self.player.name == "Adam" else "/botToCasino1"
        btc_file = ''
        if self.player.name == "Adam":
            btc_file = "botToCasino0"
        elif self.player.name == "Bill":
            btc_file = "botToCasino1"
        elif self.player.name == "Chris":
            btc_file = "botToCasino2"
        file_name = self.communication_files_directory + btc_file 
        try:
            with open(file_name, 'wt') as f:
                f.write('c')
                f.close()
        except:
            print("Could not write r to ", btc_file, "from", self.player.name)

    def get_action_of_preceding_player(self):
        pass

    def populate_regret_table(self):
        pass


class Fold(Action):
    count_folds = {"Preflop":0, "Flop":0, "Turn":0, "River":0}
    def __init__(self, round_game, player):
        self.player = player
        self.count_folds[round_game] = self.count_folds[round_game] + 1
        self.round_game =  round_game
        self.send_file()

    def determine_table_stats(self):
        pass

    def send_file(self):
        btc_file = ''
        if self.player.name == "Adam":
            btc_file = "botToCasino0"
        elif self.player.name == "Bill":
            btc_file = "botToCasino1"
        elif self.player.name == "Chris":
            btc_file = "botToCasino2"
        file_name = self.communication_files_directory + btc_file 
        with open(file_name, 'wt') as f:
            f.write('f')
            f.close()

    def get_action_of_preceding_player(self):
        pass

    def __str__(self): 
        return "f"

    def populate_regret_table(self):
        pass