
# Imports helper functions
from kaggle_environments.envs.halite.helpers import *

''' GLOBAL VARIABLES '''
# General
penalty_rate = -100000
chase_ship_rate = 200
convert_reward = 5000
nearby_halite = 1000
min_halite_for_conversion = 2000

# Rewards for surrounding halite
big_os_reward = 1000
big_ts_reward = 500
big_ths_reward = 250
big_fs_reward = 125
little_os_reward = 125
little_ts_reward = 100
little_ths_reward = 50
little_fs_reward = 25
min_os_reward = 4
min_ts_reward = 3
min_ths_reward = 2
min_fs_reward = 1

# FUNCTIONS
def findOpponentShips(board):
    opp_ship_locations = {}
    for opponent in board.opponents:
        for opp_ship in opponent.ships:
            opp_ship_locations[opp_ship.id] = opp_ship.position
    return opp_ship_locations

def defineRewardSet():
    reward_set = {}
    reward_set['north'] = 0
    reward_set['south'] = 0
    reward_set['east'] = 0
    reward_set['west'] = 0
    reward_set['convert'] = 0
    return reward_set

def checkShipPrevLocation(ship, reward_set, board, ship_prev_location):
    if ship.cell.north.position == ship_prev_location[ship.id]:
        reward_set['north'] += penalty_rate
    if ship.cell.south.position == ship_prev_location[ship.id]:
        reward_set['south'] += penalty_rate
    if ship.cell.east.position == ship_prev_location[ship.id]:
        reward_set['east'] += penalty_rate
    if ship.cell.west.position == ship_prev_location[ship.id]:
        reward_set['west'] += penalty_rate
    return reward_set

def checkMyShipCollisions(ship, my_ships, reward_set, ship_locations, board):
    if ship.cell.north.ship_id == my_ships.id and my_ships.next_action is None:
        reward_set['north'] += penalty_rate
    if ship.cell.north.position in ship_locations.values():
        reward_set['north'] += penalty_rate
    if ship.cell.south.ship_id == my_ships.id and my_ships.next_action is None:
        reward_set['south'] += penalty_rate
    if ship.cell.south.position in ship_locations.values():
        reward_set['south'] += penalty_rate
    if ship.cell.east.ship_id == my_ships.id and my_ships.next_action is None:
        reward_set['east'] += penalty_rate
    if ship.cell.east.position in ship_locations.values():
        reward_set['east'] += penalty_rate
    if ship.cell.west.ship_id == my_ships.id and my_ships.next_action is None:
        reward_set['west'] += penalty_rate
    if ship.cell.west.position in ship_locations.values():
        reward_set['west'] += penalty_rate
    return reward_set

def checkEnemyShipCollisions(ship, opp_ships, reward_set, board, ship_state):
    # check if opponent ship is adjacent to ship
    if opp_ships.position == ship.cell.north.position:
        if opp_ships.halite <= ship.halite:
            reward_set['north'] += penalty_rate
        else:
            reward_set['north'] += chase_ship_rate
    if opp_ships.position == ship.cell.south.position:
        if opp_ships.halite <= ship.halite:
            reward_set['south'] += penalty_rate
        else:
            reward_set['south'] += chase_ship_rate
    if opp_ships.position == ship.cell.east.position:
        if opp_ships.halite <= ship.halite:
            reward_set['east'] += penalty_rate
        else:
            reward_set['east'] += chase_ship_rate
    if opp_ships.position == ship.cell.west.position:
        if opp_ships.halite <= ship.halite:
            reward_set['west'] += penalty_rate
        else:
            reward_set['west'] += chase_ship_rate
    
    # Check if opponent ship can move to square where my ship is
    if opp_ships.cell.south.position == ship.cell.north.position:
        if opp_ships.halite <= ship.halite:
            reward_set['north'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['north'] += chase_ship_rate
    if opp_ships.cell.east.position == ship.cell.north.position:
        if opp_ships.halite <= ship.halite:
            reward_set['north'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['north'] += chase_ship_rate
    if opp_ships.cell.west.position == ship.cell.north.position:
        if opp_ships.halite <= ship.halite:
            reward_set['north'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['north'] += chase_ship_rate
    if opp_ships.cell.north.position == ship.cell.south.position:
        if opp_ships.halite <= ship.halite:
            reward_set['south'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['south'] += chase_ship_rate
    if opp_ships.cell.east.position == ship.cell.south.position:
        if opp_ships.halite <= ship.halite:
            reward_set['south'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['south'] += chase_ship_rate
    if opp_ships.cell.west.position == ship.cell.south.position:
        if opp_ships.halite <= ship.halite:
            reward_set['south'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['south'] += chase_ship_rate
    if opp_ships.cell.south.position == ship.cell.east.position:
        if opp_ships.halite <= ship.halite:
            reward_set['east'] += penalty_rate
    if opp_ships.cell.north.position == ship.cell.east.position:
        if opp_ships.halite <= ship.halite:
            reward_set['east'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['east'] += chase_ship_rate
    if opp_ships.cell.west.position == ship.cell.east.position:
        if opp_ships.halite <= ship.halite:
            reward_set['east'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['east'] += chase_ship_rate
    if opp_ships.cell.south.position == ship.cell.west.position:
        if opp_ships.halite <= ship.halite:
            reward_set['west'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['west'] += chase_ship_rate
    if opp_ships.cell.east.position == ship.cell.west.position:
        if opp_ships.halite <= ship.halite:
            reward_set['west'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['west'] += chase_ship_rate
    if opp_ships.cell.north.position == ship.cell.west.position:
        if opp_ships.halite <= ship.halite:
            reward_set['west'] += penalty_rate
        elif ship_state == 'ATTACK':
            reward_set['west'] += chase_ship_rate
    return reward_set

def checkEnemyShipyardCollisions(ship, opp_sy, reward_set, board):
    if opp_sy.position == ship.cell.north.position:
        reward_set['north'] += penalty_rate
    if opp_sy.position == ship.cell.south.position:
        reward_set['south'] += penalty_rate
    if opp_sy.position == ship.cell.east.position:
        reward_set['east'] += penalty_rate
    if opp_sy.position == ship.cell.west.position:
        reward_set['west'] += penalty_rate
    return reward_set

def oneStepLookAheadHalite(reward_set, nh, sh, eh, wh):
    if nh == max(nh, sh, eh, wh) and nh > 300:
        reward_set['north'] += big_os_reward
    if sh == max(nh, sh, eh, wh) and sh > 300:
        reward_set['south'] += big_os_reward
    if eh == max(nh, sh, eh, wh) and eh > 300:
        reward_set['east'] += big_os_reward
    if wh == max(nh, sh, eh, wh) and wh > 300:
        reward_set['west'] += big_os_reward
    if nh == max(nh, sh, eh, wh) and nh > 100:
        reward_set['north'] += little_os_reward
    if sh == max(nh, sh, eh, wh) and sh > 100:
        reward_set['south'] += little_os_reward
    if eh == max(nh, sh, eh, wh) and eh > 100:
        reward_set['east'] += little_os_reward
    if wh == max(nh, sh, eh, wh) and wh > 100:
        reward_set['west'] += little_os_reward
    if nh == max(nh, sh, eh, wh):
        reward_set['north'] += min_os_reward
    if sh == max(nh, sh, eh, wh):
        reward_set['south'] += min_os_reward
    if eh == max(nh, sh, eh, wh):
        reward_set['east'] += min_os_reward
    if wh == max(nh, sh, eh, wh):
        reward_set['west'] += min_os_reward
    return reward_set

def twoStepLookAheadHalite(reward_set, nh, sh, eh, wh, nnh, ssh, eeh, wwh, nwh, neh, swh, seh):
    if (nh + nnh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (nh + nnh) > 500:
        reward_set['north'] += big_ts_reward
    if (sh + ssh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (sh + ssh) > 500:
        reward_set['south'] += big_ts_reward
    if (eh + eeh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (eh + eeh) > 500:
        reward_set['east'] += big_ts_reward
    if (wh + wwh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (wh + wwh) > 500:
        reward_set['west'] += big_ts_reward
    if (nh + nnh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (nh + nnh) > 200:
        reward_set['north'] += little_ts_reward
    if (sh + ssh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (sh + ssh) > 200:
        reward_set['south'] += little_ts_reward
    if (eh + eeh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (eh + eeh) > 200:
        reward_set['east'] += little_ts_reward
    if (wh + wwh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh) and (wh + wwh) > 200:
        reward_set['west'] += little_ts_reward
    if (nh + nnh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh):
        reward_set['north'] += min_ts_reward
    if (sh + ssh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh):
        reward_set['south'] += min_ts_reward
    if (eh + eeh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh):
        reward_set['east'] += min_ts_reward
    if (wh + wwh) == max(nh + nnh, sh + ssh, eh + eeh, wh + wwh):
        reward_set['west'] += min_ts_reward
    return reward_set

def threeStepLookAheadHalite(reward_set, nh, sh, eh, wh, nnh, ssh, eeh, wwh, nnnh, sssh, eeeh, wwwh):
    if (nh+nnh+nnnh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (nh+nnh+nnnh) > 800:
        reward_set['north'] += big_ths_reward
    if (sh+ssh+sssh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (sh+ssh+sssh) > 800:
        reward_set['south'] += big_ths_reward
    if (eh+eeh+eeeh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (eh+eeh+eeeh) > 800:
        reward_set['east'] += big_ths_reward
    if (wh+wwh+wwwh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (wh+wwh+wwwh) > 800:
        reward_set['west'] += big_ths_reward
    if (nh+nnh+nnnh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (nh+nnh+nnnh) > 400:
        reward_set['north'] += little_ths_reward
    if (sh+ssh+sssh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (sh+ssh+sssh) > 400:
        reward_set['south'] += little_ths_reward
    if (eh+eeh+eeeh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (eh+eeh+eeeh) > 400:
        reward_set['east'] += little_ths_reward
    if (wh+wwh+wwwh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh) and (wh+wwh+wwwh) > 400:
        reward_set['west'] += little_ths_reward
    if (nh+nnh+nnnh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh):
        reward_set['north'] += min_ths_reward
    if (sh+ssh+sssh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh):
        reward_set['south'] += min_ths_reward
    if (eh+eeh+eeeh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh):
        reward_set['east'] += min_ths_reward
    if (wh+wwh+wwwh) == max(nh+nnh+nnnh,sh+ssh+sssh,eh+eeh+eeeh,wh+wwh+wwwh):
        reward_set['west'] += min_ths_reward
    return reward_set

def fourStepLookAheadHalite(reward_set, nh, sh, eh, wh, nnh, ssh, eeh, wwh, nnnh, sssh, eeeh, wwwh, \
                            n4h, s4h, e4h, w4h):
    if (nh+nnh+nnnh+n4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (nh+nnh+nnnh+n4h) > 1100:
        reward_set['north'] += big_fs_reward
    if (sh+ssh+sssh+s4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (sh+ssh+sssh+s4h) > 1100:
        reward_set['south'] += big_fs_reward
    if (eh+eeh+eeeh+e4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (eh+eeh+eeeh+e4h) > 1100:
        reward_set['east'] += big_fs_reward
    if (wh+wwh+wwwh+w4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (wh+wwh+wwwh+w4h) > 1100:
        reward_set['west'] += big_fs_reward
    if (nh+nnh+nnnh+n4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (nh+nnh+nnnh+n4h) > 600:
        reward_set['north'] += little_fs_reward
    if (sh+ssh+sssh+s4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (sh+ssh+sssh+s4h) > 600:
        reward_set['south'] += little_fs_reward
    if (eh+eeh+eeeh+e4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (eh+eeh+eeeh+e4h) > 600:
        reward_set['east'] += little_fs_reward
    if (wh+wwh+wwwh+w4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h) and (wh+wwh+wwwh+w4h) > 600:
        reward_set['west'] += little_fs_reward
    if (nh+nnh+nnnh+n4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h):
        reward_set['north'] += min_fs_reward
    if (sh+ssh+sssh+s4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h):
        reward_set['south'] += min_fs_reward
    if (eh+eeh+eeeh+e4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h):
        reward_set['east'] += min_fs_reward
    if (wh+wwh+wwwh+w4h) == max(nh+nnh+nnnh+n4h,sh+ssh+sssh+s4h,eh+eeh+eeeh+e4h,wh+wwh+wwwh+w4h):
        reward_set['west'] += min_fs_reward
    return reward_set

def closestShipyard(ship, size, me, board, my_shipyard = True):
    fromX, fromY = divmod(ship.position[0],size), divmod(ship.position[1],size)
    target_shipyard = None
    shortest_steps = size*2
    if my_shipyard:
        for sy in me.shipyards:
            toX, toY = divmod(sy.position[0],size), divmod(sy.position[1],size)
            change_x = toX[1] - fromX[1]
            change_y = toY[1] - fromY[1]
            if abs(change_x) <= size // 2:
                step_x = abs(change_x)
            else:
                if change_x > 0:
                    step_x = abs(change_x - size)
                elif change_x < 0:
                    step_x = abs(change_x + size)
            if abs(change_y) <= size // 2:
                step_y = abs(change_y)
            else:
                if change_y > 0:
                    step_y = abs(change_y - size)
                elif change_y < 0:
                    step_y = abs(change_y + size)

            steps = step_x + step_y

            if (steps < shortest_steps):
                shortest_steps = steps
                target_shipyard = sy
    else:
        for opp in board.opponents:
            for opp_sy in opp.shipyards:
                toX, toY = divmod(opp_sy.position[0],size), divmod(opp_sy.position[1],size)
                change_x = toX[1] - fromX[1]
                change_y = toY[1] - fromY[1]
                if abs(change_x) <= size // 2:
                    step_x = abs(change_x)
                else:
                    if change_x > 0:
                        step_x = abs(change_x - size)
                    elif change_x < 0:
                        step_x = abs(change_x + size)
                if abs(change_y) <= size // 2:
                    step_y = abs(change_y)
                else:
                    if change_y > 0:
                        step_y = abs(change_y - size)
                    elif change_y < 0:
                        step_y = abs(change_y + size)

                steps = step_x + step_y

                if (steps < shortest_steps):
                    shortest_steps = steps
                    target_shipyard = opp_sy
    return target_shipyard

def closestShipyardDirection(ship, board, size, target_shipyard, reward_set):
    fromX, fromY = divmod(ship.position[0],size), divmod(ship.position[1],size)
    toX, toY = divmod(target_shipyard.position[0],size), divmod(target_shipyard.position[1],size)
    if fromY < toY:
        reward_set['north'] += 500
    if fromY > toY:
        reward_set['south'] += 500
    if fromX < toX:
        reward_set['east'] += 500
    if fromX > toX:
        reward_set['west'] += 500
    return reward_set

# Directions a ship can move
directions = [ShipAction.NORTH, ShipAction.EAST, ShipAction.SOUTH, ShipAction.WEST]

# Will keep track of whether a ship is collecting halite or carrying cargo to a shipyard
ship_states = {}

# Keep track of ship locations
ship_locations = {}

# Keep track of ship previous location
ship_prev_location = {}

# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player
    
    active_ships = []
    remove_list = []
    for ship in me.ships:
        active_ships.append(ship.id)
    for location in ship_locations:
        if location not in active_ships:
            remove_list.append(location)
    for removable in remove_list:
        ship_locations.pop(removable)

    # If there are less than 3 ships, use first shipyard to spawn a ship.
    if len(me.ships) < 3 and len(me.shipyards) > 0:
        best_halite = 0
        chosen_sy = me.shipyards[0]
        for sy in me.shipyards:
            surrounding_halite = sy.cell.north.halite + sy.cell.south.halite + sy.cell.east.halite + sy.cell.west.halite + \
            sy.cell.north.north.halite + sy.cell.south.south.halite + sy.cell.east.east.halite + sy.cell.west.west.halite
            if surrounding_halite >= best_halite and sy.position not in ship_locations.values():
                best_halite = surrounding_halite
                chosen_sy = sy
        chosen_sy.next_action = ShipyardAction.SPAWN

    # If there are no shipyards, convert first ship into shipyard.
    if len(me.shipyards) == 0 and len(me.ships) > 0:
        least_halite = me.ships[0].halite
        for ships in me.ships:
            if ships.halite <= least_halite:
                least_halite = ships.halite
                chosen_ship = ships
        if chosen_ship.id in ship_locations:
            ship_locations.pop(chosen_ship.id)
        chosen_ship.next_action = ShipAction.CONVERT
    
    opp_shipyards = []
    for opp in board.opponents:
        for opp_sy in opp.shipyards:
            opp_shipyards.append(opp_sy.id)
    
    for ship in me.ships:
        # easily reference cells around ship
        # one move away
        nh = ship.cell.north.halite
        sh = ship.cell.south.halite
        eh = ship.cell.east.halite
        wh = ship.cell.west.halite
        ch = ship.cell.halite
        # two moves away
        nnh = ship.cell.north.north.halite
        neh = ship.cell.north.east.halite
        nwh = ship.cell.north.west.halite
        ssh = ship.cell.south.south.halite
        seh = ship.cell.south.east.halite
        swh = ship.cell.south.west.halite
        eeh = ship.cell.east.east.halite
        wwh = ship.cell.west.west.halite
        # three moves away
        nnnh = ship.cell.north.north.north.halite
        sssh = ship.cell.south.south.south.halite
        eeeh = ship.cell.east.east.east.halite
        wwwh = ship.cell.west.west.west.halite
        # four moves away
        n4h = ship.cell.north.north.north.north.halite
        s4h = ship.cell.south.south.south.south.halite
        e4h = ship.cell.east.east.east.east.halite
        w4h = ship.cell.west.west.west.west.halite
        
        if ship.next_action == None:
               
            ### Part 1: Set the ship's state
            if ship.halite < 500:
                ship_states[ship.id] = "COLLECT"
            if len(me.ships) == 3 and ship.id == me.ships[0].id and me.halite >= 2000 and len(opp_shipyards) > 0:
                ship_states[ship.id] = "ATTACK"
            if ship.halite >= 500 and ship.cell.halite <= 100 and len(me.shipyards) > 0:
                ship_states[ship.id] = "DEPOSIT"
                
            ### Part 2: Use the ship's state to select an action
            
            ''' CODE FOR COLLECTING SHIPS '''
            
            if ship_states[ship.id] == "COLLECT":
                
                opp_ship_locations = findOpponentShips(board)
                
                if ship.cell.halite < 100:
                    # define reward set and apply penalty for collisions
                    reward_set = defineRewardSet()
                    if ship.id in ship_prev_location:
                        reward_set = checkShipPrevLocation(ship, reward_set, board, ship_prev_location)
                    for my_ships in me.ships:
                        reward_set = checkMyShipCollisions(ship, my_ships, reward_set, ship_locations, board)
                    for opponent in board.opponents:
                        for opp_ships in opponent.ships:
                            reward_set = checkEnemyShipCollisions(ship, opp_ships, reward_set, board, ship_states[ship.id])      
                        for opp_sy in opponent.shipyards:
                            reward_set = checkEnemyShipyardCollisions(ship, opp_sy, reward_set, board)
                            
                    # rewards for moving in each direction
                    reward_set = oneStepLookAheadHalite(reward_set, nh, sh, eh, wh)
                    reward_set = twoStepLookAheadHalite(reward_set, nh, sh, eh, wh, \
                                                       nnh, ssh, eeh, wwh, \
                                                       nwh, neh, swh, seh)
                    reward_set = threeStepLookAheadHalite(reward_set, nh, sh, eh, wh, \
                                                          nnh, ssh, eeh, wwh, \
                                                          nnnh, sssh, eeeh, wwwh)
                    reward_set = fourStepLookAheadHalite(reward_set, nh, sh, eh, wh, \
                                                         nnh, ssh, eeh, wwh, \
                                                         nnnh, sssh, eeeh, wwwh, \
                                                         n4h, s4h, e4h, w4h)
                    
                    # should ship convert to shipyard
                    if (nh+nnh+nnnh+sh+ssh+sssh+eh+eeh+eeeh+wh+wwh+wwwh) > nearby_halite and len(me.shipyards) > 0 and me.halite > min_halite_for_conversion:
                        fromX, fromY = ship.position[0], ship.position[1]
                        to_first_sy_x, to_first_sy_y = me.shipyards[0].position[0], me.shipyards[0].position[1]
                        min_sy_distance_away = abs(fromX - to_first_sy_x) + abs(fromY - to_first_sy_y)
                        for sy in me.shipyards:
                            toX, toY = sy.position[0], sy.position[1]
                            x_distance = abs(fromX - toX)
                            y_distance = abs(fromY - toY)
                            if x_distance + y_distance < min_sy_distance_away:
                                min_sy_distance_away = x_distance + y_distance
                        if min_sy_distance_away > 4:
                            reward_set['convert'] += convert_reward
                        
                    # allocate best direction to move
                    chosen_direction = max(reward_set, key = reward_set.get)
                    if chosen_direction == 'north':
                        ship.next_action = directions[0]
                        ship_locations[ship.id] = ship.cell.north.position
                        ship_prev_location[ship.id] = ship.cell.position
                    if chosen_direction == 'south':
                        ship.next_action = directions[2]
                        ship_locations[ship.id] = ship.cell.south.position
                        ship_prev_location[ship.id] = ship.cell.position
                    if chosen_direction == 'east':
                        ship.next_action = directions[1]
                        ship_locations[ship.id] = ship.cell.east.position
                        ship_prev_location[ship.id] = ship.cell.position
                    if chosen_direction == 'west':
                        ship.next_action = directions[3]
                        ship_locations[ship.id] = ship.cell.west.position
                        ship_prev_location[ship.id] = ship.cell.position
                    if chosen_direction == 'convert':
                        if ship.id in ship_locations:
                            ship_locations.pop(ship.id)
                        ship.next_action = ShipAction.CONVERT

                elif ship.cell.halite >= 100 and (ship.cell.north.position in opp_ship_locations.values() or \
                                                  ship.cell.south.position in opp_ship_locations.values() or \
                                                  ship.cell.east.position in opp_ship_locations.values() or \
                                                  ship.cell.west.position in opp_ship_locations.values()):

                    # define reward set and apply penalty for collisions
                    reward_set = defineRewardSet()
                    reward_set = checkShipPrevLocation(ship, reward_set, board, ship_prev_location)
                    for my_ships in me.ships:
                        reward_set = checkMyShipCollisions(ship, my_ships, reward_set, ship_locations, board)
                    for opponent in board.opponents:
                        for opp_ships in opponent.ships:
                            reward_set = checkEnemyShipCollisions(ship, opp_ships, reward_set, board, ship_states[ship.id])
                        for opp_sy in opponent.shipyards:
                            reward_set = checkEnemyShipyardCollisions(ship, opp_sy, reward_set, board)
                    
                    # rewards for moving in each direction
                    reward_set = oneStepLookAheadHalite(reward_set, nh, sh, eh, wh)
                    reward_set = twoStepLookAheadHalite(reward_set, nh, sh, eh, wh, \
                                                       nnh, ssh, eeh, wwh, \
                                                       nwh, neh, swh, seh)
                    reward_set = threeStepLookAheadHalite(reward_set, nh, sh, eh, wh, \
                                                          nnh, ssh, eeh, wwh, \
                                                          nnnh, sssh, eeeh, wwwh)
                    reward_set = fourStepLookAheadHalite(reward_set, nh, sh, eh, wh, \
                                                         nnh, ssh, eeh, wwh, \
                                                         nnnh, sssh, eeeh, wwwh, \
                                                         n4h, s4h, e4h, w4h)
                    
                    # allocate best direction to move
                    chosen_direction = max(reward_set, key = reward_set.get)
                    if chosen_direction == 'north':
                        ship.next_action = directions[0]
                        ship_locations[ship.id] = ship.cell.north.position
                        ship_prev_location[ship.id] = ship.cell.position
                    if chosen_direction == 'south':
                        ship.next_action = directions[2]
                        ship_locations[ship.id] = ship.cell.south.position
                        ship_prev_location[ship.id] = ship.cell.position
                    if chosen_direction == 'east':
                        ship.next_action = directions[1]
                        ship_locations[ship.id] = ship.cell.east.position
                        ship_prev_location[ship.id] = ship.cell.position
                    if chosen_direction == 'west':
                        ship.next_action = directions[3]
                        ship_locations[ship.id] = ship.cell.west.position
                        ship_prev_location[ship.id] = ship.cell.position
            
            ''' CODE FOR DEPOSITING SHIPS '''
            
            if ship_states[ship.id] == "DEPOSIT":
                # Define reward set and apply penalties for unwanted collisions
                reward_set = defineRewardSet()
                reward_set = checkShipPrevLocation(ship, reward_set, board, ship_prev_location)
                for my_ships in me.ships:
                    reward_set = checkMyShipCollisions(ship, my_ships, reward_set, ship_locations, board)
                for opponent in board.opponents:
                    for opp_ships in opponent.ships:
                        reward_set = checkEnemyShipCollisions(ship, opp_ships, reward_set, board, ship_states[ship.id])          
                    for opp_sy in opponent.shipyards:
                        reward_set = checkEnemyShipyardCollisions(ship, opp_sy, reward_set, board)                
                
                # Locate closest shipyard to deposit
                target_shipyard = closestShipyard(ship, size, me, board)
                if len(me.shipyards) > 0:
                    reward_set = closestShipyardDirection(ship, board, size, target_shipyard, reward_set)
                     
                chosen_direction = max(reward_set, key = reward_set.get)
                if chosen_direction == 'north':
                    ship.next_action = directions[0]
                    ship_locations[ship.id] = ship.cell.north.position
                    ship_prev_location[ship.id] = ship.cell.position
                if chosen_direction == 'south':
                    ship.next_action = directions[2]
                    ship_locations[ship.id] = ship.cell.south.position
                    ship_prev_location[ship.id] = ship.cell.position
                if chosen_direction == 'east':
                    ship.next_action = directions[1]
                    ship_locations[ship.id] = ship.cell.east.position
                    ship_prev_location[ship.id] = ship.cell.position
                if chosen_direction == 'west':
                    ship.next_action = directions[3]
                    ship_locations[ship.id] = ship.cell.west.position
                    ship_prev_location[ship.id] = ship.cell.position
            
            ''' CODE FOR ATTACKING SHIPS '''
            
            if ship_states[ship.id] == "ATTACK":
                # Define reward set and apply penalty for collisions
                reward_set = defineRewardSet()
                reward_set = checkShipPrevLocation(ship, reward_set, board, ship_prev_location)
                for my_ships in me.ships:
                    reward_set = checkMyShipCollisions(ship, my_ships, reward_set, ship_locations, board)
                for opponent in board.opponents:
                    for opp_ships in opponent.ships:
                        reward_set = checkEnemyShipCollisions(ship, opp_ships, reward_set, board, ship_states[ship.id])
                
                target_shipyard = closestShipyard(ship, size, me, board, False)
                
                total_opp_sy = 0
                for opp in board.opponents:
                    for opp_sy in opp.shipyards:
                        total_opp_sy += 1
                if total_opp_sy > 0:
                    reward_set = closestShipyardDirection(ship, board, size, target_shipyard, reward_set)
                    
                chosen_direction = max(reward_set, key = reward_set.get)
                if chosen_direction == 'north':
                    ship.next_action = directions[0]
                    ship_locations[ship.id] = ship.cell.north.position
                if chosen_direction == 'south':
                    ship.next_action = directions[2]
                    ship_locations[ship.id] = ship.cell.south.position
                if chosen_direction == 'east':
                    ship.next_action = directions[1]
                    ship_locations[ship.id] = ship.cell.east.position
                if chosen_direction == 'west':
                    ship.next_action = directions[3]
                    ship_locations[ship.id] = ship.cell.west.position
                
    return me.next_actions
