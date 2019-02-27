import gym
import holdem

def play_out_hand(env, n_seats):
  # reset environment, gather relevant observations
  (player_states, (community_infos, community_cards)) = env.reset()
  (player_infos, player_hands) = zip(*player_states)

  # display the table, cards and all
  env.render(mode='human')

  terminal = False
  while not terminal:
    # play safe actions, check when noone else has raised, call when raised.
    actions = holdem.safe_actions(community_infos, n_seats=n_seats)
    (player_states, (community_infos, community_cards)), rews, terminal, info = env.step(actions)
    env.render(mode='human')

env = gym.make('TexasHoldem-v1') # holdem.TexasHoldemEnv(2)

# build episodes with a series of calls to play_out_hand()

