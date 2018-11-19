import numpy
import pandas
from collections import deque

mPlayers = [] # a queue of all the bots
table = [] # all players still in the hand
mDeck = [] # shuffled deck
mCurrentHand = '' # status of current hand
mWinners = [] # winners among players left in hand
mCounter = 0 # current hand number
mButton = 0 # current button
mPot = 0 # current pot

class Casino:

    def __init__(self):
        pass
         
    def shuffle_deck(self):  # randomly shuffles mDeck
        import itertools, random
        deck = list(itertools.product(range(1,14),['Spade','Heart','Diamond','Club']))
        random.shuffle(deck)
        print("You got:")
        for i in range(5):
            print(deck[i][0], "of", deck[i][1])

   
    def populateTable(self):  # creates vector of bots
        pass
    def dealCards(self): # tell bots their starting hands 
        pass
    def getPreflopBets(self): 
        pass
    def getFlopBets(self): 
        pass
    def getTurnBets(self): 
        pass
    def getRiverBets(self): 
        pass
    def getWinners(self):
        pass
    def payoffs(self): # pay winners
        pass
    def showdown(self): # add showdown to mCurrentHand
        pass
    def tellHandSummary(self): # tells hand summary to all in even or odd file.
        pass
    def fileHandSummary(self): # tells hand summary to all in even or odd file.
        pass
    def printHandSummary(self): # tells hand summary to all in even or odd file.
        pass
    def prepareNext(self): # initialise stuff for next hand
        pass
    def attend(self): # waiting a while for bots to make a decision
        pass

    #misc
    tableEmpty(): # check if only one player is left, ie can go to showdown