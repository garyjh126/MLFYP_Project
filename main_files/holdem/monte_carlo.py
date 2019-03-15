import HandHoldem
import gym
import holdem
import numpy as np
from collections import defaultdict
from include import *
import matplotlib.pyplot as plt




def which_round(community_cards):
	count_cards = 0
	_round = ''
	for i in community_cards:
		if not i == -1:
			count_cards = count_cards + 1
	if count_cards == 0:
		_round = 'Preflop'
	elif count_cards == 3:
		_round = 'Flop'
	elif count_cards == 4:
		_round = 'Turn'
	elif count_cards == 5:
		_round = 'River'
	return _round 

def fill_range_structure(_round, player):
	range_structure = None
	if _round == 'Preflop': 
		range_structure = preflop_range
	elif _round == 'Flop':
		range_structure = hand_strength_flop
	elif _round == 'Turn':
		range_structure = hand_strength_turn
	elif _round == 'River':
		range_structure = hand_strength_river
	return range_structure

def set_attributes(hand_strength, evaluation, player, rc, score_desc, event):
	if event == 'Preflop':
		if player.evaluation_preflop["he"] == '':
			player.evaluation_preflop["hand_strength"] = hand_strength
			player.evaluation_preflop["he"] = player.he
			player.evaluation_preflop["rc"] = rc
			player.evaluation_preflop["score_desc"] = score_desc
			player.evaluation_preflop["evaluation"] = evaluation
	elif event == 'Flop':
		if player.evaluation_flop["he"] == '':
			player.evaluation_flop["hand_strength"] = hand_strength
			player.evaluation_flop["he"] = player.he
			player.evaluation_flop["rc"] = rc
			player.evaluation_flop["score_desc"] = score_desc
			player.evaluation_flop["evaluation"] = evaluation
	elif event == 'Turn':
		if player.evaluation_turn["he"] == '':
			player.evaluation_turn["hand_strength"] = hand_strength
			player.evaluation_turn["he"] = player.he
			player.evaluation_turn["rc"] = rc
			player.evaluation_turn["score_desc"] = score_desc
			player.evaluation_turn["evaluation"] = evaluation
	elif event == 'River':
		if player.evaluation_river["he"] == '':
			player.evaluation_river["hand_strength"] = hand_strength
			player.evaluation_river["he"] = player.he
			player.evaluation_river["rc"] = rc
			player.evaluation_river["score_desc"] = score_desc
			player.evaluation_river["evaluation"] = evaluation

def highest_in_LR(player_o, env):
    highest_lr_bot = 0
    highest_lr_value = 0
    
    for key, value in env.level_raises.items():
        if value > highest_lr_value:
            highest_lr_value = value
            highest_lr_bot = key
    return highest_lr_value, highest_lr_bot

def calc_raises_i_face(player_o, env):
	bot_position_num = player_o.get_seat()
	my_lr_value = env.level_raises[bot_position_num]
	highest_lr_value, highest_lr_bot = highest_in_LR(player_o, env)
	add_me = highest_lr_value - my_lr_value
	return player_o.round['raises_i_owe'] + add_me
	


def assign_evals_player(player_o, _round, env):
	hand_strength, evaluation, rc, score_desc, hand, board = player_o.he.get_evaluation(_round)
	set_attributes(hand_strength, evaluation, player_o, rc, score_desc, _round)
	player_o.populatePlayerPossibleMoves(env)
	player_o.round['raises_i_owe'] = calc_raises_i_face(player_o, env)
	

def get_action_policy(player_infos, player_hands, community_infos, community_cards, env, _round, n_seats):
	player_actions = None
	current_player = community_infos[-1]
	player_object = env._player_dict[current_player]
	to_call = community_infos[-2]
	empty, seat, stack, is_playing_hand, hand_rank, played_this_round, betting, allin, lastsidepot = player_infos[current_player]
	card1, card2 = player_hands[current_player]
	player_object.he.set_community_cards(community_cards, _round)
	
	if(current_player == 0): # learner move 
		player_actions = holdem.safe_actions(community_infos, which_action=None, n_seats=n_seats)
	else: # bot move 
		player_object.he.evaluate(_round)
		range_structure = fill_range_structure(_round, player_object)
		assign_evals_player(player_object, _round, env)
		which_action = player_object.choose_action(_round, range_structure, env) 
		player_actions = holdem.safe_actions(community_infos, which_action, n_seats=n_seats)
	
	return player_actions



def generate_episode(env, n_seats):
	# state observation
	episode = []
	(player_states, (community_infos, community_cards)) = env.reset()
	(player_infos, player_hands) = zip(*player_states)
	current_state = ((player_infos, player_hands), (community_infos, community_cards))

	env.render(mode='human', initial=True)
	terminal = False
	while not terminal:

		_round = which_round(community_cards)
		current_player = community_infos[-1]
		if env._player_dict[current_player].he == None:
			card1, card2 = player_hands[current_player]
			he = HandHoldem.HandEvaluation([card1, card2], current_player, _round) #Unique to player instance
			env._player_dict[current_player].he = he
			
		a = (env._current_player.currentbet)
		actions = get_action_policy(player_infos, player_hands, community_infos, community_cards, env, _round, n_seats)
		(player_states, (community_infos, community_cards)), rews, terminal, info = env.step(actions)
		episode.append((current_state, actions, rews))

		env.render(mode='human')


		# BUG: When one person folds, game assings current player as _next() but somehow ends up
		# assigning it as it itself over and over again. Need to address how to terminate this loop:
		# Also, if every player is still playing the game but does not have enough in stack, need to 
		# play to showdown. (Use _resolve function to deal next rounds)
		# Problem with freezing may also be due to lack of awareness by players still in game that
		# others have folded/broke. Incoroprate this somehow.

			

	env.assign_positions()
	return episode
	


env = gym.make('TexasHoldem-v1') # holdem.TexasHoldemEnv(2)
env.add_player(0, stack=200) # add a player to seat 0 with 2000 "chips"
# env.add_player(1, stack=200) # tight
env.add_player(2, stack=200) # aggressive

amount_of_rotations = 5
full_rotation = len(env._player_dict)
no_of_rotations = full_rotation*amount_of_rotations
episode_list = []
stacks_over_time = {0: [env._player_dict[0].stack], 1: [0], 2: [env._player_dict[2].stack] } # Player: stack
print(stacks_over_time[0])

for i in range(no_of_rotations):
	print("\n\n********{}*********".format(i))
	episode = generate_episode(env, env.n_seats) 
	list_players = env._player_dict.copy()
	for player in list_players.values():
		if player.stack <= 0:
			env.remove_player(player.get_seat())
	stack_list = env.report_game(requested_attributes = ["stack"])
	
	for s in range(len(stacks_over_time)):
		arr = stacks_over_time[s] + [stack_list[s]]
		stacks_over_time.update({s: arr})
	episode_list.append(episode)


plt.plot(stacks_over_time[0])
plt.ylabel('Stack Size')
plt.xlabel('Episode')
plt.show()

def mc_prediction_poker(total_episodes):
   
    returns_sum = defaultdict(float)
    states_count = defaultdict(float)
    
    V = defaultdict(float)
    
    for k in range(1, total_episodes + 1):
        
        episode = generate_episode(env, env.n_seats) 

        states_in_episode = list(set([sar[0] for sar in episode])) # sar--> state,action,reward
        
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


# v = mc_prediction_poker(100)