import re 
import Player as p_file
import numpy as np
def create_cards_for_game(self):
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

def casinoToBot_Parsing(self, file_data, plr, player_list):
    # <hand number> D <dealer button position> P <action by all players in order from first to 
    # act, e.g. fccrf...> F <flop card 1> F <flop 2> F <flop 3> F <flop action starting with first player to act>
    # T <turn card> T <turn action> R <river card> R <river action>

    arr =  re.split(r'[DPFFFFTTRR]',file_data)

    if arr[0] != None:
        plr.hand_num = arr[0]
   
    if arr[1] != None:
        for i in range(len(player_list)):
            if str(arr[1]) == str(i):
                player_list[i].dealer_status = True
                player_list[i].position = "SB"
            else: 
                player_list[i].dealer_status = False
                player_list[i].position = "BB"
            

    # dictionary = {"hand_num" : arr[0],
    #             "button" : arr[1] ,
    #             "preflop_action" : arr[2],
    #             "flop_card_1" : arr[3] ,
    #             "flop_card_2" : arr[4],
    #             "flop_card_3" : arr[5] ,
    #             "flop_action" : arr[6] ,
    #             "turn_card" : arr[7],
    #             "turn_action" : arr[8],
    #             "river_card" : arr[9],
    #             "river_action" : arr[10]}


    return arr

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
    player.card_holding =   p_file.CardHolding(player.name,card_a_suit,card_a_rank,card_b_suit, card_b_rank)
    
    return player.card_holding