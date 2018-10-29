from __future__ import division
from random import random
import numpy as np
import pandas as pd
import os
import uuid


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

        # Create more players for Poker game
        self.table = Table(player_list)
        self.max_game = max_game

    # def winner(self, a1, a2):
    #
    #     ## Winner cannot be declared directly from the utility matrix
    #
    #     result = Poker.utilities.loc[a1, a2]
    #     if result == 1:     return self.p1
    #     elif result == -1:  return self.p2
    #     else:               return 'Draw'
    #
    # def play(self, avg_regret_matching=False):
    #     def play_regret_matching():
    #         for i in range(0, self.max_game):
    #             self.p1.update_strategy(i, "p1")
    #             self.p2.update_strategy(i, "p2")
    #             a1 = self.p1.action(i, "p1")
    #             a2 = self.p2.action(i, "p2")
    #             self.p1.regret(a1, a2, i, "p1")
    #             self.p2.regret(a2, a1, i, "p2")
    #
    #
    #             winner = self.winner(a1, a2)
    #             num_wins[winner] += 1
    #
    #     def play_avg_regret_matching():
    #         for i in range(0, self.max_game):
    #             a1 = self.p1.action(i, "p1", use_avg=True)
    #             a2 = self.p2.action(i, "p2", use_avg=True)
    #             winner = self.winner(a1, a2)
    #             num_wins[winner] += 1
    #
    #     num_wins = {
    #         self.p1: 0,
    #         self.p2: 0,
    #         'Draw': 0
    #     }
    #
    #     play_regret_matching() if not avg_regret_matching else play_avg_regret_matching()
    #     print(num_wins)
    #
    # def conclude(self):
    #     """
    #     let two players conclude the average strategy from the previous strategy stats
    #     """
    #     self.p1.learn_avg_strategy()
    #     self.p2.learn_avg_strategy()


class Table(Game):


    num_of_players = 0
    def __init__(self, players):
        for i in range(len(players)):
            self.players[i] = players[i]
            self.position_list.append(players[i].position)
            num_of_players += 1

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

    def get_number_of_players():
        return num_of_players

    # def swap_player_positions(playerA, playerB):
    #     tmp = playerA.position
    #     playerA.position = playerB.position
    #     playerB.position = tmp

    def rotate():
        self.position_list.insert(0, self.position_list.pop())
        for player in range(len(self.players)):



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
