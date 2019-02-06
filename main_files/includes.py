limit = 2

#preflop ranges (Dealer moves last)
# {action: {facing_raises_debt: {bot_position: { 
preflop_range = {"betting": 
                    {
                        0: #facing_raises_debt (in this round)
                            {
                                0: 7000,
                                1 : 5000,
                                2 : 6000
                            }
                        ,
                        1: #facing_raises_debt (in this round)
                            {
                                0: 6000, 
                                1 : 4000,
                                2 : 5000
                            }
                        ,
                        2: #facing_raises_debt (in this round)
                            {
                                0: 5000,
                                1 : 3500,
                                2 : 4200
                            }
                        
                        # cannot face more than 2 raises
                    },
                 "calling": # more like to open range wider for calling having already seen all players just checking/calling before
                    {
                        0: #facing_calls (in this round) - first to act
                            {
                                0: 6000,
                                1 : 5500,
                                2 : 5000
                            }
                        ,
                        1: #facing_calls (in this round)
                            {
                                0: 8000, 
                                1 : 6000,
                                2 : 7000
                            }
                        ,
                        2: #facing_calls (in this round)
                            {
                                0: 10000,
                                1 : 10000,
                                2 : 10000
                            }
                        
                        # cannot face more than 2 raises
                    }
                }


#flop ranges (Dealer moves first)
postflop_range_upper_truedealer = 4000
postflop_range_lower_notdealer =  4500
