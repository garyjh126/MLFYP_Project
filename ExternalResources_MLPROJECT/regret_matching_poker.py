from __future__ import division
from random import random
import numpy as np
import pandas as pd
import os


'''
    Use regret-matching algorithm to play Scissors-Rock-Paper.
'''

<<<<<<< HEAD
class PokerRound(Game):

    def __init__(self, actionsPlayer1, actionsPlayer2):
        super().__init__(max_game)
        self.actionsPlayer1, self.actionsPlayer2 = np.zeros((2, 3))  # ASSUMING HEADS-UP
        self.name = name
        self.list_of_actions_player1 = []
        self.list_of_actions_player2 = []


class PokerStreet:
=======
class Poker:
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3

    # Must take in 2 cards from C++ Casino Program
    # Evaluate cards and make decision on action which corresponds to strategy
    # If bet, determine bet size which also corresponds to strategy
<<<<<<< HEAD

    # In Hold'em, as with other forms of poker, the available actions are ‘fold’, ‘check’, ‘bet’, ‘call’ or ‘raise’.
    # We have the following representations:
    #       raise and bet as BET,
    #       check and call as CALL.





=======
	##
    actions = ['ROCK', 'PAPER', 'SCISSORS']
    n_actions = 3
    utilities = pd.DataFrame([
        # ROCK  PAPER  SCISSORS
        [ 0,    -1,    1], # ROCK
        [ 1,     0,   -1], # PAPER
        [-1,     1,    0]  # SCISSORS
    ], columns=actions, index=actions)
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3




class Player:
<<<<<<< HEAD
    def __init__(self, name, list_of_actions):
        self.strategy, self.avg_strategy,\
        self.strategy_sum, self.regret_sum = np.zeros((4, Poker.n_actions))
        self.name = name
        self.list_of_actions = []
=======
    def __init__(self, name):
        self.strategy, self.avg_strategy,\
        self.strategy_sum, self.regret_sum = np.zeros((4, Poker.n_actions))
        self.name = name
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3

    def __repr__(self):
        return self.name

    def update_strategy(self, i, which_player_forprint):
        """
        set the preference (strategy) of choosing an action to be proportional to positive regrets
        e.g, a strategy that prefers PAPER can be [0.2, 0.6, 0.2]
        """
        self.strategy = np.copy(self.regret_sum)
        self.strategy[self.strategy < 0] = 0  # reset negative regrets to zero

        # Q: Why set negative regrets to zero?
<<<<<<< HEAD
        # A: The strategy performance history is being tracked by strategy_sum.
        # 'Strategy' has it's negative regrets set to zero because it needs to
=======
        # A: The strategy performance history is being tracked by strategy_sum. 
        # 'Strategy' has it's negative regrets set to zero because it needs to 
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
        # evaluate new hand


        summation = sum(self.strategy)
<<<<<<< HEAD
        # Q: But then why is sum of 'Strategy' being calculated if it doesn't
        # consider negative regrets?
        # A: Probably because you can't normalise with a array that has negative numbers
        # Better Answer: It would make sense to think that a more negative value would
        # correspond to a bad action to take and so it would seem to be clever to not
        # play that option. For sake of simplictly, we only consider positive values
        # (Not diving by zero etc)

=======
        # Q: But then why is sum of 'Strategy' being calculated if it doesn't 
        # consider negative regrets?
        # A: Probably because you can't normalise with a array that has negative numbers
        # Better Answer: It would make sense to think that a more negative value would 
        # correspond to a bad action to take and so it would seem to be clever to not 
        # play that option. For sake of simplictly, we only consider positive values 
        # (Not diving by zero etc)
        
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3


        if summation > 0:
            # normalise
            self.strategy /= summation
        else:
            # uniform distribution to reduce exploitability
            self.strategy = np.repeat(1 / Poker.n_actions, Poker.n_actions)

        self.strategy_sum += self.strategy

        # Strategy is unique to player instance

        f = open('strategy_stats.txt','a+')
        if which_player_forprint == "p1":
            f.write("\nGAME_NUMBER: " + str(i) +"\n\t" + "\nPlayer_no: " + which_player_forprint + "\n\tself.self_strategy: " + str(self.strategy) +"\n\t" + "self.strategy_sum: " + str(self.strategy_sum) + "\n")
<<<<<<< HEAD
        else:
=======
        else: 
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
            f.write("\nPlayer_no: " + which_player_forprint + "\n\tself.self_strategy: " + str(self.strategy) +"\n\t" + "self.strategy_sum: " + str(self.strategy_sum) + "\n")
        f.close()


    def regret(self, my_action, opp_action, i, which_player_forprint):
        """
        we here define the regret of not having chosen an action as the difference between the utility of that action
        and the utility of the action we actually chose, with respect to the fixed choices of the other player.

        compute the regret and add it to regret sum.
        """
        result = Poker.utilities.loc[my_action, opp_action] # At this point, it can the winner is established
        facts = Poker.utilities.loc[:, opp_action].values
        regret = facts - result
        self.regret_sum += regret

<<<<<<< HEAD
        # Q: what is the difference between a regret_sum and strategy_sum?
=======
        # Q: what is the difference between a regret_sum and strategy_sum?      
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
        # A: regret_sum has affect on action(). straegy_sum is used for learn_avg_strategy

        f = open('strategy_stats.txt','a+')
        if which_player_forprint == "p2":
            f.write("\nPlayer_no: " + which_player_forprint + "\n\tself.regret_sum: " + str(self.regret_sum) +"\n\n***********************************************")
<<<<<<< HEAD
        else:
            f.write("\nPlayer_no: " + which_player_forprint + "\n\tself.regret_sum: " + str(self.regret_sum) +"\n")
        f.close()


=======
        else: 
            f.write("\nPlayer_no: " + which_player_forprint + "\n\tself.regret_sum: " + str(self.regret_sum) +"\n")
        f.close()

        
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3

    def action(self, i, which_player_forprint, use_avg=False):
        """
        select an action according to strategy probabilities
        """
<<<<<<< HEAD


        strategy = self.avg_strategy if use_avg else self.strategy
        act = np.random.choice(Poker.actions, p=strategy)


=======
        strategy = self.avg_strategy if use_avg else self.strategy
        act = np.random.choice(Poker.actions, p=strategy)
        
        
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
        f = open('strategy_stats.txt','a+')
        f.write("\nPlayer_no: " + which_player_forprint + "\n\tAction: " + str(act) +"\n")
        f.close()

        return act

    def learn_avg_strategy(self):
        # averaged strategy converges to Nash Equilibrium
<<<<<<< HEAD
        summation = sum(self.strategy_sum)
=======
        summation = sum(self.strategy_sum) 
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
        if summation > 0:
            self.avg_strategy = self.strategy_sum / summation
        else:
            self.avg_strategy = np.repeat(1/Poker.n_actions, Poker.n_actions)
<<<<<<< HEAD


=======
        
        
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
        f = open('strategy_stats.txt','a+')
        f.write("\nself.strategy_sum: " + str(self.strategy_sum) + "\n")
        f.close()

<<<<<<< HEAD

=======
        
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3


class Game:
    def __init__(self, max_game=5):

<<<<<<< HEAD

        # Create more players for Poker game
        self.p1 = Player('Player 1', actions_player1)
        self.p2 = Player('Player 2', actions_player2)


        self.max_game = max_game

    def winner(self, a1, a2):

        ## Winner cannot be declared directly from the utility matrix

=======
        # Create more players for Poker game
        self.p1 = Player('Gary')
        self.p2 = Player('John')
        self.max_game = max_game

    def winner(self, a1, a2):
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
        result = Poker.utilities.loc[a1, a2]
        if result == 1:     return self.p1
        elif result == -1:  return self.p2
        else:               return 'Draw'

    def play(self, avg_regret_matching=False):
        def play_regret_matching():
            for i in range(0, self.max_game):
                self.p1.update_strategy(i, "p1")
                self.p2.update_strategy(i, "p2")
                a1 = self.p1.action(i, "p1")
                a2 = self.p2.action(i, "p2")
                self.p1.regret(a1, a2, i, "p1")
                self.p2.regret(a2, a1, i, "p2")


                winner = self.winner(a1, a2)
                num_wins[winner] += 1

        def play_avg_regret_matching():
            for i in range(0, self.max_game):
                a1 = self.p1.action(i, "p1", use_avg=True)
                a2 = self.p2.action(i, "p2", use_avg=True)
                winner = self.winner(a1, a2)
                num_wins[winner] += 1

        num_wins = {
            self.p1: 0,
            self.p2: 0,
            'Draw': 0
        }

        play_regret_matching() if not avg_regret_matching else play_avg_regret_matching()
        print(num_wins)

    def conclude(self):
        """
<<<<<<< HEAD
        let two players conclude the average strategy from the previous strategy stats
=======
        let two players conclude the average strategy from the previous strategy stats 
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
        """
        self.p1.learn_avg_strategy()
        self.p2.learn_avg_strategy()


if __name__ == '__main__':
    os.remove("strategy_stats.txt")
    game = Game()

<<<<<<< HEAD
    print('==== Use simple regret-matching strategy === ')
    game.play()
    print('==== Use averaged regret-matching strategy === ')
    game.conclude()
    game.play(avg_regret_matching=True)
=======
    print('==== Use simple regret-matching strategy === ') 
    game.play()
    print('==== Use averaged regret-matching strategy === ')
    game.conclude()
    game.play(avg_regret_matching=True)
>>>>>>> 4040822570874223831b0dd940ce57bef523e1d3
