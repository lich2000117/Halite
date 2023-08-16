from kaggle_environments.envs.halite.helpers import *
import kaggle_environments
import random

#########
### Remove All Prints
#### Cap:250, Window Size:5


#### Set one point to go
ship_dest = {}
size=None

#### Set no_movement_counter 
no_movement_counter = 0
#me=None

### my own observation
class Obj:
  pass

my_obs = Obj()

### setup attack_ship_id
attack_ship_id = []
target_player_id = 1

  
    
# Returns best direction to move from one position (fromPos) to another (toPos)
# Example: If I'm at pos 0 and want to get to pos 55, which direction should I choose?
def getDirTo(fromPos, toPos, size=21):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    dX, dY= toPos - fromPos
    man_dist = abs(dX) + abs(dY)
    if fromY < toY: return [ShipAction.NORTH], (dX, dY), man_dist
    if fromY > toY: return [ShipAction.SOUTH], (dX, dY), man_dist
    if fromX < toX: return [ShipAction.EAST], (dX, dY), man_dist
    if fromX > toX: return [ShipAction.WEST], (dX, dY), man_dist
    if (fromY == toY) and (fromX == toX): return [None], (dX, dY), man_dist
    
def getDirTo_simple(fromPos, toPos, size=21):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    dX, dY= toPos - fromPos
    man_dist = abs(dX) + abs(dY)
    if fromY < toY: return ShipAction.NORTH
    if fromY > toY: return ShipAction.SOUTH
    if fromX < toX: return ShipAction.EAST
    if fromX > toX: return ShipAction.WEST
    if (fromY == toY) and (fromX == toX): return None
    

def my_obs(board):
    
    times = 0
    step_e = 0 
    step_list = []

    times = 300 // interval
    for i in range(1,times+1):
        step_e = i * interval
        step_list.append(step_e)
    
    if (((board.step +1) in step_list) and (me.halite >= 1500)) or ((board.step > 120 and board.step<285) and (me.halite >= 1500)):
        my_obs.max_ships = 3             
    else: my_obs.max_ships = 2
    #my_obs.max_ships = 3
    my_obs.ship_num = len(me.ships)
    my_obs.shipyard_num = len(me.shipyards)
    my_obs.not_available = {}
    my_obs.total_halite = me.halite
      

## Find the best nearby cell with max halite       
def find_best_cell(board,my_loc, my_ship_id, my_other_ship_id, window_size = 5):
    best_halite = -1
    if len(my_other_ship_id)!=0 and (my_other_ship_id in ship_dest):
        for p,c in board.cells.items():
            #assert isinstance(p,Point)
            #print('my_other_ship_id is {}'.format(my_other_ship_id))
            #print('choose max halite while considering ship_dest[my_other_ship_id]:{}'.format(ship_dest[my_other_ship_id]))
            ######## Add one % to control the next best cell
            if (c.halite > (best_halite * 1.05)) and (p not in ship_dest[my_other_ship_id]) and (abs(my_loc.x - p.x)< window_size) and (abs(my_loc.y - p.y) < window_size) and (p not in ship_dest):
                best_halite = c.halite
                #print('current cell halite is {}'.format(c.halite))
                best_cell = c
                best_point = p
    else:
        for p,c in board.cells.items():
            if c.halite > best_halite and (abs(my_loc.x - p.x)< window_size) and (abs(my_loc.y - p.y) < window_size) and (p not in ship_dest):
                best_halite = c.halite
                #print('current cell halite is {}'.format(c.halite))
                best_cell = c
                best_point = p
    return best_point, best_cell.halite

def ship_actions(board):
    ships=[ship for ship in me.ships if ship.next_action == None]
    #########BUG: if two ships know where to go, then they are not in 'ships'
    #choose destinations for all ships
    choose_dest(ships, board)
    #print(ship_dest)
    
    actions = {}
    for ship in ships:
        if ship.id in ship_dest:
            a, d, man_dist = getDirTo(ship.position, ship_dest[ship.id], size)
            actions[ship.id] = a
        else:
            actions[ship.id] = None
            
    #print('REFRESH not available dic by getting current ship locations')
    for ship in ships:
        my_obs.not_available[ship.position] = 1
    #print('REFRESH not available - current ships at {}'.format(my_obs.not_available))
        
            
    for ship in ships:
        action = None
        ship_current_position = ship.position
        
        #print('##This is ship {}##\n'.format(ship.id))
        #print('ship_current_position is {}, ship_dest is {}'.format(ship_current_position,ship_dest[ship.id]))
        #print('MY HATILE IS {}'.format(ship.halite))
        if ship_current_position != ship_dest[ship.id]:
            ship_all_action = actions[ship.id]
            #print("all actions for this ship is {}".format(ship_all_action))

            for action in ship_all_action:
                step = steps(ship_current_position,action,)
                #print("The next possible step is: {}".format(step))
            ### add logic if this step is valid or not
            #######################
                #print('not_available is currently at:{}\n'.format(my_obs.not_available))
                if step not in my_obs.not_available:
                    #print('my next step would be {} but will add it to not_available'.format(step))
                    ship.next_action = action
                    my_obs.not_available[step] = 1 ###### CHECK THIS
                    #print('UPDATE: not_available has been updated to {} in this turn'.format(my_obs.not_available))
                else: #### CHOOSE A RANDOM VALID MOVE
                    all_random_actions=[ShipAction.NORTH, ShipAction.EAST,ShipAction.SOUTH,ShipAction.WEST]
                    valid_random = random.choice(all_random_actions)
                    random_step = steps(ship_current_position,valid_random,)
                    if random_step not in my_obs.not_available:
                            ship.next_action = valid_random
                    else: ship.next_action = None
            
            #print("The confirmed next step of ship {}\n".format(ship.next_action))
        else:
            #print("I AM THERE!")
            my_obs.not_available[ship_current_position] = 1
            #print('since I am mining here. the not available place is updated to {}'.format(my_obs.not_available))
            
#         if ship.halite > 250: #### Set-up a smaller value
#             # Move towards shipyard to deposit cargo
#             print("I AM GOING HOME TO DEPOSIT {}".format(ship.halite))
#             direction = getDirTo_simple(ship.position, me.shipyards[0].position, size)
#             print("My deposit direction is {}".format(direction))
#             deposit_step = steps(ship_current_position,direction,)
#             print("My deposit_step is {}".format(deposit_step))
#             if (deposit_step not in my_obs.not_available) and direction:
#                 print('my deposit_step is {}'.format(deposit_step))
#                 print('my obs not available is {}'.format(my_obs.not_available))
#                 ship.next_action = direction
#                 my_obs.not_available[deposit_step] = 1
#                 print('Be careful, I am on my way to depoit, avoid {}'.format(my_obs.not_available))
          
     #### Special Patching 1 ####### If two ships potentail destiations and current locations are overlapped
     ## If all ship's actions are none and one of the ship's location is another ships destionation, let one ship move randomly
    
    ###### ##### know_where_to_go_ships=[ship for ship in me.ships if ship.next_action != None]
   
        
    
    
def choose_dest(ships, board):
    #choose a destination for my ships
    #could be halite position, enemy base or random move
    #print(board)
    #print(len(ships))
    ship_dest.clear()
    #print('how many ships {}'.format(len(ships)))   
    if len(ships)==0:
        return
    fix_point = Point(3,3)
    #print(fix_point)
    #choose a fixed point

#     for ship in ships: 
#         ship_dest[ship.id]= fix_point   #########CHANGE THIS TO ANY POINT,
#         print("my ship current location is: {}".format(ship.position))
#         print("ship_dest dic is: {}".format(ship_dest))
#         print("dest has halite: {}".format(board.cells[fix_point].halite))
    
    #choose the best haltie position
    halite_ships = [ship for ship in me.ships if ship.id!=attack_ship_id]
    #print('HALITE SHIPS ARE: {}'.format(halite_ships))
    for ship in halite_ships:
        if len(me.shipyards)>0 and ship.halite <=250:
            #print('my ship position is: {}'.format(ship.position))
            my_ship_id = ship.id
            #print('my ship ID is: {}'.format(my_ship_id))
            #print('all of my ships are: {}'.format(me.ship_ids))
            my_other_ship_id = tuple(set(me.ship_ids)- set([ship.id]))
            #print('my other ship ID is: {}'.format(my_other_ship_id))
            best_point, best_halite= find_best_cell(board, ship.position, my_ship_id, my_other_ship_id, window_size = 2)
            if best_halite > 50:
                ship_dest[ship.id]= best_point
                #print('WARNING: this resource at {} is MINE!!!'.format(best_point))
            else: 
                #print('WARNING: change window_size to 5 now')
                best_point, best_halite= find_best_cell(board, ship.position,my_ship_id, my_other_ship_id, window_size = 5)
                ship_dest[ship.id]= best_point
            #print("MODE: Best Halite Mode")
            #print("my ship current location is: {}".format(ship.position))
            #print("ship_dest dic is: {}".format(ship_dest))
            #print("dest has halite: {}".format(board.cells[best_point].halite))
        elif len(me.shipyards)>0 and ship.halite >250: 
            ship_dest[ship.id]=me.shipyards[0].position
            #print("I AM GOING HOME TO DEPOSIT {}".format(ship.halite))
        else: 
            #print("NO SHIPYARD!")
            ### Wait for the shipyard being built in the next step
            ### Don't move
            ship_dest[ship.id]=ship.position
            
    
    #maybe choose enemy base to attack
    attack_ships = [ship for ship in me.ships if ship.id==attack_ship_id]
    #print('ATTACK SHIPS ARE: {}'.format(attack_ships))
    for ship in attack_ships:
        ship_dest[ship.id]=attack_shipyard_loc


    #choose enemy ship
    
    #random move

        
    
    
    return 

####### Atack logic #######
def choose_target_shipyard(board):
    players_halite = {} # dict record players id and halite
    for i in range(len(board.players)):
        k = board.players[i].id
        v = board.players[i].halite
        players_halite[k]=v

    rank_list = sorted(players_halite.items(), key=lambda x:x[1], reverse=True)
    player_rank = []

    for i in range(len(rank_list)):
        player_rank.append(rank_list[i][0]) # Get the playerID rank list

    target_player_id = 1 
    ### Choose enemy    
    if player_rank.index(me.id) == 0:        
        # If we are 1st, attack 2nd
        target_player_id = player_rank[(player_rank.index(me.id) + 1)]
    else:          
        # If we are not 1st, attack the one rank higher than us
        target_player_id = player_rank[(player_rank.index(me.id) - 1)]
    
    target_point1 = (0,0)
    target_point2 = (0,0)
    
    ### Attack enemy's ship target_point1
    if len(board.players[target_player_id].ships) > 0: # check target player has ship
        target_shipid = ''
        target_point1 = (0,0)
        target_shipid = board.players[target_player_id].ship_ids[0]
        target_point1 = board.ships[target_shipid].position
    elif len(board.opponents[0].ships) > 0:
        target_shipid = ''
        target_point1 = (0,0)
        target_shipid = board.opponents[0].ship_ids[0]
        target_point1 = board.ships[target_shipid].position

    ### Attack enemy's shipyard target_point2
    if len(board.players[target_player_id].shipyards) > 0: # check target player has shipyard
        target_point2 = board.players[target_player_id].shipyards[0].position
    elif len(board.players[target_player_id].shipyards) == 0:
        for i in range(len(board.opponents)):
            if len(board.opponents[i].shipyards) > 0:
                target_point2 = board.opponents[i].shipyards[0].position
                break 
    else:
        target_point2 = (7,7)
    
    return(target_point2)

###########################


def steps(position, action):
  dest=None
  if dest is None: dest=position
  if action==ShipAction.NORTH: dest=position+Point(0,1)
  if action==ShipAction.SOUTH: dest=position+Point(0,-1)
  if action==ShipAction.EAST:  dest=position+Point(1,0)
  if action==ShipAction.WEST:  dest=position+Point(-1,0)

  return dest 

### Everything ship_turn_shipyard condition
def ship_turn_shipyard (board):
    #if no shipyard, convert the ship to shipyard
    #print('how many shipyard:{}'.format(len(me.shipyards)))
    #print('how many ships:{}'.format(len(me.ships)))
    if len(me.shipyards) == 0 and len(me.ships) > 0: 
        me.ships[0].next_action = ShipAction.CONVERT
        my_obs.not_available[me.ships[0].position] = 1
        my_obs.shipyard_num+=1
        my_obs.total_halite-=500
        
### Shipyard action
def shipyard_gen_ships (board):
    for shipyard in me.shipyards:
        if my_obs.ship_num < my_obs.max_ships: ###### CHECK BELOW #######
            if my_obs.total_halite >=500 and shipyard.position not in my_obs.not_available:
                shipyard.next_action = ShipyardAction.SPAWN
                #print(shipyard.position)
                my_obs.not_available[shipyard.position] = 1
                my_obs.ship_num+=1
                my_obs.total_halite-=500
                

    
            
    

# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    global me
    global size
    global no_movement_counter
    global attack_ship_id
    global other_player
    global attack_shipyard_loc
    global target_player_id
    global interval
    size = config.size
    board = Board(obs, config)
    me = board.current_player
    #print(me.ships[0].next_action)


    # If there are no shipyards, convert first ship into shipyard.
    #if len(me.shipyards) == 0 and len(me.ships) > 0:
        #me.ships[0].next_action = ShipAction.CONVERT
        
    # If there are no ships, use first shipyard to spawn a ship.
    #if len(me.ships) == 0 and len(me.shipyards) > 0:
        #me.shipyards[0].next_action = ShipyardAction.SPAWN
    #print('#####current step NO is {}######\n\n\n'.format(board.step)) 
    
    ### Get attack ship ID  
    
    interval = 50
    times = 0
    step_e = 0 
    step_list = []

    times = 300 // interval
    for i in range(1,times+1):
        step_e = i * interval
        step_list.append(step_e)
    
    
    if (board.step in step_list) and (len(me.ships)==3):
        attack_ship_id = me.ships[-1].id
        #print('ATTACK SHIP IS HERE!!! is {}'.format(attack_ship_id))
        attack_shipyard_loc = choose_target_shipyard(board)
        #print('Target shipyard has been found:{}'.format(attack_shipyard_loc))
        #### Choose other_player by ranking ########
    else:
        pass
    
    my_obs(board)
    ship_turn_shipyard(board)
    shipyard_gen_ships (board)
    ship_actions(board)
    

    
    ### Prevent Ideal Ships forever
    no_movements_ships=[ship for ship in me.ships if ship.next_action == None]
    
    if (len(no_movements_ships) == my_obs.ship_num) and my_obs.ship_num >1:
        no_movement_counter = no_movement_counter + 1
        if no_movement_counter > 5:
            ## RANDOM MOVE
            first_ship = me.ships[0]
            all_random_actions=[ShipAction.NORTH, ShipAction.EAST,ShipAction.SOUTH,ShipAction.WEST]
            valid_random = random.choice(all_random_actions)
            random_step = steps(first_ship.position,valid_random,)
            if random_step not in my_obs.not_available:
                first_ship.next_action = valid_random
                #print('First ship has to take a random move as we have been here for 5 steps by doing nothing!!!')
                no_movement_counter = 0
        else: pass #print('Wait, nothing is moving - current no movement counter is {}'.format(no_movement_counter))
    else: pass #print('ALL GOOD!!!')
        
    
        
                
    return me.next_actions
