import random
from z3 import *
BOARD_SIZE = 3
SHIPS = [3]  # Example: A ship of size 3
NUM_SHIPS = len(SHIPS)
MAX_LENGTH_SHIP = max(SHIPS)
HIT_VALUE = "1"  # Value representing a hit in the board
MISS_VALUE = "-1"  # Value representing a miss in the board
UNCHECKED_VALUE = "0" # Value representing an unchecked field in the board
solver = Solver()

# Create a boolean variable for each cell to indicate if a ship part may be present
ship_cells = [[Bool(f"ship_{r}_{c}") for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]

# Initialize the board with 0 (unbombarded)
def initialize_board(board_size):
    return [[UNCHECKED_VALUE for _ in range(board_size)] for _ in range(board_size)]

# Place a ship on the board
def place_ship(board, ship_length):
    placed = False
    while not placed:
        row = random.randint(0, BOARD_SIZE - 1)
        col = random.randint(0, BOARD_SIZE - 1)
        orientation = random.choice(['horizontal', 'vertical'])
        if orientation == 'horizontal':
            if col + ship_length <= BOARD_SIZE and all(board[row][c] == '0' for c in range(col, col + ship_length)):
                for i in range(ship_length):
                    board[row][col + i] = 'S'
                placed = True
        else:
            if row + ship_length <= BOARD_SIZE and all(board[r][col] == '0' for r in range(row, row + ship_length)):
                for i in range(ship_length):
                    board[row + i][col] = 'S'
                placed = True

def print_board(board):
    for row in board:
        print(' '.join(row))
    print()

def update_visible_board(visible_board, hidden_board, row, col):
    constraints = []
    if hidden_board[row][col] == 'S':
        print("Hit!")
        visible_board[row][col] = HIT_VALUE  # H for Hit
    else:
        print("Miss!")
        visible_board[row][col] = MISS_VALUE  # M for Miss

def add_battleship_constraints():
    already_hit = False
    solver.reset()
    constraints = []

    # Constraints that ensure the ships occupy a continuous line of cells horizontally or vertically
    for SHIP_SIZE in SHIPS:

        possible_ship_placements = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if visible_board[r][c] == HIT_VALUE:
                    constraints.append(ship_cells[r][c])
                    already_hit = True

                elif visible_board[r][c] == MISS_VALUE:
                    constraints.append(z3.Not(ship_cells[r][c]))
                elif visible_board[r][c] == UNCHECKED_VALUE and already_hit == False:
                    constraints.append(ship_cells[r][c])
        
        already_hit = any(cell == '1' for row in visible_board for cell in row)

        if already_hit:
            # Scan for hit coordinates and add constraints based on that
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    if visible_board[row][col] == '1':
                        # Horizontal possibilities incorporating the hit
                        for offset in range(min(SHIP_SIZE, col + 1)):
                            if col - offset >= 0 and col - offset + SHIP_SIZE <= BOARD_SIZE:
                                segment = [ship_cells[row][col - offset + i] for i in range(SHIP_SIZE)]
                                if all(visible_board[row][col - offset + i] in ['1', '0'] for i in range(SHIP_SIZE)):
                                    possible_ship_placements.append(And(segment))

                        # Vertical possibilities incorporating the hit
                        for offset in range(min(SHIP_SIZE, row + 1)):
                            if row - offset >= 0 and row - offset + SHIP_SIZE <= BOARD_SIZE:
                                segment = [ship_cells[row - offset + i][col] for i in range(SHIP_SIZE)]
                                if all(visible_board[row - offset + i][col] in ['1', '0'] for i in range(SHIP_SIZE)):
                                    possible_ship_placements.append(And(segment))
        else:
            # Add constraints for all cells if no hit has been recorded
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE - SHIP_SIZE + 1):
                    segment = [ship_cells[r][c + i] for i in range(SHIP_SIZE)]
                    if all(visible_board[r][c + i] in ['0'] for i in range(SHIP_SIZE)):
                        possible_ship_placements.append(And(segment))

            for c in range(BOARD_SIZE):
                for r in range(BOARD_SIZE - SHIP_SIZE + 1):
                    segment = [ship_cells[r + i][c] for i in range(SHIP_SIZE)]
                    if all(visible_board[r + i][c] in ['0'] for i in range(SHIP_SIZE)):
                        possible_ship_placements.append(And(segment))

        # Add constraint that exactly one ship placement is valid
        solver.add(Or(possible_ship_placements))

            # Add constraints based on the current hits, misses and not checked fields
        solver.add(constraints)

def display_all_possibilities():
    possible_placements = initialize_board(BOARD_SIZE)
    blocking_clause = []
    solution_count = 0
    while solver.check() == sat:
        solution_count += 1
        model = solver.model()
        print(model)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if is_true(model.evaluate(ship_cells[row][col])):
                    possible_placements[row][col] = "S"
                    blocking_clause.append(ship_cells[row][col] == False)
                else:
                    blocking_clause.append(ship_cells[row][col] == True)
         # Add the blocking clause to the solver
        solver.add(Or(blocking_clause))
        if solution_count == 10:
            break
    print(f"Solution {solution_count}:")
    for i in range(BOARD_SIZE):
        print(possible_placements[i])
    if solution_count == 0:
        print("No possible ship configurations found with the given constraints.")






if __name__ == "__main__":
    hidden_board = initialize_board(BOARD_SIZE)
    visible_board = initialize_board(BOARD_SIZE)
    

    for ship in SHIPS:
        place_ship(hidden_board, ship)

    print("Let's play Battleship!")
    while True:
        try:        
            print_board(visible_board)
            operation = str(input("shoot | prob:"))
            if operation == "shoot":
                row = int(input("Enter row (0-indexed): "))
                col = int(input("Enter column (0-indexed): "))
                if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
                    print("Coordinates out of bounds. Try again.")
                    continue
                if visible_board[row][col] == HIT_VALUE or visible_board [row][col] == MISS_VALUE:  # Already guessed
                    print("You've already guessed that. Try again.")
                    continue
                update_visible_board(visible_board, hidden_board, row, col)
            elif operation == "prob":
                add_battleship_constraints()
                display_all_possibilities()
            else: 
                print("Operation is not valid")
        except ValueError:
            print("Invalid input. Please enter numeric values.")