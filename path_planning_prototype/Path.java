import java.util.Stack;

public class Path {
    private static int x = 0;
    private static int y = 0;
    private static Direction direction = Direction.DOWN;
    private static OverallDirection overallDirection = OverallDirection.LR;
    private static Stack<Direction> directionStack = new Stack<>();
    private static Stack<Direction> unmatchedMoves = new Stack<>();

    private static enum Direction {
        UP,
        DOWN,
        LEFT,
        RIGHT
    }
    private static enum OverallDirection {
        LR,
        RL
    }
    private static char[][] grid = new char[10][15];
    
    private static boolean verbose = false;
    public static void main(String[] args) throws Exception {
        if (args.length > 0 && args[0].equals("-v")) {
            verbose = true;
        }

        for (int i = 0; i < grid.length; ++i) {
            for (int j = 0; j < grid[i].length; ++j) {
                grid[i][j] = '0';
            }
        }

        printGrid();

        while (move() != -1) {
            System.out.printf("Current state: (%d, %d), Direction: %s\n", x, y, direction);
            if (verbose)
                printGrid();
            System.out.println();
        }
        System.out.println("\nFinal State:\n");
        printGrid();
        System.out.println();
    }

    public static void printGrid() {
        for (char[] arr : grid) {
            System.out.println(java.util.Arrays.toString(arr));
        }
    }

    private static boolean term() {
        if (grid[0].length % 2 == 0) {
            return x == 0 && y == grid[0].length - 1;
        } else {
            return x == grid.length - 1 && y == grid[0].length - 1;
        }
    }

    private static boolean atTurningEdge() {
        switch (direction) {
            case UP:
                return x == 0;
            case DOWN:
                return x == grid.length - 1;
            case LEFT:
                return x == 0 || x == grid.length - 1;
            case RIGHT:
                return x == 0 || x == grid.length - 1;
        }
        return false;
    }

    private static void setNextDirection() {
        switch (direction) {
            case UP:
                if (overallDirection == OverallDirection.LR) {
                    direction = Direction.RIGHT;
                } else {
                    direction = Direction.LEFT;
                }
                break;
            case DOWN:
                if (overallDirection == OverallDirection.LR) {
                    direction = Direction.RIGHT;
                } else {
                    direction = Direction.LEFT;
                }
                break;
            default:
                return;
        }
    }

    // Motion control API calls here
    private static void sendMoveControlSig() {
        System.out.println("sending move signal " + direction + " to motion control");
    }

    private static void moveUp() {
        grid[x][y] = '^';
        x--;
    }
    
    private static void moveDown() {
        grid[x][y] = 'v';
        x++;
    }
    
    private static void moveLeft() {
        grid[x][y] = '<';
        y--;
    }
    
    private static void moveRight() {
        grid[x][y] = '>';
        y++;
    }

    // Object Detection API calls here
    private static boolean canMoveInDirection(Direction moveDirection) {
        switch (moveDirection) {
            case UP:
                return x > 0 && grid[x - 1][y] != 'X';
            case DOWN:
                return x < grid.length - 1 && grid[x + 1][y] != 'X';
            case LEFT:
                return y > 0 && grid[x][y - 1] != 'X';
            case RIGHT:
                return y < grid[x].length - 1 && grid[x][y + 1] != 'X';
        }
        return false;
    }

    private static Direction opposite(Direction opp) {
        switch (opp) {
            case UP:
                return Direction.DOWN;
            case DOWN:
                return Direction.UP;
            case LEFT:
                return Direction.RIGHT;
            default:
                return Direction.LEFT;
        }
    }

    private static void setDirectionPerp() {
        switch (direction) {
            case UP:
                if (overallDirection == OverallDirection.LR) {
                    if (y == grid[0].length - 1) {
                        direction = Direction.LEFT;
                    } else {
                        direction = Direction.RIGHT;
                    }
                } else {
                    direction = Direction.LEFT;
                }
                break;
            case DOWN:
                if (overallDirection == OverallDirection.LR) {
                    if (y == grid[0].length - 1) {
                        direction = Direction.LEFT;
                    } else {
                        direction = Direction.RIGHT;
                    }
                } else {
                    direction = Direction.LEFT;
                }
                break;
            case LEFT:
                if (overallDirection == OverallDirection.LR) {
                    direction = Direction.UP;
                } else {
                    direction = Direction.DOWN;
                }
                break;
            case RIGHT:
                if (overallDirection == OverallDirection.LR) {
                    direction = Direction.UP;
                } else {
                    direction = Direction.DOWN;
                }
                break;
        }
    }

    public static int move() {
        if (unmatchedMoves.empty() && !directionStack.empty() || directionStack.size() > 1) {
            if (canMoveInDirection(directionStack.peek())) {
                direction = directionStack.pop();
            } else {
                if (directionStack.size() > 1) {
                    unmatchedMoves.push(opposite(direction));
                }
            }
        } else if (directionStack.size() == 1 && !unmatchedMoves.empty()) {
            if (canMoveInDirection(unmatchedMoves.peek())) {
                direction = unmatchedMoves.pop();
            }
        }

        switch (direction) {
            case DOWN:
                if (term()) { grid[x][y] = 'T'; return -1; }
                if (atTurningEdge()) {
                    setNextDirection();
                } else {
                    if (canMoveInDirection(direction)) {
                        moveDown();
                    } else {
                        boolean unmatched = false;
                        while (!canMoveInDirection(direction)) {
                            if (!unmatched) { directionStack.push(direction); directionStack.push(direction); }
                            setDirectionPerp();
                            unmatched = true;
                        }
                    }
                }
                break;
            case UP:
                if (term()) { grid[x][y] = 'T'; return -1; }
                if (atTurningEdge()) {
                    setNextDirection();
                } else {
                    if (canMoveInDirection(direction)) {
                        moveUp();
                    } else {
                        boolean unmatched = false;
                        while (!canMoveInDirection(direction)) {
                            if (!unmatched) { directionStack.push(direction); directionStack.push(direction); }
                            setDirectionPerp();
                            unmatched = true;
                        }
                    }
                }
                break;
            case LEFT:
                if (term()) { return -1; }
                if (canMoveInDirection(direction)) {
                    moveLeft();
                    if (atTurningEdge()) {
                        if (x == 0) {
                            direction = Direction.DOWN;
                        } else {
                            direction = Direction.UP;
                        }
                        directionStack.clear();
                        unmatchedMoves.clear();
                    }
                }
                break;
            case RIGHT:
                if (term()) { return -1; }
                if (canMoveInDirection(direction)) {
                    moveRight();
                    if (atTurningEdge()) {
                        if (x == 0) {
                            direction = Direction.DOWN;
                        } else {
                            direction = Direction.UP;
                        }

                        directionStack.clear();
                        unmatchedMoves.clear();
                    }
                }
                break;
        }
        sendMoveControlSig();
        return 0;
    }
}
