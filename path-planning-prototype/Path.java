import java.util.Random;

public class Path {
    private static int x = 0;
    private static int y = 0;
    private static Direction direction = Direction.DOWN;
    private static OverallDirection overallDirection = OverallDirection.LR_StopB;
    private static enum Direction {
        UP,
        DOWN,
        LEFT,
        RIGHT
    }
    private static enum OverallDirection {
        LR_StopB,
        LR_StopT,
        RL_StopB,
        RL_StopT
    }
    private static char[][] grid = new char[10][15];
    private static int[] displacement = new int[]{0, 0};
    
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

        // grid[2][1] = 'X';
        // grid[3][2] = 'X';
        // grid[4][1] = 'X';
        // grid[4][0] = 'X';
        // grid[4][14] ='X';
        Random rand = new Random();
        for (int i = 0; i < 15; ++i) {
            int a = rand.nextInt(grid.length);
            int b = rand.nextInt(grid[0].length);
            a = a > 0 ? a : 1;
            a = a < grid.length - 1 ? a : grid.length - 2;
            b = b > 0 ? b : 1;
            b = b < grid[0].length - 1 ? b : grid[0].length - 2;
            grid[a][b] = 'X';
        }

        // grid =  new char[][]{{'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'},
        //         {'0', '0', '0', '0', 'X', '0', '0', '0', 'X', '0', '0', '0', '0', '0', '0'},
        //         {'0', '0', '0', '0', '0', 'X', '0', '0', '0', '0', '0', 'X', '0', 'X', '0'},
        //         {'0', 'X', '0', '0', '0', '0', '0', '0', 'X', '0', '0', '0', '0', '0', '0'},
        //         {'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'},
        //         {'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'X', 'X', '0'},
        //         {'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'X', '0', '0', '0'},
        //         {'0', '0', 'X', '0', '0', '0', '0', '0', 'X', '0', '0', '0', '0', '0', '0'},
        //         {'0', 'X', '0', 'X', '0', '0', '0', '0', '0', '0', '0', 'X', '0', '0', '0'},
        //         {'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'} };
        printGrid();

        while (move() != -1) {
            System.out.printf("Current state: (%d, %d), Direction: %s\n", x, y, direction);
            if (verbose)
                printGrid();
        }
        System.out.println("\nFinal State:\n");
        printGrid();
        System.out.println();
        System.out.println("Total Moves Made: " + Path.actualMovesMade);
    }
    
    public static int move() {
        switch (direction) {
            case UP:
                if (overallDirection == OverallDirection.LR_StopB || overallDirection == OverallDirection.LR_StopT) {
                    if (x == 0) {
                        if (y == grid[0].length - 1 && overallDirection == OverallDirection.LR_StopT) {
                            grid[x][y] = 'E';
                            return -1;
                        }
                        int downCount = 0;
                        while (!moveRight()) {
                        moveDown();
                            if (++downCount == grid.length - 1) {
                                return -1;
                            }
                        }
                        direction = Direction.DOWN;
                        return 0;
                    } else {
                        moveDir(direction);
                        while (displacement[1] != 0) {
                            if (displacement[1] < 0) {
                                moveDir(Direction.RIGHT);
                            } else if (displacement[1] > 0) {
                                moveDir(Direction.LEFT);
                            }
                        }
                    }
                } else {
                    if (x == 0) {
                        if (y == 0 && overallDirection == OverallDirection.RL_StopT) {
                            grid[x][y] = 'E';
                            return -1;
                        }
                        int downCount = 0;
                        while (!moveLeft()) {
                            moveDown();
                            if (++downCount == grid.length - 1) {
                                return -1;
                            }
                        }
                        direction = Direction.DOWN;
                        return 0;
                    } else {
                        moveDir(direction);
                        while(displacement[1] != 0) {
                            if (displacement[1] < 0) {
                                moveDir(Direction.RIGHT);
                            } else if (displacement[1] > 0) {
                                moveDir(Direction.LEFT);
                            }
                        }
                    }
                }
                break;
            case DOWN:
                if (overallDirection == OverallDirection.LR_StopB || overallDirection == OverallDirection.LR_StopT) {
                    if (x == grid.length - 1) {
                        if (y == grid[0].length - 1 && overallDirection == OverallDirection.LR_StopB) {
                            grid[x][y] = 'E';
                            return -1;
                        }
                        int upCount = 0;
                        while (!moveRight()) {
                            moveUp();
                            if (++upCount == grid[x].length - 1) {
                                return -1;
                            }
                        }
                        direction = Direction.UP;
                        return 0;
                    } else {
                        moveDir(direction);
                        while (displacement[1] != 0) {
                            if (displacement[1] < 0) {
                                moveDir(Direction.RIGHT);
                            } else if (displacement[1] > 0) {
                                moveDir(Direction.LEFT);
                            }
                        }
                    }
                } else {
                    if (x == grid.length - 1) {
                        if (y == 0 && overallDirection == OverallDirection.RL_StopB) {
                            grid[x][y] = 'E';
                            return -1;
                        }
                        int upCount = 0;
                        while (!moveLeft()) {
                            moveUp();
                            if (++upCount == grid[x].length - 1) {
                                return -1;
                            }
                        }
                        direction = Direction.UP;
                        return 0;
                    } else {
                        moveDir(direction);
                        while (displacement[1] != 0) {
                            if (displacement[1] < 0) {
                                moveDir(Direction.RIGHT);
                            } else if (displacement[1] > 0) {
                                moveDir(Direction.LEFT);
                            }
                        }
                    }
                }
            default:
                break;
        }
        return 0;
    }

    private static void moveDir(Direction direction) {
        switch (direction) {
            case UP:
                while (!moveUp()) {
                    moveDir(Direction.RIGHT);
                }
                break;
            case DOWN:
                while (!moveDown()) {
                    if (Path.direction != Direction.DOWN || y == grid[x].length - 1) {
                        moveDir(Direction.LEFT);
                    } else {
                        moveDir(Direction.RIGHT);
                    }
                }
                break;
            case LEFT:
                while (!moveLeft()) {
                    if (Path.direction != Direction.DOWN) {
                        moveDir(Direction.UP);
                    } else {
                        moveDir(Direction.DOWN);
                    }
                }
                displacement[1]--;
                break;
            case RIGHT:
                while (!moveRight()) {
                    moveDir(Direction.DOWN);
                }
                displacement[1]++;
                break;
        }
    }

    private static boolean moveLeft() {
        if (verbose) System.out.println("moveLeft()");
        if (x < 0 || y <= 0) {
            if (verbose) System.out.println("RRN: False, 1st check");
            return false;
        }
        if (grid[x][y - 1] == 'X') {
            if (verbose) System.out.println("RRN: False, 2nd check");
            return false;
        }
        grid[x][y] = '<';
        y--;
        if (verbose) System.out.println("RRN: True");
        moveHook();
        return true;
    }

    private static boolean moveRight() {
        if (verbose) System.out.println("moveRight()");
        if (x >= grid.length || y >= grid[x].length - 1) {
            if (verbose) System.out.println("RRN: False, 1st check");
            return false;
        }
        if (grid[x][y + 1] == 'X') {
            if (verbose) System.out.println("RRN: False, 2nd check");
            return false;
        }
        grid[x][y] = '>';
        y++;
        if (verbose) System.out.println("RRN: True");
        moveHook();
        return true;
    }

    private static boolean moveUp() {
        if (verbose) System.out.println("moveUp()");
        if (x <= 0) {
            if (verbose) System.out.println("RRN: False, 1st check");
            return false;
        }
        if (grid[x - 1][y] == 'X') {
            if (verbose) System.out.println("RRN: False, 2nd check");
            return false;
        }
        grid[x][y] = '^';
        x--;
        if (verbose) System.out.println("RRN: true");
        moveHook();
        return true;
    }

    private static boolean moveDown() {
        if (verbose) System.out.println("moveDown()");
        if (x >= grid.length - 1) {
            if (verbose) System.out.println("RRN: False, 1st check");
            return false;
        }
        if (grid[x + 1][y] == 'X') {
            if (verbose) System.out.println("RRN: False, 2nd check");
            return false;
        }
        grid[x][y] = 'V';
        x++;
        if (verbose) System.out.println("RRN: True");
        moveHook();
        return true;
    }

    static int actualMovesMade = 0;
    private static void moveHook() {
        Path.actualMovesMade++;
    }

    public static void printGrid() {
        for (char[] arr : grid) {
            System.out.println(java.util.Arrays.toString(arr));
        }
    }
}