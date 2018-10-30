from __future__ import division
from random import random
import numpy as np
import pandas as pd
import os
import uuid


'''
    Use regret-matching algorithm to play Poker
'''


class Game:
    def __init__(self, max_game=5):

        Player1 = Player(uuid.uuid1() ,'Adam', CardHolding('-','-','-','-'), 'BTN')
        Player2 = Player(uuid.uuid1() ,'Bill', CardHolding('-','-','-','-'), 'SB')
        Player3 = Player(uuid.uuid1() ,'Chris', CardHolding('-','-','-','-'), 'BB')
        Player4 = Player(uuid.uuid1() ,'Dennis', CardHolding('-','-','-','-'), 'CO')
        player_list = [Player1, Player2, Player3, Player4]
        positions_at_table = {0: Player1.position, 1: Player2.position, 2: Player3.position, 3: Player4.position} # mutable
        
        # Create more players for Poker game
        self.table = Table(player_list, positions_at_table)
        self.max_game = max_game


class Table(Game):


    num_of_players = 0
    def __init__(self, player_list, positions_at_table):
        for i in range(len(player_list)):
            self.player_list[i] = player_list[i]
            #self.position_list.append(player_list[i].position)
            num_of_players += 1
        self.positions_at_table = positions_at_table.copy()

    def get_players_at_table():
        return self.player_list

    def get_player_at_position(position):
        for i in self.player_list:
            if i.position == position:
                return i
    
    def get_player_by_ID(ID):
        for player in player_list:
            if player.ID == ID: 
                return player

    def get_position_of_player(player):
        for i in self.player_list:
            if i == player:
                return i.position

    def get_number_of_players():
        return num_of_players

    def rotate():
        keys = self.positions_at_table.keys()
        values = self.positions_at_table.values()
        shifted_values = values.insert(0, values.pop())
        new_positions_at_table = dict(zip(keys, shifted_values))
        self.positions_at_table = new_positions_at_table

    def remove_player(player):
        for i in self.player_list:
            if i == player:
                list_of_players.remove(player)
        for index, pos in positions_at_table.items():
            if pos == player.position:
                del positions_at_table[pos]
                reinstantiate_positions_at_table(pos)

    def reinstantiate_positions_at_table(player_to_remove):
        keys = []
        for index in range(len(self.positions_at_table)):
            keys.append(index)
        values = self.positions_at_table.values()
        new_dict = dict(zip(keys, values))
        self.positions_at_table = new_dict


class Player(Game):
    def __init__(self, ID, name, card_holding, position):
        self.ID = ID
        self.name = name
        self.card_holding = card_holding
        self.position = position
        self.strategy, self.avg_strategy,\
        self.strategy_sum, self.regret_sum = np.zeros((4, 3))
        self.list_of_actions_game = np.array([])

    def __str__(self):
        return self.name

    def send_actions_to_game


    

class PokerRound(Table):

    def __init__(self, actionsPlayer1, actionsPlayer2):
        self.actionsPlayer1, self.actionsPlayer2 = np.zeros((2, 3)) 
        self.name = name
        self.list_of_actions_player1 = []
        self.list_of_actions_player2 = []







if __name__ == '__main__':
    os.remove("strategy_stats.txt")
    game = Game()
    print('==== Use simple regret-matching strategy === ')
    game.play()
    print('==== Use averaged regret-matching strategy === ')
    game.conclude()
    game.play(avg_regret_matching=True)
