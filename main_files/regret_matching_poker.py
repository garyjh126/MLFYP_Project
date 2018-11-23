from __future__ import division
import re
from random import random
import numpy as np
import pandas as pd
import os
import uuid

import pyinotify
from treys import *
import Hand
import Player as p

most_recent_file_changed = ''


class Game:

    cards = []

    def __init__(self, max_game=5):
        global cards
        cards = self.create_cards_for_game() 
        Player1 = p.Player(uuid.uuid1() ,'Adam', p.CardHolding('-','-','-','-','-'), 'BTN', '/give_hand_bot0', cards, None)
        Player2 = p.Player(uuid.uuid1() ,'Bill', p.CardHolding('-','-','-','-','-'), 'SB', '/give_hand_bot1', cards, None)
        #Player3 = Player(uuid.uuid1() ,'Chris', CardHolding('-','-','-','-','-'), 'BB', '/give_hand_bot2', cards, None)
        #Player4 = Player(uuid.uuid1() ,'Dennis', CardHolding('-','-','-','-','-'), 'CO', '/give_hand_bot3', cards, None)
        self.player_list = [Player1, Player2] #, Player3, Player4]
        positions_at_table = {0: Player1.position, 1: Player2.position} #, 2: Player3.position, 3: Player4.position} # mutable
        self.table = Table(self.player_list, positions_at_table)
        self.max_game = max_game
        self.parse_data_from_GHB()

    def parse_data_from_GHB(self):

        self.main_watch_manager = main_watch_manager(self.player_list)
        
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


def get_status_from_file(file_name):
    data = ''
    with open('/usr/local/home/u180455/Desktop/Project/MLFYP_Project/MLFYP_Project/pokercasino/botfiles/' + file_name, 'rt') as f:
        data = f.read()
    return data
    

class MyEventHandler(pyinotify.ProcessEvent):

    casino_to_bot_list_b1 = []
    times = 0

    def my_init(self, **kargs):
        """
        This is your constructor it is automatically called from
        ProcessEvent.__init__(), And extra arguments passed to __init__() would
        be delegated automatically to my_init().
        """
        self.player_list = kargs["player_list"]

    def process_IN_CLOSE_WRITE(self, event):
        ### declaring a bot_number and event_type 
        #print(event.pathname)
        global file_changed
        arr = re.split(r'[/]',event.pathname)
        most_recent_file_changed = (arr[len(arr)-1])
        last_letter = most_recent_file_changed[len(most_recent_file_changed)-1]
        bot_number = last_letter if (last_letter =='0' or last_letter == '1') else ''
        event_type = most_recent_file_changed if bot_number == '' else most_recent_file_changed[0:len(most_recent_file_changed)-1]
        filename = str(event_type+bot_number)
        file_data = get_status_from_file(str(filename))

        if event_type == "give_hand_bot":
        
            # for i in range(len(self.player_list)):
            if bot_number == '0':
                self.player_list[0].card_holding = self.player_list[0].GHB_Parsing(file_data) #check cards
                #print(self.player_list[0].card_holding)
                he, evaluation, rc, score_desc, _ = self.player_list[0].hand_evaluate_preflop(self.player_list[0].card_holding, self.player_list[0].name)
                print(he, evaluation, rc, score_desc)

            elif bot_number == '1':
                self.player_list[1].card_holding = self.player_list[1].GHB_Parsing(file_data) #check cards
                #print(self.player_list[0].card_holding)
                he, evaluation, rc, score_desc, _ = self.player_list[1].hand_evaluate_preflop(self.player_list[1].card_holding, self.player_list[1].name)
                print(he, evaluation, rc, score_desc)

        if event_type == "casinoToBot":   
            
            if bot_number == '0':
                #self.player_list[0].game_state = self.casinoToBot_Parsing(file_data) #check cards
                pass

            elif bot_number == '1':
                self.player_list[1].game_state.append(self.casinoToBot_Parsing(file_data)) #check cards
                #print(self.player_list[1].game_state)

 

    def casinoToBot_Parsing(self, file_data):
        # <hand number> D <dealer button position> P <action by all players in order from first to 
        # act, e.g. fccrf...> F <flop card 1> F <flop 2> F <flop 3> F <flop action starting with first player to act>
        # T <turn card> T <turn action> R <river card> R <river action>

        arr = re.split(r'[DPFFFFTTRR]',file_data)
        # dictionary = {"hand_num" : arr[0],
        #                 "button" : arr[1] ,
        #                 "preflop_action" : arr[2],
        #                 "flop_card_1" : arr[3] ,
        #                 "flop_card_2" : arr[4],
        #                 "flop_card_3" : arr[5] ,
        #                 "flop_action" : arr[6] ,
        #                 "turn_card" : arr[7],
        #                 "turn_action" : arr[8],
        #                 "river_card" : arr[9],
        #                 "river_action" : arr[10]}
       
        for i in range(len(arr)):
            print(i, arr[i], arr)
            # if arr[i] not in self.casino_to_bot_list_b1:
            if(arr[i] != self.casino_to_bot_list_b1[i]):
                print("true")
            
            #     #return block
            self.casino_to_bot_list_b1.append(arr[i])
            #     return block

        
class main_watch_manager():
    
    def __init__(self, player_list ,communication_files_directory='/usr/local/home/u180455/Desktop/Project/MLFYP_Project/MLFYP_Project/pokercasino/botfiles'):
        self.communication_files_directory = communication_files_directory
        self.player_list = player_list

        # watch manager
        wm = pyinotify.WatchManager()
        wm.add_watch(self.communication_files_directory, pyinotify.ALL_EVENTS, rec=True)

        # event handler
        kwargs = {"player_list": self.player_list}
        eh = MyEventHandler(**kwargs)

        # notifier
        notifier = pyinotify.Notifier(wm, eh)
        notifier.loop()


if __name__ == '__main__':

    game = Game()

    #os.remove("strategy_stats.txt")
    #print('==== Use simple regret-matching strategy === ')
    #game.play()
    #print('==== Use averaged regret-matching strategy === ')
    #game.conclude()
    #game.play(avg_regret_matching=True)



