from __future__ import division
from random import random
import numpy as np
import pandas as pd
import os
import uuid
from itertools import izip

'''
    Use regret-matching algorithm to play Scissors-Rock-Paper.
'''

class PokerRound(Game):

    def __init__(self, actionsPlayer1, actionsPlayer2):
        super().__init__(max_game)
        self.actionsPlayer1, self.actionsPlayer2 = np.zeros((2, 3))  # ASSUMING HEADS-UP
        self.name = name
        self.list_of_actions_player1 = []
        self.list_of_actions_player2 = []




class PokerStreet:

    # Must take in 2 cards from C++ Casino Program
    # Evaluate cards and make decision on action which corresponds to strategy
    # If bet, determine bet size which also corresponds to strategy\
    # In Holdem, as with other forms of poker, the available actions are fold, check, call, bet or raise
    # We have the following representations:
    #       raise and bet as BET,
    #       check and call as CALL.
    pass








class Player:
    def __init__(self, name, cards, position):
        self.strategy, self.avg_strategy,\
        self.strategy_sum, self.regret_sum = np.zeros((4, Poker.n_actions))
        self.name = name
        self.cards = cards
        self.position = position

    def __repr__(self):
        return self.name



class Game:
    def __init__(self, max_game=5):

        Player1 = Player(uuid1() ,'Adam', CardHolding('-','-','-','-'), 'BTN')
        Player2 = Player(uuid1() ,'Bill', CardHolding('-','-','-','-'), 'SB')
        Player3 = Player(uuid1() ,'Chris', CardHolding('-','-','-','-'), 'BB')
        Player4 = Player(uuid1() ,'Dennis', CardHolding('-','-','-','-'), 'CO')
        player_list = [Player1, Player2, Player3, Player4]
        position_list = {0: Player1.position, 1: Player2.position, 2: Player3.position, 3: Player4.position}
        # Create more players for Poker game
        self.table = Table(player_list, position_list)
        self.max_game = max_game


class Table(Game):

    num_of_players = 0

    def __init__(self, players, position_list):
        # self.players = np.copy(players)
        for i in range(len(players)):
            self.players[i] = players[i]
            num_of_players += 1
        self.position_list = dict.copy(position_list)

    def get_players_at_table():
        return self.players

    def get_player_at_position(position):
        for i in self.players:
            if i.position == position:
                return i

    def get_position_of_player(player):
        for i in self.players:
            if i == player:
                return i.position

    def set_position_of_player(player, position):
        for pl in self.players:
            if pl == player:
                pl.position = position

    def get_number_of_players():
        return num_of_players

    # def swap_player_positions(playerA, playerB):
    #     tmp = playerA.position
    #     playerA.position = playerB.position
    #     playerB.position = tmp

    #def rotate():
        # position_indexes = []
        # count = 0
        # for i in position_list:
        #     position_indexes.append(count)
        # self.position_list.insert(0, self.position_list.pop())
        # for player_index in range(len(self.players)):
        #     current_position = get_position_of_player(get_player_at_position(player_index))
        #     index_of_current_position = self.position_list.index(current_position)
        #     index_of_new_position = index_of_current_position + 1
        #     new_position = ''
        #     for pos in self.position_list:
        #         if pos == current_position:
        #             new_position = self.position_list[current_position+1]
        #     set_position_of_player(get_player_at_position(player_index), )

    def rotate_table(pos_dict):
        values = pos_dict.values()
        keys = pos_dict.keys()
        values.insert(0, values.pop())
        self.positions_list = dict(zip(list(keys)), values))


    def remove_player(player):
        for i in self.players:
            if i == player:
                #pos = get_position_of_player(player)
                list_of_players.remove(player)
        for pos in position_list:
            if pos == player.position:
                position_list.remove(pos)
        rearrange_positions_at_table()

    def switch_position_associations():
        # Assume only 4 positions for the moment
        for index in range(len(self.position_list)):
            if index == 0:
                self.




if __name__ == '__main__':
    os.remove("strategy_stats.txt")
    game = Game()

    print('==== Use simple regret-matching strategy === ')
    game.play()
    print('==== Use averaged regret-matching strategy === ')
    game.conclude()
    game.play(avg_regret_matching=True)
