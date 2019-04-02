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

with_render = False

n_episodes = 100 # n games we want agent to play (default 1001)

villain = "Strong"

starting_stack_size = 2000

epsilon = 0.9

def get_action_policy(player_infos, community_infos, community_cards, env, _round, n_seats, state, policy):
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
		player_actions = holdem.safe_actions(to_call, community_infos, villain_choice=None, n_seats=n_seats, choice=choice, player_o = player_object, best_nonlearning_action=best_nonlearning_action)
		
	else: # bot move 
		if villain == "CallChump":
			player_actions = utilities.safe_actions_call_bot(community_infos, villain_choice=None, n_seats=n_seats)
		else:
			villain_choice = player_object.choose_action(_round, range_structure, env) 
			player_actions = holdem.safe_actions(to_call, community_infos, villain_choice, n_seats=n_seats, choice=None, player_o = player_object)
	
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

LARGE_FONT= ("Verdana", 12)


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


class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        self.state = [None, False]
        tk.Tk.__init__(self, *args, **kwargs)

        # tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Sea of BTC client")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PagePokerGameMC, StartGame):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        # PagePokerGameMC.simulation(PagePokerGameMC)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    def receive_info(self, state):
        self.state[0] = state
        self.state[1] = False

    def get_state(self):
        self.state[1] = True
        return self.state[0]


        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Main Menu", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="Analyze Agents",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Compete Against Agents",
                            command=lambda: controller.show_frame(PageOne))
        button2.pack()

        

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Choose Agent", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Monte-Carlo Agent",
                            command=lambda: controller.show_frame(PagePokerGameMC))
        button1.pack()

        button2 = ttk.Button(self, text="Deep Q-Learning Agent",
                            command=lambda: controller.show_frame(PagePokerGame))
        button2.pack()




class PagePokerGameMC(tk.Frame):

	def __init__(self, parent, controller):
		



		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="Poker Room", font=("Arial Bold", 30))
		label.pack(pady=10,padx=10)
		button1 = ttk.Button(self, text="Back to Home",
							command=lambda: controller.show_frame(StartPage))
		button1.pack()

		start_button = ttk.Button(self, text="start game",
							command=lambda: controller.show_frame(StartGame))
		start_button.pack() 

		


class StartGame(tk.Frame):


	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="Poker Room", font=("Arial Bold", 30))
		label.pack(pady=10,padx=10)
		button1 = ttk.Button(self, text="Back to Home",
							command=lambda: controller.show_frame(StartPage))
		button1.pack()

		self.separator = tk.LabelFrame(self, width=50, height=150, text="Board", bd=10)
		self.separator.pack(fill='x', padx=5, pady=5)

		
	

		self.returns_sum = defaultdict(float)
		self.returns_count = defaultdict(float)
		self.Q = defaultdict(lambda: np.zeros(env.action_space.n))
		self.policy = make_epsilon_greedy_policy(self.Q, env.action_space.n, epsilon)
		self.guest_cards = []
		self.learner_cards = []
		self.state = None
		self.player_states, self.community_infos, self.community_cards = None, None, None
		self.player_infos, self.player_hands = None, None
		self.current_state = None
		self.state_set = None
		self.p1 = env._player_dict[0]
		self.p2 = env._player_dict[2]
		self.episode_list = []
		self.total_pot_label = None
		self._round = None
		self.current_player = None
		self.guest_action = None
		self.call_button = None
		self.raise_button = None
		self.fold_button = None
		self.guest_buttons = [self.call_button, self.raise_button, self.fold_button]
		self.terminal = False
		self.guest_label = None
		self.learner_label = None
		self.p1_pos = None
		self.ps_pos = None
		self.guest_cards_st, self.learner_cards_st = None, None
		self.episodes = []
		self.last_bet_label = None
		self.community_display = []

		self.delegate_state_info(reset=True)

		self.set_info_before_loop()
		self.simulate(initial=True)

		


	def restart_game(self):
		utilities.do_necessary_env_cleanup(env)
		self.delegate_state_info(reset=True)
		self.set_info_before_loop()
		self.simulate()


	# def start_new_round(self):
	# 	self.delegate_state_info(reset=False)
	# 	while not(self.terminal):
	# 		self.simulate()

	def set_guest_action(self, action):
		# self.update_local_state(reset=False)
		# self.populate_info_pre_action()
		self.guest_action = action

		if (self.community_infos[-3] == 2):
			self.simulate()
		
			if self.community_infos[-3] == 0 and not env.is_new_r:
				self.simulate()

		

		# if env.is_new_r:
		# 	self.start_new_round()

	def simulate(self, initial = False):
		# for i_episode in range(1, n_episodes + 1):
		

		self.populate_info_pre_action()
		if self.current_player == 0:
			self.episodes.append(self.generate_episode_learner_move())
		elif self.current_player == 2:
			self.episodes.append(self.generate_episode_guest())
		
		if self.terminal:
			
			self.restart_game()
			

		else:
			
			self.update_local_state(reset=False)
			
		# utilities.do_necessary_env_cleanup(env)


	def update_local_state(self, reset=True):
		self.p1_pos = 'SB' if self.p1.position == 0 else 'BB'
		self.p2_pos = 'SB' if self.p2.position == 0 else 'BB'

		if reset:
			self.state = env.reset()
			
		else:
			self.state = env._get_current_state()
			self.set_info_before_loop()
			self.update_display()


	def update_display(self):
		
		self.update_pot_size()

		self.assign_player_objects_to_display(reset=True)
		
		self.assign_cards_to_display(self.guest_cards_st, self.learner_cards_st, reset=True)
		
		self.print_last_action()

		self.assign_guest_buttons()


	def print_last_action(self, spec=None):
		if self.last_bet_label is not None:
			self.last_bet_label.pack_forget()
		if spec:
			self.last_bet_label = tk.Label(self, text="Activity:\n{}".format(spec), font=("Arial Bold", 10))	
		else:
			self.last_bet_label = tk.Label(self, text="Activity:\n{}".format(env._last_actions[0]), font=("Arial Bold", 10))
		self.last_bet_label.pack(side='top', pady=20,padx=20)

		if env._last_actions is not None:
			if env._last_actions[0] == 'fold':
				self.print_last_action(spec='Player 1 Folded')
				time.sleep(2)

	def delegate_state_info(self, reset):
		
		self.update_local_state(reset=reset)
		
		player_label = [Card.int_to_str(self.p2.hand[0]).upper(), Card.int_to_str(self.p2.hand[1]).upper()]
		
		self.assign_player_objects_to_display()

		# LEFT OF SCREEN
		self.guest_cards_st = [Card.int_to_str(self.p2.hand[0]).upper(), Card.int_to_str(self.p2.hand[1]).upper()]
		# RIGHT OF SCREEN
		self.learner_cards_st = [Card.int_to_str(self.p1.hand[0]).upper(), Card.int_to_str(self.p1.hand[1]).upper()]

		self.assign_cards_to_display(self.guest_cards_st, self.learner_cards_st, reset=False)

		self.update_pot_size()

	def update_pot_size(self):
		if self.total_pot_label is not None:
			self.total_pot_label.pack_forget()
		self.total_pot_label = tk.Label(self, text="Pot:\n{}\n".format(env._totalpot), font=("Arial Bold", 20))
		self.total_pot_label.pack(side='top', pady=40,padx=40)

	def assign_guest_buttons(self):
		for button in self.guest_buttons:
			if button is not None:
				button.pack_forget()
		self.call_button = ttk.Button(self, text="Call",
						command=lambda: self.set_guest_action('c'))
		self.call_button.pack(side='bottom')
		self.raise_button = ttk.Button(self, text="Raise",
						command=lambda: self.set_guest_action('r'))
		self.raise_button.pack(side='bottom')
		self.fold_button = ttk.Button(self, text="Fold",
						command=lambda: self.set_guest_action('f'))
		self.fold_button.pack(side='bottom')
		self.guest_buttons = [self.call_button, self.raise_button, self.fold_button]

		

	def assign_cards_to_display(self, guest_cards_st, learner_cards_st, reset = False):
		if reset:
			for card in self.guest_cards+self.learner_cards:
				card.pack_forget()
		position_cards = [0, 0]
		
		for card in self.guest_cards_st:
			guest_card = self.form_image(card)
			guest_card.pack(side='left', expand = False, padx=position_cards[0], pady=position_cards[1])
			self.guest_cards.append(guest_card)

		for card in self.learner_cards_st:
			learner_card = self.form_image(card)
			learner_card.pack(side='right', expand = False, padx=position_cards[0], pady=position_cards[1])
			self.learner_cards.append(learner_card)
		cd = []
		if self.community_cards is not None:
			if not(all(i < 0 for i in self.community_cards)):
				if self.community_cards[0] is not -1 and self.community_cards[1] is not -1 and self.community_cards[2] is not -1:
					cd.append(Card.int_to_str(self.community_cards[0]).upper())
					cd.append(Card.int_to_str(self.community_cards[1]).upper())
					cd.append(Card.int_to_str(self.community_cards[2]).upper())
				if self.community_cards[3] is not -1:
					cd.append(Card.int_to_str(self.community_cards[3]).upper())
				if self.community_cards[4] is not -1:
					cd.append(Card.int_to_str(self.community_cards[4]).upper())

				if self.community_display is not None:
					for card in self.community_display:
						card.pack_forget()

				for card in cd:
					c = self.form_image(card, community=True)
					c.pack(side='left', expand = False, padx=20, pady=20)
					self.community_display.append(c)
					# testLabel = tk.Label(self.separator, text="This is a test label")
					# testLabel.pack(side='top')

	def assign_player_objects_to_display(self, reset=False):
		if reset and self.guest_label is not None and self.learner_label is not None:
			self.guest_label.pack_forget()
			self.learner_label.pack_forget()
		position_cards = [10, 10]
		self.guest_label = tk.Label(self, text="Player\n\nStack:{}\n{}".format(self.p2.stack, self.p2_pos), font=("Arial Bold", 12))
		self.guest_label.pack(side='left', pady=40,padx=40)
		self.learner_label = tk.Label(self, text="Learner\n\nStack:{}\n{}".format(self.p1.stack, self.p1_pos), font=("Arial Bold", 12))
		self.learner_label.pack(side='right', pady=40,padx=40)

		# if self.community_infos is not None:
		# 	cp = self.community_infos[-1]
		# 	if cp == 0:
		# 		self.learner_label.config(bg="red")
		# 		self.guest_label.config(bg="white")
		# 	elif cp == 2:
		# 		self.guest_label.config(bg="red")
		# 		self.learner_label.config(bg="white")
			

	def form_image(self, card, community=False):
		from PIL import Image, ImageTk
		card_image = Image.open("./JPEG/"+ card +".jpg")
		photo = ImageTk.PhotoImage(card_image)
		label = tk.Label(self, image=photo) if community is False else tk.Label(self.separator, image=photo)
		label.image = photo # keep a reference!
		return label

	def parse_action(self, action):
		if action == 'c':
			return [(1, 0), (0, 0)]
		elif action == 'r':
			total_bet = None
			if self._round == 'Preflop' and self.p2.position == 0:
			
				total_bet = 40
			else:
				total_bet = 25

			action = (2, total_bet)
			assert action[1] == 40 or action[1] == 25
			return action
		elif action == 'f':
			return [3, 0]

	def get_guest_action(self):
		action = self.guest_action
		action = self.parse_action(action)
		player_actions = holdem.safe_actions(self.community_infos[-1], self.community_infos, action, n_seats=env.n_seats, choice=None, player_o = self.p2)
		return player_actions
		

	# v = mc_prediction_poker(10)
	# # for line_no, line in enumerate(v.items()):
	# #     print(line_no, line)

	# plotting.plot_value_function(v, title="10 Steps")


	def set_info_before_loop(self, reset=True):
		# (player_states, (community_infos, community_cards)) = env.reset()

		(self.player_states, (self.community_infos, self.community_cards)) = self.state
		if not reset:
			pass
		(self.player_infos, self.player_hands) = zip(*self.player_states)
		self.current_state = ((self.player_infos, self.player_hands), (self.community_infos, self.community_cards))
		self.state_set = utilities.convert_list_to_tupleA(self.player_states[env.learner_bot.get_seat()], self.current_state[1])

	def populate_info_pre_action(self):
		self._round = utilities.which_round(self.community_cards)
		self.current_player = self.community_infos[-3]


	def get_action_for_page(self):
		if self.current_player == 0: # Learner (RHS Screen)
			self.action = get_action_policy(self.player_infos, self.community_infos, self.community_cards, env, self._round, env.n_seats, self.state_set, self.policy)

		elif self.current_player == 2: # Player on page (LHS Screen)
			self.action = self.get_guest_action()



	def generate_episode_guest(self):
		part_ep = []
		
		self.get_action_for_page()
		
		(self.player_states, (self.community_infos, community_cards)), self.action, rewards, self.terminal, info = env.step(self.action)

		parsed_return_state = utilities.convert_step_return_to_set((self.current_state, self.action, env.learner_bot.reward))
		self.action = utilities.convert_step_return_to_action(self.action)
		part_ep.append((parsed_return_state, self.action, env.learner_bot.reward))
		current_state = (self.player_states, (self.community_infos, self.community_cards)) # state = next_state
		
		return part_ep

	def generate_episode_learner_move(self):
		episode = []
		
		self.get_action_for_page()
		
		(self.player_states, (self.community_infos, community_cards)), self.action, rewards, self.terminal, info = env.step(self.action)

		parsed_return_state = utilities.convert_step_return_to_set((self.current_state, self.action, env.learner_bot.reward))
		self.action = utilities.convert_step_return_to_action(self.action)
		episode.append((parsed_return_state, self.action, env.learner_bot.reward))
		current_state = (self.player_states, (self.community_infos, self.community_cards)) # state = next_state
		
		return episode

			

	def mc_control_epsilon_greedy(self, num_episodes, discount_factor=1.0, epsilon=0.1, is_with_rendering=with_render, forgo_flag=0):


		# Keeps track of sum and count of returns for each state
		# to calculate an average. We could use an array to save all
		# returns (like in the book) but that's memory inefficient.
		
		
		self.set_info_before_actions()

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



if __name__ == '__main__':
        
    app = SeaofBTCapp()
    app.geometry("1280x720")
    app.mainloop()
    #Q, policy = mc_control_epsilon_greedy(num_episodes=n_episodes, epsilon= 0.9)
