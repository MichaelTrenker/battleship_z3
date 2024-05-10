from z3 import *

# Initialize the Z3 Solver
solver = Solver()

# Define the grid size
grid_size = 4

# Define the size of the entity
entity_size = 3

# Variable to track the number of ways to fit the entity
placement_count = 0

# Array to keep track of the number of times each cell is part of the entity
cell_usage_count = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

# Define deactivated cells - specify them as a set of (row, col) tuples
# Example: deactivated_cells = {(1, 2), (3, 1)} means cells (1,2) and (3,1) are deactivated
deactivated_cells = []
while True:
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

                # Ensure no other cells are occupied and check deactivated cells
                for r in range(grid_size):
                    for c in range(grid_size):
                        if (r, c) in deactivated_cells or not (r == row and col <= c < col + entity_size):
                            solver.add(Not(grid[r][c]))

                # Check if this setup is possible
                if solver.check() == sat:
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

                # Ensure no other cells are occupied and check deactivated cells
                for r in range(grid_size):
                    for c in range(grid_size):
                        if (r, c) in deactivated_cells or not (c == col and row <= r < row + entity_size):
                            solver.add(Not(grid[r][c]))

                # Check if this setup is possible
                if solver.check() == sat:
                    placement_count += 1
                    # Increment the usage count for each involved cell
                    for r in range(row, row + entity_size):
                        cell_usage_count[r][col] += 1

    # Print the total number of placements found
    print(f"Total placements: {placement_count}")

    # Print the usage count for each cell
    print("Cell usage counts:")
    for r in range(grid_size):
        for c in range(grid_size):
            print(f"Cell ({r}, {c}): {(cell_usage_count[r][c]*100)/4}", end="  ")
            cell_usage_count[r][c] = 0
        print()
    x = int(input("Enter the X-Coordinate of you Shoot: "))

    # Read second integer from user input
    y = int(input("Enter the Y-Coordinate of you Shoot: "))
    deactivated_cells.append((x,y))
    
