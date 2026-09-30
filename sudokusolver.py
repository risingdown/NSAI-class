pip install z3-solver

def solve_sudoku_smt(grid):
    """
    Solves a 9x9 Sudoku puzzle using the Z3 Theorem Prover.
    Empty cells should be represented by 0.
    """
    # 1. Create a 9x9 matrix of Z3 Integer variables
    X = [[z3.Int(f'cell_{r}_{c}') for c in range(9)] for r in range(9)]
    
    solver = z3.Solver()
    
    # 2. Domain Constraint: Every cell must be between 1 and 9
    for r in range(9):
        for c in range(9):
            solver.add(X[r][c] >= 1, X[r][c] <= 9)
            
    # 3. Row and Column Constraints: All values in a row/col must be unique
    for i in range(9):
        solver.add(z3.Distinct(X[i])) # Row 'i'
        solver.add(z3.Distinct([X[r][i] for r in range(9)])) # Column 'i'
        
    # 4. Block Constraints: All values in each 3x3 subgrid must be unique
    for block_r in range(3):
        for block_c in range(3):
            block_cells = [
                X[block_r * 3 + dr][block_c * 3 + dc] 
                for dr in range(3) for dc in range(3)
            ]
            solver.add(z3.Distinct(block_cells))
            
    # 5. Clue Constraints: Apply the known values from the input grid
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                solver.add(X[r][c] == grid[r][c])
                
    # 6. Solve and Extract Model
    if solver.check() == z3.sat:
        model = solver.model()
        # Evaluate each Z3 variable to extract the integer solution
        solution = [
            [model.evaluate(X[r][c]).as_long() for c in range(9)] 
            for r in range(9)
        ]
        return solution
    else:
        return None

def print_board(board):
    if not board:
        print("No solution exists.")
        return
        
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)
        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += "| "
            row_str += str(board[r][c]) + " "
        print(row_str.strip())

# --- Example Usage ---
if __name__ == "__main__":
    # 0 represents an empty square
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    print("--- Initial Puzzle ---")
    print_board(puzzle)
    
    solved_grid = solve_sudoku_smt(puzzle)
    
    print("\n--- Solved Puzzle ---")
    print_board(solved_grid)