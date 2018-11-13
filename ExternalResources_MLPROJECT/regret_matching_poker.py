from __future__ import division
import re
from random import random
import numpy as np
import pandas as pd
import os
import uuid
from abc import abstractmethod, ABCMeta
import pyinotify

class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_ACCESS(self, event):
        pass #print "ACCESS event:", event.pathname

    def process_IN_ATTRIB(self, event):
        pass #print "ATTRIB event:", event.pathname

    def process_IN_CLOSE_NOWRITE(self, event):
        pass #print "CLOSE_NOWRITE event:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        pass #print "CLOSE_WRITE event:", event.pathname

    def process_IN_CREATE(self, event):
        pass #print "CREATE event:", event.pathname

    def process_IN_DELETE(self, event):
        pass #print "DELETE event:", event.pathname

    def process_IN_MODIFY(self, event):
        pass #print "MODIFY event:", event.pathname

    def process_IN_OPEN(self, event):
        pass #print "OPEN event:", event.pathname

class main_watch_manager():
    
    def __init__(self, communication_files_directory='/usr/local/home/u180455/Desktop/Project/MLFYP_Project/MLFYP_Project/pokercasino/botfiles'):
        self.communication_files_directory = communication_files_directory

        # watch manager
        wm = pyinotify.WatchManager()
        wm.add_watch(self.communication_files_directory, pyinotify.ALL_EVENTS, rec=True)

        # event handler
        eh = MyEventHandler()

        # notifier
        notifier = pyinotify.Notifier(wm, eh)
        notifier.loop()

    def get_status_from_CTB_file(self, CTB_file):
        data = ''
        with open(self.communication_files_directory + CTB_file, 'rt') as f:
            data = f.read()
        return data

    


'''
    Use regret-matching algorithm to play Poker
'''






class Game:

    cards = []

    def __init__(self, max_game=5):
         
        
        Player1 = Player(uuid.uuid1() ,'Adam', CardHolding('-','-','-','-'), 'BTN', '/give_hand_bot0', None)
        Player2 = Player(uuid.uuid1() ,'Bill', CardHolding('-','-','-','-'), 'SB', '/give_hand_bot1', None)
        Player3 = Player(uuid.uuid1() ,'Chris', CardHolding('-','-','-','-'), 'BB', '/give_hand_bot2', None)
        Player4 = Player(uuid.uuid1() ,'Dennis', CardHolding('-','-','-','-'), 'CO', '/give_hand_bot3',None)
        self.player_list = [Player1, Player2, Player3, Player4]
        positions_at_table = {0: Player1.position, 1: Player2.position, 2: Player3.position, 3: Player4.position} # mutable
        cards = self.create_cards_for_game()
        # Create more players for Poker game
        self.table = Table(self.player_list, positions_at_table)
        self.max_game = max_game
        self.parse_data_from_CTB()
        #self.table.assign_cards_per_player_at_table()

        

    def parse_data_from_CTB(self):
        
        for player in self.player_list: 
            player.mwm_bot = main_watch_manager()   
            player_mwm = player.mwm_bot
            CTB_Status = player_mwm.get_status_from_CTB_file(player.CTB_file)
            player.CTB_Parsing(CTB_Status)

    def create_cards_for_game(self):
        suits = ['h','c','s','d']
        cards = []
       
        for suit in suits:
            for rank in range(13):
                card_str = str(rank)+suit
                cards.append(card_str)
                
        return cards
    

class Table(Game):

    num_of_players = 0

    def __init__(self, player_list, positions_at_table):
        self.player_list= list(player_list)
        #print(type(player_list))
        for i in player_list:
            Table.num_of_players += 1
        self.positions_at_table = positions_at_table.copy()

    def get_players_at_table(self):
        return self.player_list

    def get_player_at_position(self, position):
        for i in self.player_list:
            if i.position == position:
                return i

    def get_player_by_ID(self, ID):
        for player in self.player_list:
            if player.ID == ID:
                return player

    def get_position_of_player(self, player):
        for i in self.player_list:
            if i == player:
                return i.position

    def get_number_of_players(self):
        return self.num_of_players

    def rotate(self):
        keys = self.positions_at_table.keys()
        values = self.positions_at_table.values()
        shifted_values = values.insert(0, values.pop())
        new_positions_at_table = dict(zip(keys, shifted_values))
        self.positions_at_table = new_positions_at_table

    def remove_player(self, player):
        for i in self.player_list:
            if i == player:
                self.player_list.remove(player)
        for index, pos in self.positions_at_table.items():
            if pos == player.position:
                del self.positions_at_table[pos]
                self.reinstantiate_positions_at_table(pos)

    def reinstantiate_positions_at_table(self, player_to_remove):
        keys = []
        for index in range(len(self.positions_at_table)):
            keys.append(index)
        values = self.positions_at_table.values()
        new_dict = dict(zip(keys, values))
        self.positions_at_table = new_dict

    



class Player(Game):


    def __init__(self, ID, name, card_holding, position, CTB_file, mwm, stack_size = 50):
        self.ID = ID
        self.name = name
        self.card_holding = card_holding
        self.position = position
        self.strategy, self.avg_strategy,\
        self.strategy_sum, self.regret_sum = np.zeros((4, 3))
        self.list_of_actions_game = np.array([])
        self.CTB_file = CTB_file
        self.mwm = mwm
        self.stack_size = stack_size
        self.action = ''

    def __str__(self):
        return self.name

    def take_action(self):
        pass

    def CTB_Parsing(self, CTB_Status):
        # CTB_STATUS = <hand number>D<button position>A<holecard1>B<holecard2>
        # cards are 4 * rank + suit where rank is 0 .. 12 for deuce to ace, and suits is 0 .. 3

        deck_size = 52
        arr = re.split(r'[DAB]',CTB_Status)
        print(arr) #debug
        suits = ['h','c','s','d']

        card_a = arr[2] 
        card_a_suit = ''
        card_a_rank = 0
        for card in Game.cards:
            for suit in suits:
                st = re.split(r'[]',card)
                if card_a % 4 == suits.index(suit):
                    card_a_suit = suit
                card_a_rank

        for card in Game.cards:
            if card_b == card:
                card_b = card


        # card_A = arr[2] 
        # card_a_suit = card_A / deck_size

        # card_b = arr[3]
        # card_b_suit = card_B / deck_size
        
        # card_ranks = {a: 0, b: 0}

        # for rank in card_ranks:
        #     for partition in partitions:
        #         note_partition = partitions[0]
        #         if card_ranks[rank] > partition:
        #             pass
        #         else:
        #             note_partition = partition
        #             break
            

       
            

    def assign_cards(self, cards):
        self.card_holding = cards
                


class CardHolding(Player):

    def __init__(self, first_card_suit, first_card_rank, second_card_suit, second_card_rank):
        self.first_card_suit = first_card_suit
        self.first_card_rank = first_card_rank
        self.second_card_suit = second_card_suit
        self.second_card_rank = second_card_rank

    def __str__(self):
        return self.first_card_suit, self.first_card_rank, self.second_card_suit, self.second_card_rank



#INTERFACE
class Action(Player):

    __metaclass_ = ABCMeta


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

    def __init__(self, amount):
        self.amount = amount

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




class Call(Action):
    def __init__(self, amount):
        self.amount = amount

    def determine_if_this_action_works(self):
        pass

    def determine_table_stats(self):
        pass

    def send_file(self):
        pass

    def get_action_of_preceding_player(self):
        pass

    def populate_regret_table(self):
        pass

class Fold(Action):

    def __init__(self, amount):
        self.amount = amount

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


class PokerRound(Table):

    poker_round_count = 0

    def __init__(self, sb, bb, pot):
        PokerRound.poker_round_count += 1
        self.sb = sb
        self.bb = bb
        self.pot = pot

    def deal_holecards(self):
        pass


if __name__ == '__main__':

    game = Game()

    #os.remove("strategy_stats.txt")
    #print('==== Use simple regret-matching strategy === ')
    #game.play()
    #print('==== Use averaged regret-matching strategy === ')
    #game.conclude()
    #game.play(avg_regret_matching=True)
