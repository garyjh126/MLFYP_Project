
from gym import Env, error, spaces, utils
from gym.utils import seeding

from treys import Card, Deck, Evaluator

from .player import Player
from .utils import hand_to_str, format_action
from collections import OrderedDict


class TexasHoldemEnv(Env, utils.EzPickle):
	BLIND_INCREMENTS = [[10,25], [25,50], [50,100], [75,150], [100,200],
						[150,300], [200,400], [300,600], [400,800], [500,10000],
						[600,1200], [800,1600], [1000,2000]]
	
	current_player_notifier = ""
	deal_players=0
	flop_times_called_debug = 0
	turn_times_called_debug = 0
	river_times_called_debug = 0
	def __init__(self, n_seats, max_limit=100000, debug=False):
		n_suits = 4                     # s,h,d,c
		n_ranks = 13                    # 2,3,4,5,6,7,8,9,T,J,Q,K,A
		n_community_cards = 5           # flop, turn, river
		n_pocket_cards = 2
		n_stud = 5

		self.level_raises = {0:0, 1:0, 2:0} # Assuming 3 players
		
		self.n_seats = n_seats
		self._blind_index = 0
		[self._smallblind, self._bigblind] = TexasHoldemEnv.BLIND_INCREMENTS[0]
		self._deck = Deck()
		self._evaluator = Evaluator()
		self.last_seq_move = [] 
		self.filled_seats = 0
		

		self.community = []
		self._round = 0
		self._button = 0
		self._discard = []

		self._side_pots = [0] * n_seats
		self._current_sidepot = 0 # index of _side_pots
		self._totalpot = 0
		self._tocall = 0
		self._lastraise = 0
		self._number_of_hands = 0

		# fill seats with dummy players
		self._seats = [Player(i, stack=0, emptyplayer=True) for i in range(n_seats)]
		self.emptyseats = n_seats
		self._player_dict = {}
		self._current_player = None
		self._debug = debug
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

		### MAY NEED TO ALTER FOR HEADS-UP
		# self.action_space = spaces.Tuple([
		# spaces.MultiDiscrete([
		# 	3,                     # action_id
		# 	max_limit,             # raise_amount
		# ]),
		# ] * n_seats) 
		self.action_space = spaces.Discrete(4)


	def seed(self, seed=None):
		_, seed = seeding.np_random(seed)
		return [seed]


	# Important Note: Positions are only assigned at end of game. Be aware in 
	# case of reporting stats on position type
	def assign_positions(self):
		no_active_players = self.filled_seats
		if(self.filled_seats == 3):
			for player in self._seats:
				player.position = (player.position + (no_active_players-1)) % no_active_players if player in self._player_dict.values() else None

		elif(self.filled_seats == 2):
			new_positions = []
			# We want to only use positions 0 and 2, which are encodings of BTN and BB respectively

			# Sort for positions 0 and 2 first
			for player in self._player_dict.values():
				if not(player.emptyplayer):
					if player.position == 2:
						player.position == 0
						new_positions.append(player.position)
					elif player.position == 0:
						potential_next = 2
						new_positions.append(player.position)
				
			
			# Special case of former position 1 depends on new positions allocated above
			for player in self._player_dict.values():
				if player.position == 1:
					if len(new_positions) == 1:
						if new_positions[0] == 0:
							player.position = 2
						elif new_positions[0] == 2:
							player.position = 0
					
						


			
				



	def add_player(self, seat_id, stack=2000):
		"""Add a player to the environment seat with the given stack (chipcount)"""
		player_id = seat_id
		if player_id not in self._player_dict:
			new_player = Player(player_id, stack=stack, emptyplayer=False)
			if self._seats[player_id].emptyplayer:
				self._seats[player_id] = new_player
				new_player.set_seat(player_id)
			else:
				raise error.Error('Seat already taken.')
			self._player_dict[player_id] = new_player
			self.emptyseats -= 1
			self.filled_seats +=1

	def move_player_to_empty_seat(self, player):
		# priority queue placing active players at front of table
		for seat_no in range(len(self._seats)):
			if self._seats[seat_no].emptyplayer and (seat_no < player._seat):
				unused_player = self._seats[seat_no]
				self._seats[seat_no] = player
				self._seats[player.get_seat()] = unused_player

	def reassign_players_seats(self):
		for player in self._player_dict.values():
			self.move_player_to_empty_seat(player)

	def remove_player(self, seat_id):
		"""Remove a player from the environment seat."""
		player_id = seat_id
		
		try:
			idx = self._seats.index(self._player_dict[player_id])
			self._seats[idx] = Player(0, stack=0, emptyplayer=True)
			
			self._seats[idx].position = None # Very important for when transitioning from 3 to 2 players.
			del self._player_dict[player_id]
			self.emptyseats += 1
			self.filled_seats-=1
			#self.reassign_players_seats()
		except ValueError:
			pass

	def reset(self):
		self._reset_game()
		self._ready_players()
		self._number_of_hands = 1
		[self._smallblind, self._bigblind] = TexasHoldemEnv.BLIND_INCREMENTS[0]
		if (self.emptyseats < len(self._seats) - 1):
			players = [p for p in self._seats if p.playing_hand]
			self._new_round()
			self._round = 0
			self._current_player = self._first_to_act(players, "post_blinds")
			self._post_smallblind(self._current_player)
			self._current_player = self._next(players, self._current_player)
			self._post_bigblind(self._current_player)
			self._current_player = self._next(players, self._current_player)
			self._tocall = self._bigblind
			self._round = 0
			self._deal_next_round()
			self._folded_players = []
		return self._get_current_reset_returns()

	def assume_unique_cards(self, players):
		cards_count = {}
		this_board = None
		for player in players:
			player_cards = player.hand
			for card in player_cards:
				cards_count.update({card: 1}) if card not in cards_count else cards_count.update({card: cards_count[card] + 1})
			if this_board is None and player.he is not None:
				if player.he.board is not None:
					this_board = player.he.board 
		if this_board is not None:
			for card in this_board:
				cards_count.update({card: 1}) if card not in cards_count else cards_count.update({card: cards_count[card] + 1})
		
		for card, no_occurence in cards_count.items():
			if no_occurence > 1:
				return False
			else:
				return True

	def step(self, actions):
		"""
		CHECK = 0
		CALL = 1
		RAISE = 2
		FO

		RAISE_AMT = [0, minraise]
		"""
		
		players = [p for p in self._seats if p.playing_hand]
		assert self.assume_unique_cards(players) is True

		self._last_player = self._current_player
		# self._last_actions = actions
		
		



		# if current player did not play this round 
		if not self._current_player.playedthisround and len([p for p in players if not p.isallin]) >= 1:
			if self._current_player.isallin:
				self._current_player = self._next(players, self._current_player)
				return self._get_current_step_returns(False)

			move = self._current_player.player_move(self._output_state(self._current_player), actions[self._current_player.player_id])
			if self.am_i_only_player_wmoney() and self.level_raises[self._current_player.get_seat()] >= self.highest_in_LR()[0]:
				move = ("check", 0) # Protects against player making bets without any other stacked/active players
			self._last_actions = move
			if move[0] == 'call':
				assert self.action_space.contains(1)
				self._player_bet(self._current_player, self._tocall, is_posting_blind=False, bet_type=move[0])
				if self._debug:
					print('Player', self._current_player.player_id, move)
				self._current_player = self._next(players, self._current_player)
				self.last_seq_move.append('C')
				self.playedthisround = True

			elif move[0] == 'check':
				assert self.action_space.contains(0)
				self._player_bet(self._current_player, self._current_player.currentbet, is_posting_blind=False, bet_type=move[0])
				if self._debug:
					print('Player', self._current_player.player_id, move)
				self._current_player = self._next(players, self._current_player)
				self.last_seq_move.append('c')
				self.playedthisround = True

			elif move[0] == 'raise':
			
				assert self.action_space.contains(2)
				
				self._player_bet(self._current_player, move[1]+self._current_player.currentbet, is_posting_blind=False, bet_type="bet/raise")
				if self._debug:
					print('Player', self._current_player.player_id, move)
				for p in players:
					if p != self._current_player:
						p.playedthisround = False
				self._current_player = self._next(players, self._current_player)
				
				self.last_seq_move.append('R')
			elif move[0] == 'fold':
				assert self.action_space.contains(3)
				self._current_player.playing_hand = False
				self._current_player.playedthisround = True
				if self._debug:
					print('Player', self._current_player.player_id, move)
				self._current_player = self._next(players, self._current_player)
				
				self._folded_players.append(self._current_player)
				self.last_seq_move.append('F')
				# break if a single player left
				if len(players) == 1:
					self._resolve(players)

		# else:	## This will help eliminate infinite loop
		# 	self._current_player = self._next(players, self._current_player)
			
		# This will effectively dictate who will become dealer after flop	
		players_with_money = []
		for player in players:
			if(player.stack > 0):
				players_with_money.append(player)
		if all([player.playedthisround for player in players_with_money]):
			self._resolve(players)
			for player in self._player_dict.values():
				player.round == {'moves_i_made_in_this_round_sofar': '', 'possible_moves': set([]), 'raises_owed_to_me': 0, "raises_i_owe": 0}
		

		terminal = False
		if all([player.isallin for player in players]):
			while self._round < 4:
				self._deal_next_round()
				self._round += 1

		elif self.count_active_wmoney() == 1 and all([player.playedthisround for player in players]):
			# do something else here
			while self._round < 3:
				self._round += 1
				self._deal_next_round()
			

		if self._round == 4 or len(players) == 1:
			terminal = True
			self._resolve_round(players)

		return self._get_current_step_returns(terminal)

	def am_i_only_player_wmoney(self):
		count_other_broke = 0
		for player in self._player_dict.values():
			if player is not self._current_player and player.stack <= 0:
				count_other_broke += 1
		if count_other_broke == (len(self._player_dict) - 1):
			return True
		else:
			return False

	def count_active_wmoney(self):
		count = 0
		account_active_money = {0:{"is_active":False, "has_money":False},1:{"is_active":False, "has_money":False},2:{"is_active":False, "has_money":False}}
		for player in self._player_dict.values():
			if player.playing_hand:
				account_active_money[player.get_seat()].update({"is_active": True})
			if player.stack > 0:
				account_active_money[player.get_seat()].update({"has_money": True})
			
		for player, account in account_active_money.items():
			if account["is_active"] is True and account["has_money"] is True:
				count+=1

		return count



	def render(self, mode='human', close=False, initial=False):
		if(initial is True):
			print("\n")
				
		if self._last_actions is not None and initial is False:
			pid = self._last_player.player_id
			#print('last action by player {}:'.format(pid))
			print(format_action(self._last_player, self._last_actions))

		print("\n\n")
		print('Total Pot: {}'.format(self._totalpot))
		
		(player_states, community_states) = self._get_current_state()
		(player_infos, player_hands) = zip(*player_states)
		(community_infos, community_cards) = community_states

		print('Board:')
		print('-' + hand_to_str(community_cards))
		print('Players:')
		# for player in self._player_dict:
		# 	assert player.round['raises_i_owe']
		for idx, hand in enumerate(player_hands):
			if self._current_player.get_seat() == idx:
				self.current_player_notifier = "<" + str(self._current_player.position)
				
			print('{}{}stack: {} {}'.format(idx, hand_to_str(hand), self._seats[idx].stack, self.current_player_notifier))
			self.current_player_notifier = ""
	def _resolve(self, players):
		self._current_player = self._first_to_act(players)
		self._resolve_sidepots(players + self._folded_players)
		self._new_round()
		self._deal_next_round()
		if self._debug:
			print('totalpot', self._totalpot)

	def _resolve_postflop(self, players):
		self._current_player = self._first_to_act(players)
		print(self._current_player)

	def _deal_next_round(self):
		if self._round == 0:
			self._deal()
		elif self._round == 1:
			self._flop()
		elif self._round == 2:
			self._turn()
		elif self._round == 3:
			self._river()

	def _increment_blinds(self):
		self._blind_index = min(self._blind_index + 1, len(TexasHoldemEnv.BLIND_INCREMENTS) - 1)
		[self._smallblind, self._bigblind] = TexasHoldemEnv.BLIND_INCREMENTS[self._blind_index]

	def _post_smallblind(self, player):
		if self._debug:
			print('player ', player.player_id, 'small blind', self._smallblind)
		self._player_bet(player, self._smallblind, is_posting_blind=True)
		player.playedthisround = False

	def _post_bigblind(self, player):
		if self._debug:
			print('player ', player.player_id, 'big blind', self._bigblind)
		self._player_bet(player, self._bigblind, is_posting_blind=True)
		player.playedthisround = False
		self._lastraise = self._bigblind

	def highest_in_LR(self):
		highest_lr_bot = 0
		highest_lr_value = 0
		
		for key, value in self.level_raises.items():
			if value > highest_lr_value:
				highest_lr_value = value
				highest_lr_bot = key
		return highest_lr_value, highest_lr_bot

	def is_level_raises_allzero(self):
		count_zero = 0
		for value in self.level_raises.values():
			if value == 0:
				count_zero+=1
		if(count_zero == len(self.level_raises)):
			return True
		else: 
			return False

	def _player_bet(self, player, total_bet, **special_betting_type):
		if "is_posting_blind" in special_betting_type and "bet_type" not in special_betting_type: # posting blind (not remainder to match preceding calls/raises)
			if special_betting_type["is_posting_blind"] is True:
				self.level_raises[player.get_seat()] = 0 

		elif "is_posting_blind" in special_betting_type and "bet_type" in special_betting_type: # Bet/Raise or call. Also accounts for checks preflop.
			highest_lr_value, highest_lr_bot = self.highest_in_LR()
			if special_betting_type["is_posting_blind"] is False:
				if special_betting_type["bet_type"] == "bet/raise":
					if self.level_raises[player.get_seat()] < highest_lr_value:
						action_type = "raise"
						self.level_raises[player.get_seat()] = highest_lr_value + 1
					elif self.level_raises[player.get_seat()] == highest_lr_value:
						action_type = "bet"
						self.level_raises[player.get_seat()] += 1

				elif special_betting_type["bet_type"] == "call":
					if self.level_raises[player.get_seat()] < highest_lr_value:
						action_type = "call"
						self.level_raises[player.get_seat()] = highest_lr_value

					elif self.is_level_raises_allzero():
						if player.position == 0:
							action_type = "call"
							self.level_raises[player.get_seat()] = 1


					elif player.position == 2:
						action_type = "call"
						self.level_raises[player.get_seat()] = highest_lr_value

				elif special_betting_type["bet_type"] == "check" and self._round is 0:	# BB checking preflop
					if player.position == 2:
						self.level_raises[player.get_seat()] = 1
					

		# relative_bet is how much _additional_ money is the player betting this turn,
		# on top of what they have already contributed
		# total_bet is the total contribution by player to pot in this round
		relative_bet = min(player.stack, total_bet - player.currentbet)
		player.bet(relative_bet + player.currentbet)

		self._totalpot += relative_bet
		self._tocall = max(self._tocall, total_bet)
		if self._tocall > 0:
			self._tocall = max(self._tocall, self._bigblind)
		self._lastraise = max(self._lastraise, relative_bet  - self._lastraise)

	def _first_to_act(self, players, my_event="Postflop"):
		# if self._round == 0 and len(players) == 2:
		# 	return self._next(sorted(
		# 		players + [self._seats[self._button]], key=lambda x:x.get_seat()),
		# 		self._seats[self._button])
		
		first_to_act = None

		if self.filled_seats == 2:
			if my_event is "Preflop" or my_event is "post_blinds":
				first_to_act = self.assign_next_to_act(players, [0,2])

			elif my_event is "Postflop" or my_event is "sidepot":
				first_to_act = self.assign_next_to_act(players, [2,0])

		elif self.filled_seats == 3:
			if my_event is "Preflop":
				first_to_act = self.assign_next_to_act(players, [0,1,2])

			elif my_event is "Postflop" or my_event is "post_blinds" or my_event is "sidepot":
				first_to_act = self.assign_next_to_act(players, [1,2,0])

		# else: 
		# 	my_return = [player for player in players if player.get_seat() > self._button][0]
			
		#assert first_to_act is not None and not(first_to_act.emptyplayer) and not(first_to_act.stack <= 0)
		return first_to_act

	def assign_next_to_act(self, players, precedence_positions):
		for pos in precedence_positions:
			for player in players:
				if player.position == pos and not(player.emptyplayer) and player.playing_hand and player.stack > 0:
					assert player is not None
					return player

	def _next(self, players, current_player):
		i = 1
		current_player_seat = players.index(current_player)
		
		while(players[(current_player_seat+i) % len(players)].stack <= 0):
			i+=1
			if i > 10: 
				break
				# In this case of inifinte loop, self._current_player is assigned to _next but will be irrelevant anyway so okay.
		assert players[(current_player_seat+i) % len(players)] is not None
		return players[(current_player_seat+i) % len(players)]

	def _deal(self):
		self.deal_players+=1
		for player in self._seats:
			if player.playing_hand and player.stack > 0:
				player.hand = self._deck.draw(2)
				

	def _flop(self):
		self.flop_times_called_debug+=1
		self._discard.append(self._deck.draw(1)) #burn
		this_flop = self._deck.draw(3)
		self.flop_cards = this_flop
		self.community = this_flop

	def _turn(self):
		self.turn_times_called_debug+=1
		self._discard.append(self._deck.draw(1)) #burn
		self.turn_card = self._deck.draw(1)
		self.community.append(self.turn_card)
		# .append(self.community)

	def _river(self):
		self.river_times_called_debug+=1
		self._discard.append(self._deck.draw(1)) #burn
		self.river_card = self._deck.draw(1)
		self.community.append(self.river_card)

	def _ready_players(self):
		for p in self._seats:
			if not p.emptyplayer and p.sitting_out:
				p.sitting_out = False
				p.playing_hand = True
		
		

	def _resolve_sidepots(self, players_playing):
		players = [p for p in players_playing if p.currentbet]
		if self._debug:
			print('current bets: ', [p.currentbet for p in players])
			print('playing hand: ', [p.playing_hand for p in players])
		if not players:
			return
		try:
			smallest_bet = min([p.currentbet for p in players if p.playing_hand])
		except ValueError:
			for p in players:
				self._side_pots[self._current_sidepot] += p.currentbet
				p.currentbet = 0
			return

		smallest_players_allin = [p for p, bet in zip(players, [p.currentbet for p in players]) if bet == smallest_bet and p.isallin]

		for p in players:
			self._side_pots[self._current_sidepot] += min(smallest_bet, p.currentbet)
			p.currentbet -= min(smallest_bet, p.currentbet)
			p.lastsidepot = self._current_sidepot

		if smallest_players_allin:
			self._current_sidepot += 1
			self._resolve_sidepots(players)
		if self._debug:
			print('sidepots: ', self._side_pots)

	def _new_round(self):
		for player in self._player_dict.values():
			player.currentbet = 0
			player.playedthisround = False
			player.round = {'moves_i_made_in_this_round_sofar': '', 'possible_moves': set([]), 'raises_owed_to_me': 0, "raises_i_owe": 0}
		
		self._round += 1
		self._tocall = 0
		self._lastraise = 0
		self.last_seq_move = []

	def _resolve_round(self, players):
		if len(players) == 1:
			players[0].refund(sum(self._side_pots))
			self._totalpot = 0
		else:
			# compute hand ranks
			for player in players:
				assert (len(self.community) <= 5) is True
				player.handrank = self._evaluator.evaluate(player.hand, self.community)

			# trim side_pots to only include the non-empty side pots
			temp_pots = [pot for pot in self._side_pots if pot > 0]

			# compute who wins each side pot and pay winners
			for pot_idx,_ in enumerate(temp_pots):
				# find players involved in given side_pot, compute the winner(s)
				pot_contributors = [p for p in players if p.lastsidepot >= pot_idx]
				winning_rank = min([p.handrank for p in pot_contributors])
				winning_players = [p for p in pot_contributors if p.handrank == winning_rank]

				for player in winning_players:
					split_amount = int(self._side_pots[pot_idx]/len(winning_players))
					if self._debug:
						print('Player', player.player_id, 'wins side pot (', int(self._side_pots[pot_idx]/len(winning_players)), ')')
					player.refund(split_amount)
					self._side_pots[pot_idx] -= split_amount

				# any remaining chips after splitting go to the winner in the earliest position
				if self._side_pots[pot_idx]:
					earliest = self._first_to_act([player for player in winning_players], "sidepot")
					earliest.refund(self._side_pots[pot_idx])

			# for player in players: ## THIS IS AT THE END OF THE GAME. NOT DURING. (safe)
			# 	if(player.stack == 0):
			# 		self.remove_player(player.get_seat())

	def report_game(self, requested_attributes, specific_player=None):
		
		if "stack" in requested_attributes:
			player_stacks = {}
			for key, player in self._player_dict.items():
				
				player_stacks.update({key: player.stack})
			
			# if len(player_stacks) < 3:
			# 	for i in range(3):
			# 		if i not in player_stacks:
			# 			player_stacks.update({i:0})
			if specific_player is None:
				return (player_stacks)
				assert (player_stacks.values()) is not None
			else:
				return (player_dict[specific_player].values())
				 
		
		

		


		

	def _reset_game(self):
		
		playing = 0

		for i, val in self._player_dict.items():
			if val is not None:
				val.he = None
		for player in self._seats:
			if not player.emptyplayer and not player.sitting_out:
				player.reset_hand()
				playing += 1
		self.community = []
		self._current_sidepot = 0
		self._totalpot = 0
		self._side_pots = [0] * len(self._seats)
		self._deck.shuffle()
		self.level_raises = {0:0, 1:0, 2:0}

		if playing:
			self._button = (self._button + 1) % len(self._seats)
			while not self._seats[self._button].playing_hand:
				self._button = (self._button + 1) % len(self._seats)

	def _output_state(self, current_player):
		return {
		'players': [player.player_state() for player in self._seats],
		'community': self.community,
		'my_seat': current_player.get_seat(),
		'pocket_cards': current_player.hand,
		'pot': self._totalpot,
		'button': self._button,
		'tocall': (self._tocall - current_player.currentbet),
		'stack': current_player.stack,
		'bigblind': self._bigblind,
		'player_id': current_player.player_id,
		'lastraise': self._lastraise,
		'minraise': max(self._bigblind, self._lastraise + self._tocall),
		}

	def _pad(self, l, n, v):
		if (not l) or (l is None):
			l = []
		return l + [v] * (n - len(l))

	def _get_current_state(self):
		player_states = []
		for player in self._seats:
			player_features = [
				int(player.emptyplayer),
				int(player.get_seat()),
				int(player.stack),
				int(player.playing_hand),
				int(player.handrank),
				int(player.playedthisround),
				int(player.betting),
				int(player.isallin),
				int(player.lastsidepot),
			]
			player_states.append((player_features, self._pad(player.hand, 2, -1)))
		community_states = ([
			int(self._button),
			int(self._smallblind),
			int(self._bigblind),
			int(self._totalpot),
			int(self._lastraise),
			int(max(self._bigblind, self._lastraise + self._tocall)),
			int(self._tocall - self._current_player.currentbet),
			int(self._current_player.player_id),
		], self._pad(self.community, 5, -1))
		return (tuple(player_states), community_states)

	def _get_current_reset_returns(self):
		return self._get_current_state()

	def _get_current_step_returns(self, terminal):
		obs = self._get_current_state()
		# TODO, make this something else?
		rew = [player.stack for player in self._seats]
		return obs, rew, terminal, [] # TODO, return some info?
