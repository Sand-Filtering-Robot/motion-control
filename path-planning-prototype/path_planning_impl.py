from sande_gps import *
from enum import Enum

SANDE_X = 18
SANDE_Y = 10

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

class OverallDirection(Enum):
    LR = 0
    RL = 1

class PlanStateManager:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.direction = Direction.DOWN
        self.overall_direction = OverallDirection.LR
        self.direction_stack = []
        self.unmatched_moves = []
        self.grid = []


def initialize_grid(bounding_box: BoundingBox) -> list:
    print(bounding_box.get_top_l_corner())
    print(bounding_box.get_bottom_r_corner())
    grid = bounding_box.quantize_to_grid(SANDE_X, SANDE_Y)
    print(len(grid))
    print(len(grid[0]))
    return grid

def find_closest_corner(top_l: tuple, bottom_l: tuple, top_r: tuple, bottom_r: tuple) -> tuple:
    current_pos = read_gps_coords()
    distance_top_l = ((top_l[0] - current_pos[0])**2 + (top_l[1] - current_pos[1])**2)**0.5
    distance_bottom_l = ((bottom_l[0] - current_pos[0])**2 + (bottom_l[1] - current_pos[1])**2)**0.5
    distance_top_r = ((top_r[0] - current_pos[0])**2 + (top_r[1] - current_pos[1])**2)**0.5
    distance_bottom_r = ((bottom_r[0] - current_pos[0])**2 + (bottom_r[1] - current_pos[1])**2)**0.5
    min_distance = (distance_top_l, top_l)
    for distance in [(distance_bottom_l, bottom_l), (distance_top_r,top_r), (distance_bottom_r, bottom_r)]:
        if distance[0] < min_distance[0]:
            min_distance = distance
    return min_distance[1]

# Operating under assumption of top left 
def get_initial_direction(bounding_box: BoundingBox) -> tuple:
    top_l = bounding_box.get_top_l_corner()
    bottom_r = bounding_box.get_bottom_r_corner()
    bottom_l = (bottom_r[0], top_l[1])
    top_r = (top_l[0], bottom_r[1])
    closest_corner = find_closest_corner(top_l, bottom_l, top_r, bottom_r)
    if closest_corner == top_l:
        return (Direction.DOWN, OverallDirection.LR)
    if closest_corner == top_r:
        return (Direction.DOWN, OverallDirection.RL)
    if closest_corner == bottom_l:
        return (Direction.UP, OverallDirection.LR)
    if closest_corner == bottom_r:
        return (Direction.UP, OverallDirection.RL)

def term(state):
    if len(state.grid[0]) % 2 == 0:
        return state.x == 0 and state.y == len(state.grid[0]) - 1
    else:
        return state.x == len(state.grid) - 1 and state.y == len(state.grid[0]) - 1

def at_turning_edge(state):
    if state.direction == Direction.UP:
        return state.x == 0
    elif state.direction == Direction.DOWN:
        return state.x == len(state.grid) - 1
    else:
        return state.x == 0 or state.x == len(state.grid) - 1 


def setNextDirection(state):
    if state.direction == Direction.UP:
        if state.overall_direction == OverallDirection.LR:
            state.direction = Direction.RIGHT
        else:
            state.direction = Direction.LEFT
    elif state.direction == Direction.DOWN:
        if state.overall_direction == OverallDirection.LR:
            state.direction = Direction.RIGHT
        else:
            state.direction = Direction.LEFT

# Motion control API calls here
def send_move_control_signal(direction):
    print("Sending move signal " + str(direction) + " to motion control!")

def move_up(state):
    state.grid[state.x][state.y] = "^"
    state.x -= 1

def move_down(state):
    state.grid[state.x][state.y] = "v"
    state.x += 1

def move_left(state):
    state.grid[state.x][state.y] = "<"
    state.y -= 1

def move_right(state):
    state.grid[state.x][state.y] = ">"
    state.y += 1


# Object detection API calls will go here eventually
def can_move_in_direction(moveDirection, state):
    if moveDirection == Direction.UP:
        return state.x > 0 and (state.grid[state.x - 1][state.y] != "X")
    elif moveDirection == Direction.DOWN:
        return state.x < len(state.grid) - 1 and (state.grid[state.x + 1][state.y] != "X")
    elif moveDirection == Direction.LEFT:
        return state.y > 0 and (state.grid[state.x][state.y - 1] != "X")
    elif moveDirection == Direction.RIGHT:
        return state.y < len(state.grid[0]) - 1 and (state.grid[state.x][state.y + 1] != "X")
    else:
        return False

def opposite(opp):
    if opp == Direction.UP:
        return Direction.DOWN
    if opp == Direction.DOWN:
        return Direction.UP
    if opp == Direction.LEFT:
        return Direction.RIGHT
    if opp == Direction.RIGHT:
        return Direction.LEFT
    

def set_direction_perp(state):
    if state.direction == Direction.UP:
        if state.overall_direction == OverallDirection.LR:
            if state.y == len(state.grid[0]) - 1:
                state.direction = Direction.LEFT
            else:
                state.direction = Direction.RIGHT
        else:
            state.direction = Direction.LEFT
    elif state.direction == Direction.DOWN:
        if state.overall_direction == OverallDirection.LR:
            if state.y == len(state.grid[0]) - 1:
                state.direction = Direction.LEFT
            else:
                state.direction = Direction.RIGHT
        else:
            state.direction = Direction.LEFT
    elif state.direction == Direction.LEFT:
        if state.overall_direction == OverallDirection.LR:
            state.direction = Direction.UP
        else:
            state.direction == Direction.DOWN
    elif state.direction == Direction.RIGHT:
        if state.overall_direction == OverallDirection.LR:
            state.direction = Direction.UP
        else:
            state.direction == Direction.DOWN

def move(state: PlanStateManager) -> int:
    if (not len(state.unmatched_moves) and len(state.direction_stack)) or len(state.direction_stack) > 1:
        if (can_move_in_direction(state.direction_stack[-1], state)):
            state.direction = state.direction_stack.pop()
        else:
            if len(state.direction_stack) > 1:
                state.unmatched_moves.append(opposite(state.direction))
    elif len(state.direction_stack) == 1 and len(state.unmatched_moves):
        if can_move_in_direction(state.unmatched_moves[-1], state):
            state.direction =  state.unmatched_moves.pop()

    if state.direction == Direction.DOWN:
        if term(state):
            state.grid[state.x][state.y] = "T"
            return -1
        if at_turning_edge(state):
            setNextDirection(state)
        else:
            if can_move_in_direction(state.direction, state):
                move_down(state)
            else:
                unmatched = False
                while (not can_move_in_direction(state.direction, state)):
                    if not unmatched:
                        state.direction_stack.append(state.direction)
                        state.direction_stack.append(state.direction)
                    set_direction_perp(state)
                    unmatched = True
    elif state.direction == Direction.UP:
        if term(state):
            state.grid[state.x][state.y] = "T"
            return -1
        if at_turning_edge(state):
            setNextDirection(state)
        else:
            if can_move_in_direction(state.direction, state):
                move_up(state)
            else:
                unmatched = False
                while (not can_move_in_direction(state.direction, state)):
                    if not unmatched:
                        state.direction_stack.append(state.direction)
                        state.direction_stack.append(state.direction)
                    set_direction_perp(state)
                    unmatched = True
    elif state.direction == Direction.LEFT:
        if term(state):
            state.grid[state.x][state.y] = "T"
            return -1
        if can_move_in_direction(state.direction, state):
            move_left(state)
            if at_turning_edge(state):
                if state.x == 0:
                    state.direction = Direction.DOWN
                else:
                    state.direction = Direction.UP
                state.direction_stack = []
                state.unmatched_moves = []
    elif state.direction == Direction.RIGHT:
        if term(state):
            state.grid[state.x][state.y] = "T"
            return -1
        if can_move_in_direction(state.direction, state):
            move_right(state)
            if at_turning_edge(state):
                if state.x == 0:
                    state.direction = Direction.DOWN
                else:
                    state.direction = Direction.UP
                state.direction_stack = []
                state.unmatched_moves = []
    send_move_control_signal(state.direction)
    return 0

def test_main():
    print("Testing path planning")
    bounding_box: BoundingBox = BoundingBox('33°46\'44.6"N', '84°24\'20.5"W', '33°46\'44.1"N', '84°24\'19.3"W')
    state = PlanStateManager()
    direction, gen_direction = get_initial_direction(bounding_box)
    state.direction = direction
    state.overall_direction = gen_direction

    grid = initialize_grid(bounding_box)

    state.grid = grid
    print(f"Initial State: ({state.x}, {state.y}), Direction: {state.direction}")

    move_return = 0
    while (move_return != -1):
        move_return = move(state)
        print(f"Current state: ({state.x}, {state.y}), Direction: {state.direction}")
    for row in state.grid:
        print(row)
    

if __name__ == "__main__":
    test_main()
