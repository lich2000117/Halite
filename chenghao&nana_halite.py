# Imports helper functions
from kaggle_environments.envs.halite.helpers import *
import math
import random
import time

# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    
    size = config.size
    board = Board(obs, config)

    #### Scoring Functions

    config = {
        "player_halite": 1.1,
        "cargo_storage_reward": 1,
        "stay_and_collect_bonus": 2.1,
        "cargo_carry_penalty_multiplier": 1,
        "cargo_threshold": 150,
        "num_ships_award": 2,
        "num_bases_award": 1.1,
        "return_base_multiplier": 1,
        "high_halite_cell_threshold": 3,
        "move_to_high_halite_cell_multiplier": 1,
        "how_many_tiles_look_radius": 3,
        
        "offense_distance":3,
        "attack_reward":2,
        "defend_reward":1,
        "base_distance":5,
        "max_shipyard":3,
        "MAX_SHIP":3,
        
        "remain_steps_threshold":10,
    }

    def calculate_distance(point1, point2, board):
        """
        Calculate the shortest distance between two points in a toroidal grid
        """
        size = board.configuration.size
        dx = abs(point1[0] - point2[0])
        dy = abs(point1[1] - point2[1])
        return min(dx, size - dx) + min(dy, size - dy)

    def best_halite_cell_scoring(ship_position, cell_list, board):
        """Return the scoring for moving towards the best halite cell, consists of distance, target value."""
        max_value = -float('inf')
        best_cell = None
        for cell in cell_list:
            if board.cells[cell].ship:
                # skip where the cell is covered
                if board.cells[cell].ship.position!=ship_position:
                    continue
            distance = calculate_distance(ship_position, cell, board)
            halite = board.cells[cell].halite
            value = halite/(distance+1)*config["move_to_high_halite_cell_multiplier"]
            if value > max_value:
                max_value = value
                best_cell = cell
        return best_cell, max_value

        

    def find_closest_point(target_point, point_list, board):
        """find closeset point of a point and a list"""
        closest_distance = float('inf')
        closest_point = None

        for point in point_list:
            distance = calculate_distance(target_point, point, board)
            if distance < closest_distance:
                closest_distance = distance
                closest_point = point

        return closest_point, closest_distance
    
    def get_ships_by_point(point, board):
        for ship in board.ships.values():
            if ship.position == point:
                return ship
    
    def get_num_objects_nearby(center, target_list, board, radius=config["how_many_tiles_look_radius"]):
        """Provide a center, how many targets are fall in n radius space"""
        def get_surrounding_points(center, n, board):
            """
            Get all points within a radius n of the given center point in a toroidal grid
            """
            size = board.configuration.size
            points = []
            for x in range(size):
                for y in range(size):
                    point = (x, y)
                    if calculate_distance(center, point, board) <= n:
                        points.append(point)
            return points
        
        count = 0
        obj = []
        points = get_surrounding_points(center, radius, board)
        for point in points:
            if point in target_list:
                count += 1
                obj.append(point)
        return obj, count
        
    
    
    def Function_A(fact_board, board, player, debug=False):
        """Function handling Attack or Defense based on opponent ship location"""
        fact_opponent_ships = get_opponent_ships(fact_board, player)
        new_opponent_ships = get_opponent_ships(board, player)
        offense_score = 0  # this offense score could be negative if we need to defend
        
        # for each ship in future step, calculate score
        for ship in player.ships:
            nearest_enemy_ship, distance = find_closest_point(ship.position, fact_opponent_ships, board)
            if distance < config["offense_distance"]:
                
                # 1. Attack Mode if Enemy ship has less halite
                # we have less halite, attack
                halite_diff = ship.halite - get_ships_by_point(nearest_enemy_ship, fact_board).halite
                if halite_diff < 0:
                    if nearest_enemy_ship not in new_opponent_ships:
                        # 1.1. if our this move eliminates that ship from fact state, add bonus
                        offense_score += get_ships_by_point(nearest_enemy_ship, fact_board).halite*config["attack_reward"]
                    else:
                        #1.2 in pursuit mode, estimate offensive bonus
                        offense_score += abs(halite_diff)*(1/(1+distance))*config["attack_reward"]
                
                # 2. Defend Mode
                elif halite_diff >0:
                    # we have more halite, defend, move away from enemy, penalise when close
                    offense_score -= (abs(halite_diff) + 1)*(1/(1+distance))*config["defend_reward"]
                    
                    # if we are right next to enemy ship and we are stationary, immediate danger, move asap
                    if ship.id in fact_board.ships.keys():
                        if ship.position == fact_board.ships[ship.id].position and distance == 1:
                            offense_score -= (abs(ship.halite)*100)*config["defend_reward"]
                            
                    # penalise if move to base to defend
                    if len([True for player_yard in player.shipyards if player_yard.position == ship.position]) >= 1:
                        offense_score -= 100/(0.1+ship.halite) # if player has more halite , can defend to shipyard
                
        if player.ships:
            offense_score = offense_score/len(player.ships)
        
        ## For prediction Feature ONLY as normally we cannot make enemy ship move towards ours
        # if predict: 
        #     #for ship we lost, not in future ships, penalise
        #     #if we are stationary and enemy ship is one distance away, extra penalty
        #     for old_ship in fact_board.ships.values():
        #         # check if new enemy in our missing ship's location
        #         attacker_ship, distance = find_closest_point(old_ship.position, new_opponent_ships, board)
        #         if (old_ship not in player.ships) and distance == 0:
        #             offense_score -= (abs(get_ships_by_point(attacker_ship, board).halite) + 1)*config["defend_reward"]*999
        
        if debug: print(" Offense Score: ", offense_score)
        return offense_score
    
    def get_opponent_ships(board, player):
        return [ship.position for ship in board.ships.values() if ship.id not in board.players[player.id].ship_ids]
        
        
    def Function_B(fact_board, board, player, debug=False):
        """Building Scoring Function"""
        
        def spawn_bonus(fact_board, board, player):
            """Bonus for spawn ships that has nearby enemy ships or more resources"""
            score = 0
            for ship in player.ships:
                # identify new ship
                if ship.id not in fact_board.ships.keys():
                    opponent_ships = get_opponent_ships(board, player)
                    halite_cell_list = [cell.position for cell in board.cells.values()]
                    _, num_enemy_nearby = get_num_objects_nearby(ship.position, opponent_ships, board)
                    _, best_score = best_halite_cell_scoring(ship.position, halite_cell_list, board)
                    
                    score += best_score - num_enemy_nearby
            return score
        
        score = 0
        
        
        # 0. base number cannot be to large, use halite value as base 
        base_score = player.halite*config["player_halite"]
        score += base_score
        if debug: print("   Player Halite Reward: ", base_score)


        # 1. player ships number
        if (len(player.ships) > config["MAX_SHIP"]) :
            # hard coding, avoid excessive ships
            score -= 99999999
            
        ship_score = 0
        lost_ships = [ship_id for ship_id in fact_board.players[player.id].ship_ids if ship_id not in player.ship_ids]
        # if we predict losing a ship, do not make ships directly to avoid breaking rules.
        if len(lost_ships) == 0:
            ship_score = (len(player.ships)*500)*config["num_ships_award"]
            
        # 1.1 Spawn bonus for shipyard (where to spawn)
        score += spawn_bonus(fact_board, board, player)
        score += ship_score
        if debug: print("   Num Ships Award: ", ship_score)
        
        # 2. player base and ship number, at least 1
        if (len(player.shipyards)) < 1:
            # if player choose not to add a shipyard, instead they keep a ship
            if len(player.ships) == 1:
                # if player can still afford a ship after forced conversion, add penalty, they should continue to harvest then convert
                if player.halite + player.ships[0].halite > 1001:
                    score -= 9999999
            else:
                # more ships, must build a yard
                score -= 9999999
            
        # 3. if new shipyard is constructed, evaluate
        # we want number of shipyard
        new_yard_score = 0
        shipyards_list = [shipyard for shipyard in player.shipyards]
        if len(shipyards_list) > config["max_shipyard"]:
            score -= 9999999
        else:
            for yard in shipyards_list:
                if (len(shipyards_list)>1) and (yard.id not in fact_board.shipyards):
                    # identify it is a new shipyard, 

                    #calculate distance to other shipyard, the further away, better
                    _, distance = find_closest_point(yard.position, [y.position for y in shipyards_list if y != yard], board)
                    
                    if distance > config["base_distance"]: # manually setup, shipyard must be 5 grid away
                        opponent_ships = [board.ships[ship].position for ship in board.ships if ship not in player.ships]
                        player_ships = [ship.position for ship in player.ships]
                        _, num_enemy_nearby = get_num_objects_nearby(yard.position, opponent_ships, board)
                        friendly_nearby_ship_positions, num_friendly_nearby = get_num_objects_nearby(yard.position, player_ships, board)
                        friendly_ship_load = 1

                        # get halite bonus to build a base near rich friendly ships
                        for f_ship in player.ships:
                            if f_ship.position in friendly_nearby_ship_positions:
                                friendly_ship_load += f_ship.halite # must have enough resources to build extra bases
                        new_yard_score = (distance/board.configuration.size) * (1/(1+num_enemy_nearby)) + friendly_ship_load #+ 500*config["num_ships_award"] + 500*config["player_halite"] # compensate lost ship and cost of building
                        new_yard_score *= 9999  # always build shipyard if possible, above is for selection criteria only if multiple ships want to build shipyard
            score += new_yard_score
        if debug: print("   New Yard Score: ", new_yard_score)
        
        return score


    def Function_C(fact_board, board, player, debug=False):
        """This scoring function measures the score for collecting resources"""
        
        def ship_behaviour(fact_board, board, player):
            """Calculate score for moving exploration or stay and collect, return to base or convert."""
            stay_score = 0
            explore_score = 0
            return_score = 0
            shipyards_list = [shipyard.position for shipyard in player.shipyards]
            for ship in player.ships:
                if ship.id in fact_board.ships.keys():
                    #if (fact_board.ships[ship.id].position == ship.position) and (fact_board.ships[ship.id].halite <= config["cargo_threshold"]):
                    if (fact_board.ships[ship.id].position == ship.position):
                        ## FIRST: Ship stays stationary
                        
                        ## 1. If ship has not been moved and not reach the cargo amount threshold, meaning they are collecting halite, add bonus
                        temp_score = (board.cells[ship.position].halite)/(1 + 0) * config["stay_and_collect_bonus"] * 2 # by default, we want the ship to stay and collect unless the next cell has (2 x (Distance+1)) more resources
                        temp_score = temp_score/len(player.ships)
                        
                        stay_score += temp_score

                    else:
                        ## SECOND: Ship's location has changed

                        # Base if ship has higher than threshold, should return to base. Use previous timestamp as if the ship is already at the base, it has no halite
                        if fact_board.ships[ship.id].halite > config["cargo_threshold"]:
                            # 1. Situation of the board, ship going back to shipyard 
                            # we want the ship to move towards nearest bases.
                            if shipyards_list:
                                # Note: if no base exists, skip, as it was handled in Function_B
                                closest_shipyard, distance = find_closest_point(ship.position, shipyards_list, board)
                                # 1. calculate score based on distance, config and halite amount, # if reach base, the value will be large
                                temp_score = (fact_board.ships[ship.id].halite+1) / (0.5 + distance) * config["return_base_multiplier"]
                            else:
                                temp_score = 0
                            temp_score = temp_score/len(player.ships)
                            return_score += temp_score
                    
                        else:
                            ## 2. add explore score
                            
                            halite_cell_list = [cell.position for cell in board.cells.values()]
                            if halite_cell_list:

                                # 2.1 move towards best (distance+value) halite cell
                                best_halite_cell, best_score = best_halite_cell_scoring(ship.position, halite_cell_list, board)
                                temp_score = best_score 
                                temp_score = temp_score/ (len(player.ships)) # to offset halite amount for each ship


                                # 2.2 move towards high halite cell *area*
                                area_score = 0
                                for cell in halite_cell_list:
                                    area_score += board.cells[cell].halite/ (1+calculate_distance(ship.position, cell, board)) * 0.005
                                area_score = area_score/len(halite_cell_list)
                            explore_score = explore_score + temp_score + area_score

            if debug: 
                print("   Move to High Resources Reward: ", explore_score)
                print("   Stay Reward: ", stay_score)
                print("   Return Base Reward: ", return_score)
            if player.ships:
                return (explore_score + stay_score + return_score)
            else:
                return 0
        
        score = 0
        # 4. collecting resource or explore, bonus calculation
        score += ship_behaviour(fact_board, board, player)
        return score
    
    def get_action_list_for_one_object(obj_id, action_list, action_type="ship_actions"):
        """The combination format is a list of actions the ship can take,
        
        comb1,which is situation
        situation = 
                [
                {"ship_action":
                        {
                        "id": Action1, 
                        },
                },
                {"ship_action":
                        {
                        "id": Action12, 
                        },
                }
                ]
                
        
        if predict is True, it will only generate combinations for ship basic movement
        """
        actions = list(action_list)  
        actions.append("") # this None refers to ship not moving, collecting resources, base not constructing
        
        list_actions = []
        for act in actions:
            list_actions.append({action_type: {obj_id: act}})
        return list_actions


    def sugggest_move_based_on_situation(board, situation):
        """suggest move based on situation, put in queue but do not update board, return a new suggested board""" 

        new_board = board.__deepcopy__(board)

        # for ships action update
        if "ship_actions" in situation.keys():
            for ship in list(situation["ship_actions"].keys()):
                move = situation["ship_actions"][ship]
                if move:
                    if ship not in new_board.ships.keys():
                        # if our next move will destroy this ship so this ship not on the board
                        continue
                    else:
                        new_board.ships[ship].next_action = move

        # for shipyard action update
        if "base_actions" in situation.keys():
            for base in list(situation["base_actions"].keys()):
                move = situation["base_actions"][base]
                if move:
                    if base not in new_board.shipyards.keys():
                        # if our next move will destroy one of the ship
                        continue
                    else:
                        new_board.shipyards[base].next_action = move

        return new_board



    def get_best_situation(score_dict):
        key_with_highest_value = max(score_dict, key=lambda k: score_dict[k])
        return key_with_highest_value
    
    
    def calculate_board_score(fact_board, board, player):
        """Get score for the input board"""
        total_score = 0
        total_score += Function_A(fact_board, board, player)
        total_score += Function_B(fact_board, board, player)
        total_score += Function_C(fact_board, board, player)
        return total_score
    
    def make_move(player_id, fact_board, other_player_actions=[], isPredict=False):
        """Main function, select best move for that player and return a board ready to be updated (store all next action for that player)
             If predict=True, it will only predict ship movement to reduce number of combinations
            This is the implementation of second methodology: we sequentially look up each action, 
            the alternative would be check all combinations (timeout) 
        """
        # for every possible situation, get what the next board looks like
        
        def progress_objs(fact_board, progress_board, player_id, obj_type):
            output_actions = [] # list of best actions: list of {"ship_actions":{id, move}}
            if obj_type == "ship_actions":
                obj_list = fact_board.players[player_id].ships
                actionType = ShipAction
            else:
                obj_list = fact_board.players[player_id].shipyards
                actionType = ShipyardAction
                
            # for each ship, choose best action, shuffle each sequence.
            random.shuffle(obj_list)
            for obj in obj_list:
                possible_situations_single_obj = get_action_list_for_one_object(obj.id, actionType, obj_type)
                score_dict = {}
                for i in range(len(possible_situations_single_obj)):
                    situation = possible_situations_single_obj[i]
                    
                    # consider other player's action as well.
                    out = {}
                    # First, add the 'sit' dictionary to 'out'# Then, add each dictionary in 'pre' to 'out'
                    out.update(situation)
                    for d in other_player_actions:
                        for key, value in d.items():
                            if key in out:
                                out[key].update(value)
                            else:
                                out[key] = value
                    situation = out
                    
                    temp_next_board = sugggest_move_based_on_situation(progress_board, situation).next() # assume the step is taken
                    # get score for this situation (progress_board)
                    score_for_this_situation = calculate_board_score(fact_board, temp_next_board, temp_next_board.players[player_id])

                    # save score, dictionary, key is the index of situation, value is the score
                    score_dict[i] = score_for_this_situation
                
                # now we have full dictionary of score for each move situation
                # select the best one.
                best_i = get_best_situation(score_dict)
                best_action = possible_situations_single_obj[best_i]
                # return the best move suggested in the board object (not updated)
                output_board = sugggest_move_based_on_situation(progress_board, best_action)
                
                
               ## DEBUG
#                 debug_id = "5-1"
#                 #if board.step > 65 and board.step<90:
#                 if True:
#                     if obj.id == debug_id and obj_type == "ship_actions":
#                         ## Print move list
#                         sorted_situations = sorted(possible_situations_single_obj, key=lambda x: score_dict[possible_situations_single_obj.index(x)], reverse=True)

#                         # Print the sorted list
#                         i = 0
#                         if player_id == me:
#                             print("! Our Action:")
#                         print("\n-\n=== Action and corresponding Scores: ====")
#                         print(board.step)
#                         for index in sorted_situations:
#                             #if ShipAction.EAST == index["ship_actions"][debug_id] or ShipAction.WEST == index["ship_actions"][debug_id]: #or ShipAction.EAST == index["ship_actions"][debug_id] or "" == index["ship_actions"][debug_id]:
#                             if True:
#                                 #i += 1
#                                 #if i == 13:
#                                     print(index, score_dict[possible_situations_single_obj.index(index)])
#                                     test_board = sugggest_move_based_on_situation(progress_board, index).next()
#                                     print("  -- Score Break Down")
#                                     print(fact_board.ships.keys())
#                                     print("  A Score:", Function_A(fact_board, test_board, test_board.players[player_id], True))
#                                     print("  C Score:", Function_C(fact_board, test_board, test_board.players[player_id], True))
#                                     print("  B Score:", Function_B(fact_board, test_board, test_board.players[player_id], True))

    
                # move on to next iteration asssume the board applies best decision for this single ship, use this board as baseline
                progress_board = output_board.next()  
                output_actions.append(best_action)
            return progress_board, output_actions
        
        progress_board = fact_board.__deepcopy__(fact_board)
        
        progress_board, action_ships = progress_objs(fact_board, progress_board, player_id, "ship_actions")
        progress_board, action_bases = progress_objs(fact_board, progress_board, player_id, "base_actions")
        
        # put all actions together to board
          
        output_actions = {}
        
        #list1 = [{'ship_actions': {'2-1': <ShipAction.WEST: 4>}}, {'ship_actions': {'3-1': <ShipAction.NORTH: 1>}}, {'ship_actions': {'4-1': <ShipAction.WEST: 4>}}]
        #list2 = [{'base_actions': {'1-1': ''}}]
        #output=[{'ship_actions': {'2-1': <ShipAction.WEST: 4>, '3-1': <ShipAction.NORTH: 1>, '4-1': <ShipAction.WEST: 4>}, 'base_actions': {'1-1': ''}}]
        method_output_actions = action_ships + action_bases
        for item in method_output_actions:
            for key, value in item.items():
                output_actions.setdefault(key, {}).update(value)

        # update original board for actions
        output_board = sugggest_move_based_on_situation(fact_board, output_actions)
        
        ## return an output action so we can pass it around and an output board for outputing
        return method_output_actions, output_board
        
    
    def game_update_config(board):
        """This function has hard coded config value for end game"""
        cur_step = board.step+2
        steps_left = board.configuration["episodeSteps"] - cur_step
        if steps_left < config["remain_steps_threshold"]:
            config["return_base_multiplier"] *= 2
            config["move_to_high_halite_cell_multiplier"] = 0
            config["cargo_carry_penalty_multiplier"] *= 2
            config["cargo_threshold"] /= 2
        return
        
    
    ##### MAIN CODE

    # Get the current time before executing the line
    start_time = time.time()
    
    game_update_config(board)
    
    me = board.current_player_id
    
    # one step look ahead, store enemy component's move in our progress board so our steps would take acount of their moves.
    
    predicted_opponent_actions = []
    
    ## Predict Enable?
#     if True: 
#         for player in board.opponents:
#             # record predicted enemy move
#             action, _ = make_move(player.id, board, [])
#             predicted_opponent_actions += action
    _, output_board = make_move(me, board, predicted_opponent_actions)
    
    
    # # Print the execution time
    # exe_time = time.time() - start_time
    # if exe_time > 2.5:
    #     print("Execution time:", exe_time)
    return output_board.current_player.next_actions
