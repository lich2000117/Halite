
### This function will find nearest shipyard and destroy it



# Imports helper functions
from kaggle_environments.envs.halite.helpers import *

# Returns best direction to move from one position (fromPos) to another (toPos)
# Example: If I'm at pos 0 and want to get to pos 55, which direction should I choose?
def getDirTo(fromPos, toPos, size):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    if fromY < toY: return ShipAction.NORTH
    if fromY > toY: return ShipAction.SOUTH
    if fromX < toX: return ShipAction.EAST
    if fromX > toX: return ShipAction.WEST
    

def calculate_distance(point1, point2, board):
    """
    Calculate the shortest distance between two points in a toroidal grid
    """
    size = board.configuration.size
    dx = abs(point1[0] - point2[0])
    dy = abs(point1[1] - point2[1])

    return min(dx, size - dx) + min(dy, size - dy)
    
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

# Directions a ship can move
directions = [ShipAction.NORTH, ShipAction.EAST, ShipAction.SOUTH, ShipAction.WEST]

# Will keep track of whether a ship is collecting halite or carrying cargo to a shipyard
ship_states = {}

# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player
    opponent = board.opponents[0]
    enemy_ships = [ship for ship in opponent.shipyards]
    
    # If there are no ships, use first shipyard to spawn a ship.
    if len(me.ships) == 0 and len(me.shipyards) > 0:
        me.shipyards[0].next_action = ShipyardAction.SPAWN

    # If there are no shipyards, convert first ship into shipyard.
    if len(me.shipyards) == 0 and len(me.ships) > 0:
        me.ships[0].next_action = ShipAction.CONVERT
    
    for ship in me.ships:
        if ship.next_action == None:
            point,_ = find_closest_point(ship.position, [s.position for s in enemy_ships], board)
            direction = getDirTo(ship.position, point, size)
            if direction: ship.next_action = direction
                
    return me.next_actions
