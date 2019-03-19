import numpy as np
import random
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True)

ROCK, PAPER, SCISSORS = 0, 1, 2
NUM_ACTIONS = 3
regretSum = np.zeros(NUM_ACTIONS, dtype = np.float64)
strategySum = np.zeros(NUM_ACTIONS, dtype = np.float64)
oppStrategy = np.array([0.4, 0.3, 0.3])

def value(p1, p2):
    if p1==p2:
        return 0
    elif p1==ROCK and p2==SCISSORS:
        return 1
    elif p1==SCISSORS and p2==PAPER:
        return 1
    elif p1==PAPER and p2==ROCK:
        return 1
    else:
        return -1

def getStrategy():
    global regretSum, strategySum
    strategy = np.maximum(regretSum, 0)
    normalizingSum = np.sum(strategy)
    if normalizingSum > 0:
        strategy/= normalizingSum
    else:
        strategy= np.ones(NUM_ACTIONS)/NUM_ACTIONS

    strategySum += strategy
    return strategy

def getAverageStrategy():
    global strategySum
    normalizingSum = np.sum(strategySum)
    if normalizingSum > 0:
        avgStrategy = strategySum / normalizingSum
    else:
        avgStrategy = np.ones(NUM_ACTIONS)/NUM_ACTIONS

    return avgStrategy

def getAction(strategy):
    strategy = strategy/ np.sum(strategy)  ## Normalize
    rr = random.random()
    a = np.cumsum(strategy)
    x = np.searchsorted(a, rr)
    return x


def train(iterations):
    # <Get regret-matched mixed-strategy actions>
    # <Compute action utilities>
    # <Accumulate action regrets>

    global regretSum
    actionUtility = np.zeros(NUM_ACTIONS)
    for i in range(iterations):
        strategy = getStrategy()
        myAction = getAction(strategy)
        otherAction = getAction(oppStrategy)

        actionUtility[otherAction] = 0
        actionUtility[(otherAction + 1) % NUM_ACTIONS] = 1
        actionUtility[(otherAction - 1) % NUM_ACTIONS] = -1

        regretSum += actionUtility - actionUtility[myAction]


train(100000)
print(getAverageStrategy()) 


vvv = []
for i in range(100):
    vv = 0
    for j in range(100):
        strategy = getAverageStrategy()
        myAction = getAction(strategy)
        otherAction = getAction(oppStrategy)
        vv += value(myAction, otherAction)
    vvv.append(vv)
plt.title("CFR learned strategy (Learns to always choose paper).\nOur opponent uses fixed strategy (Rock-40%, Paper-30%, Scissors-30%)")
plt.plot(sorted(vvv))
plt.show()





