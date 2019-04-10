import gym
import holdem
import numpy as np
from collections import defaultdict
from include import *
import matplotlib.pyplot as plt
from libs import plotting
import sys
import utilities
if "../" not in sys.path:
  sys.path.append("../") 
import tkinter as tk
from tkinter import ttk
from treys import Card
import time
from PIL import Image, ImageTk
import os
from playsound import playsound

with_render = False

n_episodes = 100 # n games we want agent to play (default 1001)

villain = "Strong"

starting_stack_size = 2000

epsilon = 0.9

def get_action_policy(player_infos, community_infos, community_cards, env, _round, n_seats, state, policy, part_init=None):
	
	player_actions = None
	current_player = community_infos[-3]
	player_object = env._player_dict[current_player]
	to_call = community_infos[-1]
	stack, hand_rank, played_this_round, betting, lastsidepot = player_infos[current_player-1] if current_player is 2 else player_infos[current_player]
	player_object.he.set_community_cards(community_cards, _round)
	
	if _round is not "Preflop": # preflop already evaluated
		player_object.he.evaluate(_round)
	range_structure = utilities.fill_range_structure(_round, player_object)
	utilities.assign_evals_player(player_object, _round, env)

	if(current_player == 0): # learner move 
		probs = policy(state)
		choice = np.random.choice(np.arange(len(probs)), p=probs)
		best_nonlearning_action = player_object.choose_action(_round, range_structure, env) # Doesn't use
		player_actions = holdem.safe_actions(to_call, community_infos, villain_choice=None, n_seats=n_seats, choice=choice, player_o = player_object, best_nonlearning_action=best_nonlearning_action, part_init=part_init)
		
	else: # bot move 
		if villain == "CallChump":
			player_actions = utilities.safe_actions_call_bot(community_infos, villain_choice=None, n_seats=n_seats)
		else:
			villain_choice = player_object.choose_action(_round, range_structure, env) 
			player_actions = holdem.safe_actions(to_call, community_infos, villain_choice, n_seats=n_seats, choice=None, player_o = player_object, part_init=part_init)
	
	this_lr = (sum(p == player_object.get_seat() for p,v in env.level_raises.items()))
	if env.highest_in_LR()[1] is not player_object.get_seat() and env.highest_in_LR()[0] > this_lr:
		prohibit_action(player_actions, current_player, ban = [0, 0])
		# a,b = env.highest_in_LR()
		# print(player_actions)
		# which_action = player_object.choose_action(_round, range_structure, env) 
		# player_actions = holdem.safe_actions(community_infos, which_action, n_seats=n_seats, choice=None)
	return player_actions

def prohibit_action(li_actions, current_player, ban):
	if(li_actions[current_player] == ban):
		if env.learner_bot.action_type == "bet" or env.learner_bot.action_type == "raise":
			# print("ERROR")
			pass

def simulate_episodes_with_graphs(no_of_episodes=100):
	episode_list = []
	stacks_over_time = {}
	for index, player in env._player_dict.items():
		stacks_over_time.update({player.get_seat(): [player.stack]})
	for i in range(no_of_episodes):
		print("\n\n********{}*********".format(i))
		episode = generate_episode(env, env.n_seats) 
		utilities.do_necessary_env_cleanup(env)
		stack_list = env.report_game(requested_attributes = ["stack"])
		count_existing_players = 0

		for stack_record_index, stack_record in env._player_dict.items():
			arr = stacks_over_time[stack_record_index] + [stack_list[stack_record_index]]
			stacks_over_time.update({stack_record_index: arr})
			if(stack_list[stack_record_index] != 0):
				count_existing_players += 1
		episode_list.append(episode)

		if(count_existing_players == 1):
			break
		

	for player_idx, stack in stacks_over_time.items():
		if player_idx == 0:
			plt.plot(stack, label = "Player {} - Learner".format(player_idx))
		else:	
			plt.plot(stack, label = "Player {}".format(player_idx))

	plt.ylabel('Stack Size')
	plt.xlabel('Episode')
	plt.legend()
	plt.show()



def mc_prediction_poker(total_episodes):
   
    returns_sum = defaultdict(float)
    states_count = defaultdict(float)
    
    V = defaultdict(float)
    for k in range(1, total_episodes + 1):
        print("\n\n********{}*********".format(k))
        episode = generate_episode(env, env.n_seats)
        utilities.do_necessary_env_cleanup(env)
        possible_actions = np.array(np.identity(env.action_space.n,dtype=int).tolist()) # Here we create an hot encoded version of our actions

        # (PSEUDOCODE)
        # MODEL HYPERPARAMETERS: 
        # state_size = [(position, learner.stack, learner.handrank, played_this_round ...[card1, card2]), (pot_total, learner.to_call, opponent.stack, community_cards)]
        # action_size = env.action_space.n
        # learning_rate = 0.00025

        
		
        player_features_tuples = []
        player_cards_tuples = []
        community_state_tuples = []
        for idx, sar in enumerate(episode):
            pf = sar[0][0][0][0]
            player_features = tuple(pf)
            player_features_tuples.append(player_features)

            pf = sar[0][0][0][1]
            player_cards = tuple(pf)
            player_cards_tuples.append(player_cards)

            pf = sar[0][1][0]
            community_state = tuple(pf)
            community_state_tuples.append(community_state)

        # states_in_episode = list(set([sar[0] for sar in episode])) # sar--> state,action,reward
        states = []
        for i in range(len(player_features_tuples)):
            my_tup = (player_features_tuples[i] + player_cards_tuples[i] + community_state_tuples[i])
            states.append(my_tup)

        states_in_episode = set([state for state in states])

        for i,state in enumerate(states_in_episode):
            
            G = sum([sar[2] for i,sar in enumerate(episode[i:])])
            
            # for stationary problems 
            returns_sum[state] += G
            states_count[state] += 1.0         
            V[state] = returns_sum[state] / states_count[state]
            # end updating V
            
            #                    OR
            # V[state] = V[state]+ 1/states_count[state]*(G-V[state])
            
            # for non stationary problems 
            #alpha=0.5
            #V[state] = V[state]+ alpha*(G-V[state])
            

    return V

env = gym.make('TexasHoldem-v1') # holdem.TexasHoldemEnv(2)
env.add_player(0, stack=starting_stack_size) # add a player to seat 0 with 2000 "chips"
# env.add_player(1, stack=2000) # tight
env.add_player(2, stack=starting_stack_size) # aggressive

LARGE_FONT= ("Verdana", 17)


def make_epsilon_greedy_policy(Q, nA, epsilon=epsilon):
	"""
	Creates an epsilon-greedy policy based on a given Q-function and epsilon.
	
	Args:
		Q: A dictionary that maps from state -> action-values.
			Each value is a numpy array of length nA (see below)
		epsilon: The probability to select a random action . float between 0 and 1.
		nA: Number of actions in the environment.
	
	Returns:
		A function that takes the observation as an argument and returns
		the probabilities for each action in the form of a numpy array of length nA.
	
	"""
	def policy_fn(observation): # [call/check, raise/bet, fold]
		A = np.ones(nA, dtype=float) * epsilon / nA
		b = Q[observation]
		best_action = np.argmax(b)
		A[best_action] += (1.0 - epsilon)
		return A
	return policy_fn




			

	def mc_control_epsilon_greedy(self, discount_factor=1.0, epsilon=0.1):


		# Keeps track of sum and count of returns for each state
		# to calculate an average. We could use an array to save all
		# returns (like in the book) but that's memory inefficient.
		
		
		

		episode = self.generate_episode()
		utilities.do_necessary_env_cleanup(env) # assign new positions, remove players if stack < 0 etc ..

		# Find all (state, action) pairs we've visited in this episode
		# We convert each state to a tuple so that we can use it as a dict key
		sa_in_episode = set([(tuple(sar[0]), sar[1]) for sar in episode])
		for state, action in sa_in_episode:
			state = state[0]
			sa_pair = (state, action)
			# Find the first occurance of the (state, action) pair in the episode
			first_occurence_idx = next(i for i,x in enumerate(episode)
									if x[0][0] == state and x[1] == action)
			# Sum up all rewards since the first occurance
			G = sum([x[2]*(discount_factor**i) for i,x in enumerate(episode[first_occurence_idx:])])
			# Calculate average return for this state over all sampled episodes
			self.returns_sum[sa_pair] += G
			self.returns_count[sa_pair] += 1.0
			self.Q[state][action] = self.returns_sum[sa_pair] / self.returns_count[sa_pair]
			
			# The policy is improved implicitly by changing the Q dictionary


    #Q, policy = mc_control_epsilon_greedy(num_episodes=n_episodes, epsilon= 0.9)
