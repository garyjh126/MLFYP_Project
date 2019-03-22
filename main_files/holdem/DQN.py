import gym
import holdem
import numpy as np
from collections import defaultdict, deque
from include import *
import matplotlib.pyplot as plt
from libs import plotting
import sys
import utilities
import random
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import os # for creating directories


env = gym.make('TexasHoldem-v1') # holdem.TexasHoldemEnv(2)
env.add_player(0, stack=2000) # add a player to seat 0 with 2000 "chips"
# env.add_player(1, stack=2000) # tight
env.add_player(2, stack=2000) # aggressive#


state_size = 29
action_size = env.action_space.n

batch_size = 32

n_episodes = 1001 # n games we want agent to play (default 1001)

output_dir = 'model_output/TexasHoldemDirectory/'

with_render = False

if not os.path.exists(output_dir):
    os.makedirs(output_dir)


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000) # double-ended queue; acts like list, but elements can be added/removed from either end
        self.gamma = 0.95 # decay or discount rate: enables agent to take into account future actions in addition to the immediate ones, but discounted at this rate
        self.epsilon = 1.0 # exploration rate: how much to act randomly; more initially than later due to epsilon decay
        self.epsilon_decay = 0.995 # decrease number of random explorations as the agent's performance (hopefully) improves over time
        self.epsilon_min = 0.01 # minimum amount of random exploration permitted
        self.learning_rate = 0.001 # rate at which NN adjusts models parameters via SGD to reduce cost 
        self.model = self._build_model() # private method 
    
    def _build_model(self):
        # neural net to approximate Q-value function:
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu')) # 1st hidden layer; states as input
        model.add(Dense(24, activation='relu')) # 2nd hidden layer
        model.add(Dense(self.action_size, activation='linear')) # 2 actions, so 2 output neurons: 0 and 1 (L/R)
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # list of previous experiences, enabling re-training later

    def act(self, state, player_infos, community_infos, community_cards, env, _round, n_seats, state_set, policy):
        if np.random.rand() <= self.epsilon: # if acting randomly, take random action
            action = get_action_policy(player_infos, community_infos, community_cards, env, _round, n_seats, state_set, policy)
            return action
        act_values = self.model.predict(state) # if not acting according to safe_strategy, predict reward value based on current state
        return np.argmax(act_values[0]) # pick the action that will give the highest reward (i.e., go left or right?)

    def replay(self, batch_size): # method that trains NN with experiences sampled from memory
        minibatch = random.sample(self.memory, batch_size) # sample a minibatch from memory
        for state, action, reward, next_state, done in minibatch: # extract data for each minibatch sample
            target = reward # if done (boolean whether game ended or not, i.e., whether final state or not), then target = reward
            if not done: # if not done, then predict future discounted reward
                target = (reward + self.gamma * # (target) = reward + (discount rate gamma) * 
                          np.amax(self.model.predict(next_state)[0])) # (maximum target Q based on future action a')
            target_f = self.model.predict(state) # approximately map current state to future discounted reward
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0) # single epoch of training with x=state, y=target_f; fit decreases loss btwn target_f and y_hat
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)



agent = DQNAgent(state_size, action_size) # initialise agent

def create_np_array(player_infos, player_hands, community_cards, community_infos):
    ps1 = (player_infos[0])
    for card in player_hands[0]:
        ps1 = np.append(ps1, card)    
    for info in community_infos:
        ps1 = np.append(ps1, info)    
    for card in community_cards:
        ps1 = np.append(ps1, card)    
    ps1 = np.reshape(ps1, [1, 18])
    return ps1


def make_epsilon_greedy_policy(Q, epsilon, nA):
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


# ***********************************Interacting with environment ********************************



def get_action_policy(player_infos, community_infos, community_cards, env, _round, n_seats, state, policy):
	player_actions = None
	current_player = community_infos[-1]
	player_object = env._player_dict[current_player]
	to_call = community_infos[-2]
	stack, hand_rank, played_this_round, betting, lastsidepot = player_infos[current_player]
	player_object.he.set_community_cards(community_cards, _round)
	
	if _round is not "Preflop": # preflop already evaluated
		player_object.he.evaluate(_round)
	range_structure = utilities.fill_range_structure(_round, player_object)
	utilities.assign_evals_player(player_object, _round, env)

	if(current_player == 0): # learner move 
		probs = policy(state)
		choice = np.random.choice(np.arange(len(probs)), p=probs)
		best_nonlearning_action = player_object.choose_action(_round, range_structure, env) # Doesn't use
		if choice is 1:
			total_bet = env._tocall + env._bigblind - env.opponent.currentbet
			choice = (2, total_bet)
		player_actions = holdem.safe_actions(community_infos, which_action=None, n_seats=n_seats, choice=choice)
		
	else: # bot move 
		
		which_action = player_object.choose_action(_round, range_structure, env) 
		player_actions = holdem.safe_actions(community_infos, which_action, n_seats=n_seats, choice=None)
	
	return player_actions



Q = defaultdict(lambda: np.zeros(env.action_space.n))
    
# The policy we're following
policy = make_epsilon_greedy_policy(Q, agent.epsilon, env.action_space.n)

for e in range(n_episodes): # iterate over new episodes of the game    # Print out which episode we're on, useful for debugging.

    episode = []
    (player_states, (community_infos, community_cards)) = env.reset()
    (player_infos, player_hands) = zip(*player_states)
    current_state = ((player_infos, player_hands), (community_infos, community_cards))
    state = create_np_array(player_infos, player_hands, community_cards, community_infos)

    # Only want the state set that is relevant to learner bot every step. 
    state_set = utilities.convert_list_to_tupleA(player_states[env.learner_bot.get_seat()], current_state[1])

    # if is_with_rendering:
    #     env.render(mode='human', initial=True)
    terminal = False
    while not terminal:

        _round = utilities.which_round(community_cards)
        current_player = community_infos[-1]
        if current_player is not 0:
            action = get_action_policy(player_infos, community_infos, community_cards, env, _round, env.n_seats, state_set, policy)
        else:
            action = agent.act(state, player_infos, community_infos, community_cards, env, _round, env.n_seats, state_set, policy)

        (player_states, (community_infos, community_cards)), action, rewards, terminal, info = env.step(action)

        ps = zip(*player_states)
        next_state = create_np_array(ps[0], ps[1], community_cards, community_infos) # Numpy array
        agent.remember(state, action, reward, next_state, done)
        state = next_state
        if terminal: # episode ends if agent drops pole or we reach timestep 5000
            print("episode: {}/{}, reward: {}, e: {:.2}" # print the episode's score and agent's epsilon
                .format(e, n_episodes, reward, agent.epsilon))
        action = utilities.convert_step_return_to_action(action)
        current_state = (player_states, (community_infos, community_cards)) # state = next_state
        # if is_with_rendering:
        #     env.render(mode='human')

        if len(agent.memory) > batch_size:
            agent.replay(batch_size) # train the agent by replaying the experiences of the episode
        if e % 50 == 0:
            agent.save(output_dir + "weights_" + '{:04d}'.format(e) + ".hdf5")

    utilities.do_necessary_env_cleanup(env) # assign new positions, remove players if stack < 0 etc ..









def generate_episode(env, n_seats):
	# state observation
	episode = []
	(player_states, (community_infos, community_cards)) = env.reset()
	(player_infos, player_hands) = zip(*player_states)
	current_state = ((player_infos, player_hands), (community_infos, community_cards))

	env.render(mode='human', initial=True)
	terminal = False
	while not terminal:

		_round = utilities.which_round(community_cards)
		current_player = community_infos[-1]
		a = (env._current_player.currentbet)
		actions = get_action_policy(player_infos, community_infos, community_cards, env, _round, n_seats)
		(player_states, (community_infos, community_cards)), action, rewards, terminal, info = env.step(actions)
		current_state = (player_states, (community_infos, community_cards))
		episode.append((current_state, action, env.learner_bot.reward))
		env.render(mode='human')

	return episode





# v = mc_prediction_poker(10)
# # for line_no, line in enumerate(v.items()):
# #     print(line_no, line)

# plotting.plot_value_function(v, title="10 Steps")

def mc_control_epsilon_greedy(num_episodes, discount_factor=1.0, epsilon=0.1, is_with_rendering=with_render):
    """
    Monte Carlo Control using Epsilon-Greedy policies.
    Finds an optimal epsilon-greedy policy.
    
    Args:
        env: OpenAI gym environment.
        num_episodes: Number of episodes to sample.
        discount_factor: Gamma discount factor.
        epsilon: Chance the sample a random action. Float betwen 0 and 1.
    
    Returns:
        A tuple (Q, policy).
        Q is a dictionary mapping state -> action values.
        policy is a function that takes an observation as an argument and returns
        action probabilities
    """
    
    # Keeps track of sum and count of returns for each state
    # to calculate an average. We could use an array to save all
    # returns (like in the book) but that's memory inefficient.
    returns_sum = defaultdict(float)
    returns_count = defaultdict(float)
    
    # The final action-value function.
    # A nested dictionary that maps state -> (action -> action-value).
    Q = defaultdict(lambda: np.zeros(env.action_space.n))
    
    # The policy we're following
    policy = make_epsilon_greedy_policy(Q, epsilon, env.action_space.n)
    
    for i_episode in range(1, num_episodes + 1):
        # Print out which episode we're on, useful for debugging.
        if i_episode % 10 == 0:
            print("\rEpisode {}/{}.".format(i_episode, num_episodes), end="")
            sys.stdout.flush()

        # Generate an episode.
        # An episode is an array of (state, action, reward) tuples
        # episode = generate_episode_control(env, env.n_seats, policy)

        episode = []
        (player_states, (community_infos, community_cards)) = env.reset()
        (player_infos, player_hands) = zip(*player_states)
        current_state = ((player_infos, player_hands), (community_infos, community_cards))

        # Only want the state set that is relevant to learner bot every step. 
        state_set = utilities.convert_list_to_tupleA(player_states[env.learner_bot.get_seat()], current_state[1])

        if is_with_rendering:
            env.render(mode='human', initial=True)
        terminal = False
        while not terminal:

            _round = utilities.which_round(community_cards)
            current_player = community_infos[-1]
            a = (env._current_player.currentbet)
            action = get_action_policy(player_infos, community_infos, community_cards, env, _round, env.n_seats, state_set, policy)
            
            (player_states, (community_infos, community_cards)), action, rewards, terminal, info = env.step(action)

            parsed_return_state = utilities.convert_step_return_to_set((current_state, action, env.learner_bot.reward))
            action = utilities.convert_step_return_to_action(action)
            episode.append((parsed_return_state, action, env.learner_bot.reward))
            current_state = (player_states, (community_infos, community_cards)) # state = next_state
            if is_with_rendering:
                env.render(mode='human')

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
            returns_sum[sa_pair] += G
            returns_count[sa_pair] += 1.0
            Q[state][action] = returns_sum[sa_pair] / returns_count[sa_pair]
        
        # The policy is improved implicitly by changing the Q dictionary
    
    return Q, policy

# Q, policy = mc_control_epsilon_greedy(num_episodes=100, epsilon=0.1)


# for item in Q.items():
#     print(item)

# Here we have a Q-table defined which allows us to reference state-action pairs from our poker environment,
# each state-action pair informing the agent on which action led to achieving the optimal policy. 


