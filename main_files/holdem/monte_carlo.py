import HandHoldem
import gym
import holdem
import numpy as np
from collections import defaultdict
from include import *


def populatePlayerPossibleMoves(bot_position):
	possible_moves = []
	# if(llf.count_r(last_seq_move) == 3):
	# 	possible_moves.clear()
	# 	possible_moves.add('c')
	# 	possible_moves.add('f')
		
	# else:
	# 	possible_moves.clear()
	# 	possible_moves.add('r')
	# 	possible_moves.add('c')
	# 	possible_moves.add('f')

	possible_moves.append('r')
	possible_moves.append('c')
	possible_moves.append('f')
	return possible_moves

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
		range_structure = flop_range
	elif _round == 'Turn' or _round == 'River':
		range_structure = turn_river

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
			player.evaluation_preflop["hand_strength"] = hand_strength
			player.evaluation_flop["he"] = player.he
			player.evaluation_flop["rc"] = rc
			player.evaluation_flop["score_desc"] = score_desc
			player.evaluation_flop["evaluation"] = evaluation
	elif event == 'Turn':
		if player.evaluation_turn["he"] == '':
			player.evaluation_preflop["hand_strength"] = hand_strength
			player.evaluation_turn["he"] = player.he
			player.evaluation_turn["rc"] = rc
			player.evaluation_turn["score_desc"] = score_desc
			player.evaluation_turn["evaluation"] = evaluation
	elif event == 'River':
		if player.evaluation_river["he"] == '':
			player.evaluation_preflop["hand_strength"] = hand_strength
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
	player_o.round['raises_i_owe'] = player_o.round['raises_i_owe'] + add_me
	


def assign_evals_player(player_o, _round, env):
	hand_strength, evaluation, rc, score_desc, hand, board = player_o.he.get_evaluation(_round)
	set_attributes(hand_strength, evaluation, player_o, rc, score_desc, _round)
	player_o.possible_moves = populatePlayerPossibleMoves(_round)
	raises_facing = calc_raises_i_face(player_o, env)
	

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
		which_action = player_object.which_action(_round, range_structure) 
		player_actions = holdem.safe_actions(community_infos, which_action, n_seats=n_seats)
	
	return player_actions



def generate_episode(env, n_seats):
	# state observation
	(player_states, (community_infos, community_cards)) = env.reset()
	(player_infos, player_hands) = zip(*player_states)
	

  # display the table, cards and all
	env.render(mode='human')
	
	terminal = False
	while not terminal:
		
		# play safe actions, check when noone else has raised, call when raised.
		#actions = holdem.safe_actions(community_infos, n_seats=n_seats)
		_round = which_round(community_cards)
		# if _round is not 'Preflop':
		# 	env._resolve_postflop()
		# 	current_player = env._current_player.position
		# else:
		# 	current_player = community_infos[-1]
		current_player = community_infos[-1]
		if env._player_dict[current_player].he == None:
			card1, card2 = player_hands[current_player]
			he = HandHoldem.HandEvaluation([card1, card2], current_player, _round) #Unique to player instance
			env._player_dict[current_player].he = he
		
		actions = get_action_policy(player_infos, player_hands, community_infos, community_cards, env, _round, n_seats)
		(player_states, (community_infos, community_cards)), rews, terminal, info = env.step(actions)
		env.render(mode='human')
	
	env.assign_positions(initial = False)
		


env = gym.make('TexasHoldem-v1') # holdem.TexasHoldemEnv(2)
env.add_player(0, stack=2000) # add a player to seat 0 with 2000 "chips"
env.add_player(1, stack=2000) # add another player to seat 1 with 2000 "chips"


full_rotation = len(env._player_dict)
print(full_rotation)
for i in range(full_rotation*100):
	generate_episode(env, env.n_seats)

