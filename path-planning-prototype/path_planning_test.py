from sande_gps import *
from enum import Enum

SANDE_X = 18
SANDE_Y = 10

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    GENERAL_LR = 4
    GENERAL_RL = 5

def initialize_grid(bounding_box: BoundingBox) -> list:
    print(bounding_box.get_top_l_corner())
    print(bounding_box.get_bottom_r_corner())
    grid = bounding_box.quantize_to_grid(SANDE_X, SANDE_Y)
    print(len(grid))
    print(len(grid[0]))
    return grid

def find_closest_corner(top_l: tuple, bottom_l: tuple, top_r: tuple, bottom_r: tuple) -> tuple:
    current_pos = get_current_gps_position()
    distance_top_l = ((top_l[0] - current_pos[0])**2 + (top_l[1] - current_pos[1])**2)**0.5
    distance_bottom_l = ((bottom_l[0] - current_pos[0])**2 + (bottom_l[1] - current_pos[1])**2)**0.5
    distance_top_r = ((top_r[0] - current_pos[0])**2 + (top_r[1] - current_pos[1])**2)**0.5
    distance_bottom_r = ((bottom_r[0] - current_pos[0])**2 + (bottom_r[1] - current_pos[1])**2)**0.5
    min_distance = (distance_top_l, top_l)
    for distance in [(distance_bottom_l, bottom_l), (distance_top_r,top_r), (distance_bottom_r, bottom_r)]:
        if distance[0] < min_distance[0]:
            min_distance = distance
    return min_distance[1]

def get_initial_direction(bounding_box: BoundingBox) -> tuple:
    top_l = bounding_box.get_top_l_corner()
    bottom_r = bounding_box.get_bottom_r_corner()
    bottom_l = (bottom_r[0], top_l[1])
    top_r = (top_l[0], bottom_r[1])
    closest_corner = find_closest_corner(top_l, bottom_l, top_r, bottom_r)
    if closest_corner == top_l:
        return (Direction.DOWN, Direction.GENERAL_LR)
    if closest_corner == top_r:
        return (Direction.DOWN, Direction.GENERAL_RL)
    if closest_corner == bottom_l:
        return (Direction.UP, Direction.GENERAL_LR)
    if closest_corner == bottom_r:
        return (Direction.UP, Direction.GENERAL_RL)


def move(direction: Direction, gen_direction: Direction, grid: list, i: int, j: int) -> tuple:
    if direction == Direction.DOWN:
        if i == len(grid) - 1:
            if (j == len(grid[i]) - 1 and gen_direction == Direction.GENERAL_LR) or (j == 0 and gen_direction == Direction.GENERAL_RL):
                return (-1, i, j, direction)
            if gen_direction == Direction.GENERAL_LR:
                grid[i][j] = ">"
                j += 1
            else:
                grid[i][j] = "<"
                j -= 1
            direction = Direction.UP
        else:
            grid[i][j] = 'v'
            i += 1
    elif direction == Direction.UP:
        if i == 0:
            if (j == len(grid[i]) - 1 and gen_direction == Direction.GENERAL_LR) or (j == 0 and gen_direction == Direction.GENERAL_RL):
                return -1
            if gen_direction == Direction.GENERAL_LR:
                grid[i][j] = ">"
                j += 1
            else:
                grid[i][j] = "<"
                j -= 1
            direction = Direction.DOWN
        else:
            grid[i][j] = '^'
            i -= 1
    else:
        return (-1, i, j, direction)
    return (0, i, j, direction)

def test_main():
    print("Testing path planning")
    bounding_box: BoundingBox = BoundingBox('33°46\'44.6"N', '84°24\'20.5"W', '33°46\'44.1"N', '84°24\'19.3"W')
    i = 0
    j = 0
    direction, gen_direction = get_initial_direction(bounding_box)
    grid = initialize_grid(bounding_box)
    print(f"Initial State: ({i}, {j}), Direction: {direction}")

    err = 0
    while (err != -1):
        err, i, j, direction = move(direction, gen_direction, grid, i, j)
        print(f"Current state: ({i}, {j}), Direction: {direction}")
    for row in grid:
        print(row)
    

if __name__ == "__main__":
    test_main()
