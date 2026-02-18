import streamlit as st
import random
import time

class MiniSudoku:
    def __init__(self):
        # A simple hardcoded 4x4 Sudoku with solution and puzzle mask (0 is empty)
        # Format: (Solution Grid, Puzzle Mask)
        # Grid values: 1-4
        
        self.puzzles = [
            (
                [[1, 2, 3, 4], 
                 [3, 4, 1, 2], 
                 [2, 1, 4, 3], 
                 [4, 3, 2, 1]], 
                [[1, 0, 0, 4], 
                 [0, 4, 1, 0], 
                 [0, 1, 4, 0], 
                 [4, 0, 0, 1]]
            ),
            (
                [[4, 3, 2, 1], 
                 [1, 2, 3, 4], 
                 [3, 4, 1, 2], 
                 [2, 1, 4, 3]],
                [[0, 3, 2, 0], 
                 [1, 0, 0, 4], 
                 [3, 0, 0, 2], 
                 [0, 1, 4, 0]]
            )
        ]

    def get_puzzle(self):
        """Returns a random puzzle (puzzle_grid, solution_grid)"""
        return random.choice(self.puzzles)

    def render_game(self):
        st.subheader("🧩 Mini-Sudoku For Focus")
        st.markdown("Solve this 4x4 puzzle! Use numbers 1-4. Each row, column, and 2x2 box must contain unique numbers.")
        
        if 'sudoku_board' not in st.session_state:
            solution, puzzle = self.get_puzzle()
            st.session_state.sudoku_solution = solution
            st.session_state.sudoku_board = puzzle
            st.session_state.game_start_time = time.time()
            st.session_state.game_completed = False

        # Render Grid using columns
        user_solution = []
        is_complete = True
        
        # Check if already solved correctly
        if st.session_state.game_completed:
             st.success("🎉 Puzzle Solved! Focus Score: 10/10")
             return True, 10, st.session_state.get('sudoku_attempts', 1) # Completed, Score, Attempts

        grid = st.session_state.sudoku_board
        
        if 'sudoku_attempts' not in st.session_state:
            st.session_state.sudoku_attempts = 0

        with st.form("sudoku_form"):
            for i in range(4):
                cols = st.columns(4)
                row_vals = []
                for j in range(4):
                    val = grid[i][j]
                    with cols[j]:
                        if val != 0:
                            st.write(f"**{val}**") # Fixed value
                            row_vals.append(val)
                        else:
                            # User input
                            key = f"cell_{i}_{j}"
                            user_val = st.number_input(" ", min_value=1, max_value=4, step=1, key=key, label_visibility="collapsed")
                            row_vals.append(user_val)
                user_solution.append(row_vals)
            
            submitted = st.form_submit_button("Check Solution")
            
            if submitted:
                st.session_state.sudoku_attempts += 1
                if user_solution == st.session_state.sudoku_solution:
                    st.session_state.game_completed = True
                    elapsed = time.time() - st.session_state.game_start_time
                    score = max(10 - int(elapsed / 10), 5) # Faster = Higher Score
                    st.success(f"Correct! Time: {elapsed:.1f}s. Mental Focus Score: {score}/10")
                    return True, score, st.session_state.sudoku_attempts
                else:
                    st.error("Incorrect. Try again!")
                    return False, 0, st.session_state.sudoku_attempts
        
        return False, 0, st.session_state.sudoku_attempts

