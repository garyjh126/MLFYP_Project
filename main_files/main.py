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
import low_level_functions as llf

most_recent_file_changed = ''


class Game:

    cards = []

    def __init__(self, max_game=5):
        global cards
        cards =  llf.create_cards_for_game(self)
        Player1 = p.Player(0 ,'Adam', p.CardHolding('-','-','-','-','-'), 'BTN', '/give_hand_bot0', cards, None)
        Player2 = p.Player(1 ,'Bill', p.CardHolding('-','-','-','-','-'), 'SB', '/give_hand_bot1', cards, None)
        #Player3 = Player(uuid.uuid1() ,'Chris', CardHolding('-','-','-','-','-'), 'BB', '/give_hand_bot2', cards, None)
        #Player4 = Player(uuid.uuid1() ,'Dennis', CardHolding('-','-','-','-','-'), 'CO', '/give_hand_bot3', cards, None)
        self.player_list = [Player1, Player2] #, Player3, Player4]
        positions_at_table = {0: Player1.position, 1: Player2.position} #, 2: Player3.position, 3: Player4.position} # mutable
        self.max_game = max_game
        self.parse_data_from_GHB()
        

    def parse_data_from_GHB(self):

        self.main_watch_manager = main_watch_manager(self.player_list)
        

def get_status_from_file(file_name):
    data = ''
    with open('/usr/local/home/u180455/Desktop/Project/MLFYP_Project/MLFYP_Project/pokercasino/botfiles/' + file_name, 'rt') as f:
        data = f.read()
    return data
    

class MyEventHandler(pyinotify.ProcessEvent):


    def my_init(self, **kargs):
        """
        This is your constructor it is automatically called from
        ProcessEvent.__init__(), And extra arguments passed to __init__() would
        be delegated automatically to my_init().
        """
        self.player_list = kargs["player_list"]

    def process_IN_CLOSE_WRITE(self, event):
        ### declaring a bot_number and event_type 
       # print(event.pathname)
        global file_changed
        arr = re.split(r'[/]',event.pathname)
        most_recent_file_changed = (arr[len(arr)-1])
        last_letter = most_recent_file_changed[len(most_recent_file_changed)-1]
        bot_number = last_letter if (last_letter =='0' or last_letter == '1') else ''
        event_type = most_recent_file_changed if bot_number == '' else most_recent_file_changed[0:len(most_recent_file_changed)-1]
        filename = str(event_type+bot_number)
        file_data = get_status_from_file(str(filename))

        if event_type == "give_hand_bot":
        
            if bot_number == '0':
                self.player_list[0].card_holding = llf.GHB_Parsing(self.player_list[0], file_data) #check cards
                #print(self.player_list[0].card_holding)

                #PROBLEM: Cannot evaluate preflop without players position which is retrieved in casinoToBot file overwrite
                #he, evaluation, rc, score_desc, _ = self.player_list[0].hand_evaluate_preflop(self.player_list[0].card_holding, self.player_list[0].name)

                # bot 0 now has his cards


            elif bot_number == '1':
                self.player_list[1].card_holding = llf.GHB_Parsing(self.player_list[1], file_data) #check cards
                #print(self.player_list[0].card_holding)

                #PROBLEM: Cannot evaluate preflop without players position which is retrieved in casinoToBot file overwrite
                #he, evaluation, rc, score_desc, _ = self.player_list[1].hand_evaluate_preflop(self.player_list[1].card_holding, self.player_list[1].name)

                #bot 1 now has his cards

        if event_type == "casinoToBot":   
            
            if bot_number == '0':
                self.player_list[0].game_state = (llf.casinoToBot_Parsing(self, file_data, self.player_list[0], self.player_list)) #check cards
                he, evaluation, rc, score_desc, _ = self.player_list[0].hand_evaluate_preflop(self.player_list[0].card_holding, self.player_list[0].name)
                #print(he, evaluation, rc, score_desc)
                #print(self.player_list[0].game_state)

            elif bot_number == '1':
                self.player_list[1].game_state = (llf.casinoToBot_Parsing(self, file_data, self.player_list[1], self.player_list)) #check cards
                he, evaluation, rc, score_desc, _ = self.player_list[1].hand_evaluate_preflop(self.player_list[1].card_holding, self.player_list[1].name)
                #print(he, evaluation, rc, score_desc)
                #print(self.player_list[1].game_state)


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





