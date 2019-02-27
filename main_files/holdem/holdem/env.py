from gym import Env, error, spaces, utils
from gym.utils import seeding

from treys import Card, Deck, Evaluator


class TexasHoldemEnv(Env, utils.EzPickle):

	def __init__(self, n_seats, max_limit=100000, debug=False):
		
		self.n_seats = n_seats
		self._deck = Deck()
		self._evaluator = Evaluator()

		self.community = []
		self._round = 0
		self._button = 0


		self._seats = [Player(i, stack=0, emptyplayer=True) for i in range(n_seats)]
		self.emptyseats = n_seats
		self._player_dict = {}
		self._current_player = None
		self._last_player = None
		self._last_actions = None

		self.observation_space = spaces.Tuple([
		spaces.Tuple([                # players
			spaces.MultiDiscrete([
			1,                   # emptyplayer
			n_seats - 1,         # seat
			max_limit,           # stack
			1,                   # is_playing_hand
			max_limit,           # handrank
			1,                   # playedthisround
			1,                   # is_betting
			1,                   # isallin
			max_limit,           # last side pot
			]),
			spaces.Tuple([
			spaces.MultiDiscrete([    # hand
				n_suits,          # suit, can be negative one if it's not avaiable.
				n_ranks,          # rank, can be negative one if it's not avaiable.
			])
			] * n_pocket_cards)
		] * n_seats),
		spaces.Tuple([
			spaces.Discrete(n_seats - 1), # big blind location
			spaces.Discrete(max_limit),   # small blind
			spaces.Discrete(max_limit),   # big blind
			spaces.Discrete(max_limit),   # pot amount
			spaces.Discrete(max_limit),   # last raise
			spaces.Discrete(max_limit),   # minimum amount to raise
			spaces.Discrete(max_limit),   # how much needed to call by current player.
			spaces.Discrete(n_seats - 1), # current player seat location.
			spaces.MultiDiscrete([        # community cards
			n_suits - 1,          # suit
			n_ranks - 1,          # rank
			1,                     # is_flopped
			]),
		] * n_stud),
		])

		self.action_space = spaces.Tuple([
			spaces.MultiDiscrete([
				3,                     # action_id
			]),
		] * n_seats)

	def seed(self, seed=None):
		_, seed = seeding.np_random(seed)
		return [seed]


	def reset(self):
		self._reset_game()
		self._ready_players()
		self._number_of_hands = 1
		if (self.emptyseats < len(self._seats) - 1):
			players = [p for p in self._seats if p.playing_hand]
			self._new_round()
			self._round = 0
			self._current_player = self._first_to_act(players)
			self._post_smallblind(self._current_player)
			self._current_player = self._next(players, self._current_player)
			self._post_bigblind(self._current_player)
			self._current_player = self._next(players, self._current_player)
			self._tocall = self._bigblind
			self._round = 0
			self._deal_next_round()
			self._folded_players = []
		return self._get_current_reset_returns()	
	
	def step(self, actions):
		"""
		CHECK = 0
		CALL = 1
		RAISE = 2
		FOLD = 3
		
		"""
		if len(actions) != len(self._seats):
			raise error.Error('actions must be same shape as number of seats.')

		if self._current_player is None:
			raise error.Error('Round cannot be played without 2 or more players.')

		if self._round == 4:
			raise error.Error('Rounds already finished, needs to be reset.')

		players = [p for p in self._seats if p.playing_hand]
		if len(players) == 1:
			raise error.Error('Round cannot be played with one player.')

		self._last_player = self._current_player
		self._last_actions = actions

		if not self._current_player.playedthisround and len([p for p in players if not p.isallin]) >= 1:
			if self._current_player.isallin:
				self._current_player = self._next(players, self._current_player)
				return self._get_current_step_returns(False)

			move = self._current_player.player_move(
				self._output_state(self._current_player), actions[self._current_player.player_id])

			if move[0] == 'call':
				self._player_bet(self._current_player, self._tocall)
				if self._debug:
					print('Player', self._current_player.player_id, move)
				self._current_player = self._next(players, self._current_player)
			elif move[0] == 'check':
				self._player_bet(self._current_player, self._current_player.currentbet)
				if self._debug:
					print('Player', self._current_player.player_id, move)
				self._current_player = self._next(players, self._current_player)
			elif move[0] == 'raise':
				self._player_bet(self._current_player, move[1]+self._current_player.currentbet)
				if self._debug:
					print('Player', self._current_player.player_id, move)
				for p in players:
					if p != self._current_player:
						p.playedthisround = False
				self._current_player = self._next(players, self._current_player)
			elif move[0] == 'fold':
				self._current_player.playing_hand = False
				folded_player = self._current_player
				if self._debug:
					print('Player', self._current_player.player_id, move)
				self._current_player = self._next(players, self._current_player)
				players.remove(folded_player)
				self._folded_players.append(folded_player)
				# break if a single player left
				if len(players) == 1:
					self._resolve(players)
		if all([player.playedthisround for player in players]):
			self._resolve(players)

		terminal = False
		if all([player.isallin for player in players]):
			while self._round < 4:
				self._deal_next_round()
				self._round += 1
		if self._round == 4 or len(players) == 1:
			terminal = True
			self._resolve_round(players)
		return self._get_current_step_returns(terminal)