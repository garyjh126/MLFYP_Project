from random import randint
from gym import error
from treys import Card
from include import *

class Player(object):

  CHECK = 0
  CALL = 1
  RAISE = 2
  FOLD = 3

  def __init__(self, player_id, stack=2000, emptyplayer=False):
    self.player_id = player_id
    self.hand = []
    self.stack = stack
    self.currentbet = 0
    self.lastsidepot = 0
    self._seat = -1
    self.handrank = -1
    # flags for table management
    self.emptyplayer = emptyplayer
    self.betting = False
    self.isallin = False
    self.playing_hand = False
    self.playedthisround = False
    self.sitting_out = True
    self.evaluation_preflop = {'hand_strength': '', 'he': '', 'evaluation': 0, 'rc': '', 'score_desc': '', 'player_action': ''}
    self.evaluation_flop = {'hand_strength': '', 'he': '', 'evaluation': 0, 'rc': '', 'score_desc': '', 'player_action': ''}
    self.evaluation_turn = {'hand_strength': '', 'he': '', 'evaluation': 0, 'rc': '', 'score_desc': '', 'player_action': ''}
    self.evaluation_river = {'hand_strength': '', 'he': '', 'evaluation': 0, 'rc': '', 'score_desc': '', 'player_action': ''}
    self.he = None
    self.round = {'moves_i_made_in_this_round_sofar': '', 'possible_moves': set([]), 'raises_owed_to_me': 0, "raises_i_owe": 0}
    self.possible_moves = []
    self.position = None
    
  def get_seat(self):
    return self._seat

  def is_possible(self, move):
    move_possible = False
    for item in self.round['possible_moves']:
      if item == move:
        return True
        break
    return move_possible 

  def which_action(self, _round, range_structure):
    action = ''
    if range_structure == preflop_range:
      which_eval = self.evaluation_preflop
    elif range_structure == flop_range:
      which_eval = self.evaluation_flop
    elif range_structure == turn_river:
      which_eval = self.evaluation_turn
      # include river

    if (which_eval["evaluation"] < range_structure['betting'][self.round['raises_i_owe']][self.position]):
      action = (2, 25)
    elif (which_eval["evaluation"] < range_structure['calling'][self.round['raises_i_owe']][self.position]):
      action = (1, 0) # or 0
    else:
      action = (3, 0)

    return action

  def set_seat(self, value):
    self._seat = value


  def reset_hand(self):
    self._hand = []
    self.playedthisround = False
    self.betting = False
    self.isallin = False
    self.currentbet = 0
    self.lastsidepot = 0
    self.playing_hand = (self.stack != 0)

  def bet(self, bet_size):
    self.playedthisround = True
    if not bet_size:
      return
    self.stack -= (bet_size - self.currentbet)
    self.currentbet = bet_size
    if self.stack == 0:
      self.isallin = True

  def refund(self, ammount):
    self.stack += ammount

  def player_state(self):
    return (self.get_seat(), self.stack, self.playing_hand, self.betting, self.player_id)

  def reset_stack(self):
    self.stack = 2000

  def update_localstate(self, table_state):
    self.stack = table_state.get('stack')
    self.hand = table_state.get('pocket_cards')

  # cleanup
  def player_move(self, table_state, action):
    self.update_localstate(table_state)
    bigblind = table_state.get('bigblind')
    tocall = min(table_state.get('tocall', 0), self.stack)
    minraise = table_state.get('minraise', 0)

    

    [action_idx, raise_amount] = action
    raise_amount = int(raise_amount)
    action_idx = int(action_idx)

    if tocall == 0:
      assert action_idx in [Player.CHECK, Player.RAISE]
      if action_idx == Player.RAISE:
        if raise_amount < minraise:
          raise error.Error('raise must be greater than minraise {}'.format(minraise))
        if raise_amount > self.stack:
          raise error.Error('raise must be less than maxraise {}'.format(self.stack))
        move_tuple = ('raise', raise_amount)
      elif action_idx == Player.CHECK:
        move_tuple = ('check', 0)
      else:
        raise error.Error('invalid action ({}) must be check (0) or raise (2)'.format(action_idx))
    else:
      if action_idx not in [Player.RAISE, Player.CALL, Player.FOLD]:
        raise error.Error('invalid action ({}) must be raise (2), call (1), or fold (3)'.format(action_idx))
      if action_idx == Player.RAISE:
        if raise_amount < minraise:
          raise error.Error('raise must be greater than minraise {}'.format(minraise))
        if raise_amount > self.stack:
          raise error.Error('raise must be less than maxraise {}'.format(self.stack))
        move_tuple = ('raise', raise_amount)
      elif action_idx == Player.CALL:
        move_tuple = ('call', tocall)
      elif action_idx == Player.FOLD:
        move_tuple = ('fold', -1)
      else:
        raise error.Error('invalid action ({}) must be raise (2), call (1), or fold (3)'.format(action_idx))
    return move_tuple


class CardHolding(Player):

  def __init__(self, name, first_card_suit, first_card_rank, second_card_suit, second_card_rank):
    self.name = name
    self.first_card_suit = first_card_suit
    self.first_card_rank = first_card_rank
    self.second_card_suit = second_card_suit
    self.second_card_rank = second_card_rank

  def __str__(self):
    first_card = self.first_card_suit, self.first_card_rank
    second_card = self.second_card_suit, self.second_card_rank
    st = 'Name: {}'.format(self.name) + '\tFirst Card: {}'.format(str(first_card)) + '\tSecond Card: {}\n'.format(str(second_card))
    return (str(st))
  
  def get_card(self, card_no):
    if card_no == 0:
      return self.first_card_rank + self.first_card_suit
        
    else:
      return self.second_card_rank,self.second_card_suit