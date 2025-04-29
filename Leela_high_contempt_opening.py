# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 08:15:00 2025

@author: User
"""

import chess
import chess.engine

# Replace with the actual path to your Lc0 engine
lc0_path = r"something/lc0.exe"  # User to supply this path. #Set the temperature to 0.5 in the config.
stockfish_path = r"something/stockfish.exe"  # Adjust as needed

# Initialize the engines
lc0 = chess.engine.SimpleEngine.popen_uci(lc0_path)
stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)

stockfish.configure({"Threads": 16})
# Parameters
num_lines = 1000         # Number of opening lines to generate
max_depth = 25           # Maximum half-moves (12.5 full moves)
short_time = chess.engine.Limit(time=0.01,nodes=1000)  # 0.00001s for move selection (adds noise)
eval_time = chess.engine.Limit(time=0.01)   # 1s for evaluation
long_eval_time = chess.engine.Limit(time=0.5)
preliminary_threshold = 75
threshold = 90          # 1.0 pawn in centipawns
difference_threshold = 50

# List to store positions where Stockfish is weak
selected_fens = []

print("Warming up leela.")
lc0.analyse(chess.Board(), chess.engine.Limit(time=10))
print("Warming up Stockfish.")
stockfish.analyse(chess.Board(), chess.engine.Limit(time=10))
lc0.configure({"Contempt": 100})

already_played = set()
# Generate opening lines
for line in range(num_lines):
    board = chess.Board()
    print ("line:", line)
    for depth in range(max_depth):
        #print("depth: ",depth)
        # Lc0 selects a move with high contempt
        result = lc0.play(board, short_time)
        move = result.move
        board.push(move)
        if board.is_game_over():
            break #In a very rare case where the game is over, break.
        
        if board.fen() in already_played:
            continue
        already_played.add(board.fen())
        # Evaluate the position with both engines
        stockfish_info = stockfish.analyse(board, eval_time)
        stockfish_score = stockfish_info['score'].white().score(mate_score=10000)

        # Convert scores to numerical values, handling mate score.
        if abs(stockfish_score) > 50:
            stockfish_info = stockfish.analyse(board, long_eval_time)
            stockfish_score = stockfish_info['score'].white().score(mate_score=10000)

            # Convert scores to numerical values, handling mate scores
            if 70<=abs(stockfish_score)<=130:
                selected_fens.append(board.fen())
                print(board.fen(),"added")
                break

# Save selected positions to a file
with open("UHO_Alice.epd", "w") as f:
    for fen in selected_fens:
        f.write(fen + "\n")

# Clean up
lc0.quit()
stockfish.quit()