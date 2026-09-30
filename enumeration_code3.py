from typing import Any, Dict, List, Tuple

def evaluate(prog: Any, env: Dict[str, int]) -> int:
    """Recursively evaluates an AST represented as nested tuples."""
    # Base case: Terminal (variable or constant)
    if isinstance(prog, str):
        if prog in env:
            return env[prog]
        return int(prog)
    
    # Recursive case: Binary operation
    op, left, right = prog
    l_val = evaluate(left, env)
    r_val = evaluate(right, env)
    
    if op == '+': return l_val + r_val
    if op == '-': return l_val - r_val
    if op == '*': return l_val * r_val
    raise ValueError(f"Unknown operator: {op}")

def to_polish(prog: Any) -> str:
    """Converts the tuple AST into a Polish notation string."""
    if isinstance(prog, str):
        return prog
    op, left, right = prog
    return f"{op} {to_polish(left)} {to_polish(right)}"

def synthesize(examples: List[Tuple[int, int, int]], max_size: int = 15) -> str:
    """
    Finds the smallest program in Polish notation that satisfies all examples.
    examples format: [(i_1, i_2, expected_output), ...]
    """
    terminals = ['x', 'y', '0', '1', '2']
    operators = ['+', '-', '*']
    
    # bank maps AST size -> list of valid programs of exactly that size
    bank: Dict[int, List[Any]] = {1: []}
    
    # Pruning cache to store output signatures we've already seen
    seen_signatures = set()
    
    # The exact output signature we want to achieve
    target_sig = tuple(expected for _, _, expected in examples)
    
    def process_candidate(prog: Any, size: int) -> bool:
        """Evaluates program, prunes if redundant, saves it if valid, returns True if it's the solution."""
        sig = []
        for i_1, i_2, _ in examples:
            try:
                res = evaluate(prog, {'x': i_1, 'y': i_2})
                # Prevent massive integer overflows during eval (e.g., x * x * x ...)
                if abs(res) > 10**8: 
                    return False
                sig.append(res)
            except Exception:
                return False
                
        sig_tuple = tuple(sig)
        
        # Observational Equivalence Pruning:
        # If a smaller/equal program already produced these exact outputs across all examples, 
        # this program is functionally identical but larger. Discard it.
        if sig_tuple in seen_signatures:
            return False
            
        seen_signatures.add(sig_tuple)
        bank[size].append(prog)
        
        # Check if it solves the problem
        return sig_tuple == target_sig

    # Step 1: Initialize the bank with size 1 programs (terminals)
    for t in terminals:
        if process_candidate(t, 1):
            return to_polish(t)
            
    # Step 2: Build larger programs dynamically (size = 1 operator + size of left + size of right)
    for size in range(2, max_size + 1):
        bank[size] = []
        
        # To get a tree of total `size`, the left and right children must sum to `size - 1`
        for left_size in range(1, size - 1):
            right_size = size - 1 - left_size
            
            for left in bank[left_size]:
                for right in bank[right_size]:
                    for op in operators:
                        prog = (op, left, right)
                        
                        if process_candidate(prog, size):
                            return to_polish(prog)
                            
    raise ValueError(f"No valid program found up to size {max_size}.")

# --- Example Usage ---
if __name__ == "__main__":
    # Test Case 1: Simple Addition
    # 1+2=3, 4+5=9, 0+7=7 -> Expected: + x y
    examples_1 = [
        (1, 2, 3),
        (4, 5, 9),
        (0, 7, 7)
    ]
    
    # Test Case 2: x^2 - y
    # 3^2 - 2 = 7; 4^2 - 5 = 11; 2^2 - 4 = 0 -> Expected: - * x x y
    examples_2 = [
        (3, 2, 7),
        (4, 5, 11),
        (2, 4, 0)
    ]

    print(f"Test 1 Solution: {synthesize(examples_1)}")
    print(f"Test 2 Solution: {synthesize(examples_2)}")