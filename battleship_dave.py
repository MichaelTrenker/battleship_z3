from z3 import *
import argparse, random

def random_ship_position_generic(grid_size, entity_size, ship_playground):
    # Create a random row and column for the starting position of the ship
    start_row = random.randint(0, grid_size - 1)
    start_col = random.randint(0, grid_size - 1)

    # Randomly choose whether the ship will be placed horizontally or vertically
    is_horizontal = random.choice([True, False])

    if is_horizontal:
        # Check if there's enough space horizontally and no overlap or adjacency with existing ships
        if start_col + entity_size < grid_size and \
                all(ship_playground[start_row][start_col + i] == 0 for i in range(entity_size)) and \
                all(all(ship_playground[r][c] == 0 for c in range(max(0, start_col - 1), min(grid_size, start_col + entity_size + 1))) for r in range(max(0, start_row - 1), min(grid_size, start_row + 2))):
            return start_row, start_col, is_horizontal
    else:
        # Check if there's enough space vertically and no overlap or adjacency with existing ships
        if start_row + entity_size < grid_size and \
                all(ship_playground[start_row + i][start_col] == 0 for i in range(entity_size)) and \
                all(all(ship_playground[r][c] == 0 for c in range(max(0, start_col - 1), min(grid_size, start_col + 2))) for r in range(max(0, start_row - 1), min(grid_size, start_row + entity_size + 1))):
            return start_row, start_col, is_horizontal
    
    # If no valid position is found, recursively try again
    return random_ship_position_generic(grid_size, entity_size, ship_playground)

def calculate_ship_cell_usage(grid_size, entity_size, deactivated_cells, sure_cells, placement_count):
    # Initialize the Z3 Solver
    solver = Solver()

    # Array to keep track of the number of times each cell is part of an entity
    cell_usage_count = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

    # Iterate over all possible positions in the grid
    for row in range(grid_size):
        for col in range(grid_size):
            # Reset the solver for this position
            solver.reset()

            # Create a 4x4 grid of boolean variables
            grid = [[Bool(f"cell_{r}_{c}") for c in range(grid_size)] for r in range(grid_size)]

            # Assume the entity starts at (row, col) and goes horizontally
            if col + entity_size <= grid_size:
                # Set constraints for horizontal placement
                horizontal_constraints = [grid[row][c] for c in range(col, col + entity_size)]
                solver.add(And(horizontal_constraints))

                # Ensure no other cells are occupied, check deactivated and sure cells
                valid_placement = True
                for r in range(grid_size):
                    for c in range(grid_size):
                        if (r, c) in deactivated_cells or not (r == row and col <= c < col + entity_size):
                            solver.add(Not(grid[r][c]))
                        if (r, c) in sure_cells:
                            if not (r == row and col <= c < col + entity_size):
                                valid_placement = False

                # Check if this setup is possible and includes sure cells
                if valid_placement and solver.check() == sat:
                    placement_count += 1
                    # Increment the usage count for each involved cell
                    for c in range(col, col + entity_size):
                        cell_usage_count[row][c] += 1

            # Reset the solver again for vertical placement
            solver.reset()
            if row + entity_size <= grid_size:
                # Set constraints for vertical placement
                vertical_constraints = [grid[r][col] for r in range(row, row + entity_size)]
                solver.add(And(vertical_constraints))

                # Ensure no other cells are occupied, check deactivated and sure cells
                valid_placement = True
                for r in range(grid_size):
                    for c in range(grid_size):
                        if (r, c) in deactivated_cells or not (c == col and row <= r < row + entity_size):
                            solver.add(Not(grid[r][c]))
                        if (r, c) in sure_cells:
                            if not (c == col and row <= r < row + entity_size):
                                valid_placement = False

                # Check if this setup is possible and includes sure cells
                if valid_placement and solver.check() == sat:
                    placement_count += 1
                    # Increment the usage count for each involved cell
                    for r in range(row, row + entity_size):
                        cell_usage_count[r][col] += 1

    return cell_usage_count, placement_count


def main():
    # Create a parser object
    parser = argparse.ArgumentParser(description="A script that requires -real or -debug to run.")
    
    # Define the arguments
    # Use 'store_true' as the action to simply store True if the argument is present.
    parser.add_argument('-real', action='store_true', help='Run the script in real mode')
    parser.add_argument('-debug', action='store_true', help='Run the script in debug mode')

    # Parse the arguments
    args = parser.parse_args()
    
    # Check the conditions based on the provided arguments
    if args.real:
        print("Running in real mode...")
        # Add your real mode code here
    elif args.debug:
        print("Running in debug mode...")
        # Add your debug mode code here
    else:
        # If neither -real nor -debug are provided, print the help text
        parser.print_help()
        exit()

    # Define the grid size
    grid_size = 4

    # Define the size of the entity
    entity_size = 3

    # Variable to track the number of ways to fit the entity
    placement_count = 0
    shot_counter = 0

    # Define deactivated cells - specify them as a set of (row, col) tuples
    # Example: deactivated_cells = {(1, 2), (3, 1)} means cells (1,2) and (3,1) are deactivated
    deactivated_cells = []
    sure_cells = []

    # Initialize the ship and shot playground with zeros
    ship_playground = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    shot_playground = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

    # Get a random ship position for the first ship
    start_row_1, start_col_1, is_horizontal_1 = random_ship_position_generic(grid_size, entity_size, ship_playground)

    # Place the first ship in the ship playground
    if is_horizontal_1:
        for i in range(entity_size):
            ship_playground[start_row_1][start_col_1 + i] = 1
    else:
        for i in range(entity_size):
            ship_playground[start_row_1 + i][start_col_1] = 1

    """ Does not work for now
    # Get a random ship position for the second ship
    start_row_2, start_col_2, is_horizontal_2 = random_ship_position_generic(grid_size, entity_size-1, ship_playground)

    # Place the second ship in the ship playground
    if is_horizontal_2:
        for i in range(entity_size-1):
            ship_playground[start_row_2][start_col_2 + i] = 1
    else:
        for i in range(entity_size-1):
            ship_playground[start_row_2 + i][start_col_2] = 1
    """

    while True:
        cell_usage_count, placement_count = calculate_ship_cell_usage(grid_size, entity_size, deactivated_cells, sure_cells, placement_count)

        # Print the usage count for each cell
        print("\nCell usage counts:")
        total = 0
        for r in range(grid_size):
            for c in range(grid_size):
                total = total + cell_usage_count[r][c]
        if args.debug:
            for r in range(grid_size):
                for c in range(grid_size):   
                    print(ship_playground[r][c], end="  ") 
                print()
        
        print("-" * (26 * grid_size + grid_size - 1))
        for r in range(grid_size):
            for c in range(grid_size):
                if sure_cells:
                    print(f"Cell ({r}, {c}): {((cell_usage_count[r][c])/cell_usage_count[sure_cells[0][0]][sure_cells[0][1]]):.3f}% ({cell_usage_count[r][c]})", end="  ")
                else:
                    print(f"Cell ({r}, {c}): {((cell_usage_count[r][c])/total):.3f}% ({cell_usage_count[r][c]})", end=" ")
                if c != grid_size - 1:
                    print(" || ", end="")
            print()
            if r != grid_size - 1:
                print("-" * (26 * grid_size + grid_size - 1))
        print("-" * (26 * grid_size + grid_size - 1))

        for r in range(grid_size):
            for c in range(grid_size):   
                cell_usage_count[r][c] = 0
        x = int(input("Enter the first Coordinate of your Shoot: "))

        # Read second integer from user input
        y = int(input("Enter the second Coordinate of your Shoot: "))
        if ship_playground[x][y] == 1:
            sure_cells.append((x,y))
            shot_playground[x][y] = 1
            print("Wow, you hit a ship!!!\n")
        else:
            print("Miss ;(\n")
            deactivated_cells.append((x,y))
            shot_playground[x][y] = 0

        shot_counter += 1
        
        # Print the updated playground after each shot
        print("Updated Playground:")
        for r in range(grid_size):
            for c in range(grid_size):
                print(shot_playground[r][c], end="  ")
            print()
        
        # Check if all ships have been hit
        if ship_playground == shot_playground:
            print(f"\nCongratulations! You've sunk all the ships and needed {shot_counter} shots for it!")
            break

if __name__ == "__main__":
    main()
