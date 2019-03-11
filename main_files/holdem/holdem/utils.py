from treys import Card


class action_table:
  CHECK = 0
  CALL = 1
  RAISE = 2
  FOLD = 3
  NA = 0


def format_action(player, action):
  color = False
  try:
    from termcolor import colored
    # for mac, linux: http://pypi.python.org/pypi/termcolor
    # can use for windows: http://pypi.python.org/pypi/colorama
    color = True
  except ImportError:
    pass
  [aid, raise_amt] = action
  if aid == action_table.CHECK:
    text = '_ check'
    if color:
      text = colored(text, 'white')
    return text
  if aid == action_table.CALL:
    text = '- call, current bet: {}'.format(player.currentbet)
    if color:
      text = colored(text, 'yellow')
    return text
  if aid == action_table.RAISE:
    text = '^ raise, current bet: {}'.format(raise_amt)
    if color:
      text = colored(text, 'green')
    return text
  if aid == action_table.FOLD:
    text = 'x fold'
    if color:
      text = colored(text, 'red')
    return text


def card_to_str(card):
  if card == -1:
    return ''
  return Card.int_to_pretty_str(card)


def hand_to_str(hand):
  output = " "
  for i in range(len(hand)):
    c = hand[i]
    if c == -1:
      if i != len(hand) - 1:
        output += '[  ],'
      else:
        output += '[  ] '
      continue
    if i != len(hand) - 1:
      output += str(Card.int_to_pretty_str(c)) + ','
    else:
      output += str(Card.int_to_pretty_str(c)) + ' '
  return output


def safe_actions(community_infos, which_action, n_seats):
  current_player = community_infos[-1]
  to_call = community_infos[-2]
  actions = [[action_table.CHECK, action_table.NA]] * n_seats
  if to_call > 0:
    if which_action is None:
      actions[current_player] = [action_table.CALL, action_table.NA]
    else:
      actions[current_player] = [which_action[0], which_action[1]]
  return actions		
	
	


