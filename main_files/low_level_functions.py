import re 
import Player as p
import numpy as np

def create_cards_for_game():
    suits = ['h','c','s','d']
    li = []
    
    for rank in range(13):
        for suit in suits:
            if(rank == 8):
                card_r = 'T'
            elif(rank == 9):
                card_r = 'J'
            elif(rank == 10):
                card_r = 'Q'
            elif(rank == 11):
                card_r = 'K'
            elif(rank == 12):
                card_r = 'A'
            else:
                card_r = str(rank+2)
            card_str = card_r+suit
            li.append(card_str)
            
    return li

def casinoToBot_ParsingUpdateUniversal(self, file_data_original_change, plr, player_list, player_action):
    
    # arr =  re.split(r'[DPFFFFTTRR]',file_data_original_change)
    # pre_flop_last_move = arr[2]
    # btc_file = "/casinoToBotUniversal"
    # file_name = communication_files_directory='/usr/local/home/u180455/Desktop/Project/MLFYP_Project/MLFYP_Project/pokercasino/botfiles' + btc_file 
    # with open(file_name, 'wt') as f:
    #     f.append(pre_flop_last_move)
    #     f.close()
    # print("last_move:", pre_flop_last_move)
    pass

def casinoToBot_ParsingRead(self, file_data_change_CTB, plr, player_list, bot_no):
    # <hand number> D <dealer button position> P <action by all players in order from first to 
    # act, e.g. fccrf...> F <flop card 1> F <flop 2> F <flop 3> F <flop action starting with first player to act>
    # T <turn card> T <turn action> R <river card> R <river action>
    is_preflop_action_filled = False
    is_flop_action_filled = False
    is_turn_action_filled = False
    is_river_action_filled = False
    file_data_change_CTB =  re.split(r'[DPFFFFTTRR]',file_data_change_CTB)

    button = file_data_change_CTB[1]
    iDealer = False
    self.player_list[int(bot_no)].position = ''
    number_of_players = 3 

    if button == bot_no:
        iDealer = True
        self.player_list[int(bot_no)].position = 'BTN'
        self.player_list[(int(bot_no)+1) % number_of_players].position = 'SB'
        self.player_list[(int(bot_no)+2) % number_of_players].position = 'BB'

    if button == str((int(bot_no) + 1) % number_of_players):
        iDealer = False
        self.player_list[int(bot_no)].position = 'BB'
        self.player_list[(int(bot_no)+1) % number_of_players].position = 'BTN'
        self.player_list[(int(bot_no)+2) % number_of_players].position = 'SB'

    if button == str((int(bot_no) + 2) % number_of_players):
        iDealer = False
        self.player_list[int(bot_no)].position = 'SB'
        self.player_list[(int(bot_no)+1) % number_of_players].position = 'BB'
        self.player_list[(int(bot_no)+2) % number_of_players].position = 'BTN'

    
    # need to do same for other rotations of table other than the standard fixation

    


    #print("{}.. Hand Number: {}, Game_status: {}".format(plr, file_data_change_CTB[0], file_data_change_CTB))
    
    # Here we must update the local static game_state variable to the status read from CasinoToBot
    blank = True
    if file_data_change_CTB[0] != None and file_data_change_CTB[0] != '':
        blank = False
    
    if blank == False:
        #HAND NO
        if p.Player.game_state['hand_no'] == '':
            if file_data_change_CTB[0] != None:
                p.Player.game_state['hand_no'] = file_data_change_CTB[0]

        
        #DEALER POSITION
        if p.Player.game_state['dealer_position'] == '':
            if file_data_change_CTB[1] != None:
                for i in range(len(player_list)):
                    if str(file_data_change_CTB[1]) == str(i):
                        player_list[i].dealer_status = True
                        p.Player.game_state['dealer_position'] = i
                    else: 
                        player_list[i].dealer_status = False


        if file_data_change_CTB[2] != None:
            if file_data_change_CTB[2] == '':
                is_preflop_action_filled = False
            else:
                is_preflop_action_filled = True
        else: 
            is_preflop_action_filled = False


        if len(file_data_change_CTB) >= 3:
            #PREFLOP ACTION
            ## FIX: GET RID OF FIRST IF STATEMENT
            
                
            if file_data_change_CTB[2] != None:
                p.Player.game_state['action_preflop'] = file_data_change_CTB[2]
            

        if len(file_data_change_CTB) == 6:
            #FLOP 
            if p.Player.game_state['flop1'] == '' and p.Player.game_state['flop2'] == '' and p.Player.game_state['flop3'] == '':
                if file_data_change_CTB[3] != None and file_data_change_CTB[4] != None and file_data_change_CTB[5] != None:
                    p.Player.game_state['flop1'] = file_data_change_CTB[3]
                    p.Player.game_state['flop2'] = file_data_change_CTB[4]
                    p.Player.game_state['flop3'] = file_data_change_CTB[5]

        if len(file_data_change_CTB) == 7:
            #FLOP ACTION
            if p.Player.game_state['action_flop'] == '':
                if file_data_change_CTB[6] != None:
                    p.Player.game_state['action_flop'] = file_data_change_CTB[6]


            if file_data_change_CTB[6] != None:
                if file_data_change_CTB[6] == '':
                    is_flop_action_filled = False
                else:
                    is_flop_action_filled = True
            else: 
                is_flop_action_filled = False

        if len(file_data_change_CTB) == 8:
            #TURN 
            if p.Player.game_state['turn'] == '':
                if file_data_change_CTB[7] != None:
                    p.Player.game_state['turn'] = file_data_change_CTB[7]

        if len(file_data_change_CTB) == 9:
            #TURN ACTION 
            if p.Player.game_state['action_turn'] == '':
                if file_data_change_CTB[8] != None:
                    p.Player.game_state['action_turn'] = file_data_change_CTB[8]

            if file_data_change_CTB[8] != None:
                if file_data_change_CTB[8] == '':
                    is_turn_action_filled = False
                else:
                    is_turn_action_filled = True
            else: 
                is_turn_action_filled = False

        if len(file_data_change_CTB) == 10:
            #RIVER 
            if p.Player.game_state['river'] == '':
                if file_data_change_CTB[9] != None:
                    p.Player.game_state['river'] = file_data_change_CTB[9]

        if len(file_data_change_CTB) == 11:
            # DEBUGGING PURPOSES: Included all

            #FLOP 
            if p.Player.game_state['flop1'] == '' and p.Player.game_state['flop2'] == '' and p.Player.game_state['flop3'] == '':
                if file_data_change_CTB[3] != None and file_data_change_CTB[4] != None and file_data_change_CTB[5] != None:
                    p.Player.game_state['flop1'] = file_data_change_CTB[3]
                    p.Player.game_state['flop2'] = file_data_change_CTB[4]
                    p.Player.game_state['flop3'] = file_data_change_CTB[5]

            #FLOP ACTION
            if p.Player.game_state['action_flop'] == '':
                if file_data_change_CTB[6] != None:
                    p.Player.game_state['action_flop'] = file_data_change_CTB[6]

            

           
            #TURN 
            if p.Player.game_state['turn'] == '':
                if file_data_change_CTB[7] != None:
                    p.Player.game_state['turn'] = file_data_change_CTB[7]

        
            #TURN ACTION 
            if p.Player.game_state['action_turn'] == '':
                if file_data_change_CTB[8] != None:
                    p.Player.game_state['action_turn'] = file_data_change_CTB[8]

           

        
            #RIVER 
            if p.Player.game_state['river'] == '':
                if file_data_change_CTB[9] != None:
                    p.Player.game_state['river'] = file_data_change_CTB[9]

            #RIVER ACTION 
            if p.Player.game_state['action_river'] == '':
                if file_data_change_CTB[10] != None:
                    p.Player.game_state['action_river'] = file_data_change_CTB[10]
                
           


            # including preflop, flop and turn for DEBUGGING
            if file_data_change_CTB[2] != None:
                if file_data_change_CTB[2] == '':
                    is_preflop_action_filled = False
                else:
                    is_preflop_action_filled = True
            else: 
                is_preflop_action_filled = False

            if file_data_change_CTB[6] != None:
                if file_data_change_CTB[6] == '':
                    is_flop_action_filled = False
                else:
                    is_flop_action_filled = True
            else: 
                is_flop_action_filled = False

            if file_data_change_CTB[8] != None:
                if file_data_change_CTB[8] == '':
                    is_turn_action_filled = False
                else:
                    is_turn_action_filled = True
            else: 
                is_turn_action_filled = False

            if file_data_change_CTB[10] != None:
                if file_data_change_CTB[10] == '':
                    is_river_action_filled = False
                else:
                    is_river_action_filled = True
            else: 
                is_river_action_filled = False
        
    return is_preflop_action_filled, is_flop_action_filled, is_turn_action_filled, is_river_action_filled

def count_r(my_string):
        count_r = 0
        for letter in my_string:
            if letter == 'r':
                count_r = count_r + 1

        return count_r

def GHB_Parsing(player, GHB_Status):
    
    # GHB_STATUS = <hand number>D<button position>A<holecard1>B<holecard2>
    # cards are 4 * rank + suit where rank is 0 .. 12 for deuce to ace, and suits is 0 .. 3

    #restrict to just give_hand_bot files
    deck_size = 52
    arr = re.split(r'[DAB]',GHB_Status)
    suits = ['h','c','s','d']
    card_a = arr[2] #card from file / REPRESENTS INDEX OF SELF.CARDS
    card_a_suit = ''
    card_a_rank = ''
    card_b = arr[3] #card from file / REPRESENTS INDEX OF SELF.CARDS
    card_b_suit = ''
    card_b_rank = ''
    a,b,c,x,y,z = ('', '', '', '', '', '')
    for card in player.cards:
        if(str(player.cards.index(card)) == card_a):
            if(len(card) == 2):
                a,b = card
            # elif(len(card) == 3):
            #     a,b,c = card
            #     a = a+b
            #     b = c
        elif(str(player.cards.index(card))== card_b):
            if(len(card) == 2):
                x,y = card
            elif(len(card) == 3):
                x,y,z = card
                x = x+y
                y = z
    card_a_rank = a
    card_a_suit = b
    card_b_rank = x
    card_b_suit = y
    player.card_holding =   p.CardHolding(player.name,card_a_suit,card_a_rank,card_b_suit, card_b_rank)
    
    return player.card_holding

def from_num_to_cardstring(my_card):
  
    deck_size = 52
    suits = ['h','c','s','d']
    
    card_a_suit = ''
    card_a_rank = ''
    a,b = ('', '')
    cards_for_game = create_cards_for_game()
    for card in cards_for_game: ## all cards in game
        if(str(cards_for_game.index(card)) == my_card):
            if(len(card) == 2):
                a,b = card
                break
    card_a_rank = a
    card_a_suit = b
    
       
    return str(a+b)