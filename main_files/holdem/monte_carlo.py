import gym
import holdem
import numpy as np
from collections import defaultdict
from include import *
import matplotlib.pyplot as plt
from libs import plotting


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
	
	if _round is not "Preflop": # preflop already evaluated
		player_object.he.evaluate(_round)
	range_structure = fill_range_structure(_round, player_object)
	assign_evals_player(player_object, _round, env)

	if(current_player == 0): # learner move 
		which_action = player_object.choose_action(_round, range_structure, env) # Doesn't use
		player_actions = holdem.safe_actions(community_infos, which_action=None, n_seats=n_seats)
		
	else: # bot move 
		
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
		a = (env._current_player.currentbet)
		actions = get_action_policy(player_infos, player_hands, community_infos, community_cards, env, _round, n_seats)
		(player_states, (community_infos, community_cards)), action, rewards, terminal, info = env.step(actions)
		current_state = (player_states, (community_infos, community_cards))
		episode.append((current_state, action, env.learner_bot.reward))
		env.render(mode='human')

	return episode
	

def mc_prediction_poker(total_episodes):
   
    returns_sum = defaultdict(float)
    states_count = defaultdict(float)
    
    V = defaultdict(float)
    for k in range(1, total_episodes + 1):
        print("\n\n********{}*********".format(k))
        episode = generate_episode(env, env.n_seats)
        do_necessary_env_cleanup()
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

def do_necessary_env_cleanup():
    list_players = env._player_dict.copy()
    for player in list_players.values():
        if player.stack <= 0:
            env.remove_player(player.get_seat())
    env.assign_positions()

def simulate_episodes_with_graphs(no_of_episodes=100):
	episode_list = []
	stacks_over_time = {}
	for index, player in env._player_dict.items():
		stacks_over_time.update({player.get_seat(): [player.stack]})
	for i in range(no_of_episodes):
		print("\n\n********{}*********".format(i))
		episode = generate_episode(env, env.n_seats) 
		do_necessary_env_cleanup()
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



env = gym.make('TexasHoldem-v1') # holdem.TexasHoldemEnv(2)
env.add_player(0, stack=2000) # add a player to seat 0 with 2000 "chips"
# env.add_player(1, stack=2000) # tight
env.add_player(2, stack=2000) # aggressive



v = mc_prediction_poker(10)
# for line_no, line in enumerate(v.items()):
#     print(line_no, line)

plotting.plot_value_function(v, title="10 Steps")