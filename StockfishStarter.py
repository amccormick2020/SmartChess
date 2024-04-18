import chess
from stockfish import Stockfish

# Function to get human player's move
def get_human_move(board):
  while True:
    human_move = input("Enter your move (e.g., e2e4): ")
    try:
      move = chess.Move.from_uci(human_move)
      if move in board.legal_moves:
        return move
      else:
        print("Invalid move. Please try again.")
    except ValueError:
      print("Invalid move format. Please use UCI notation (e.g., e2e4).")

# Function to get the best move from Stockfish
def get_best_move_from_stockfish(board_state):
  stockfish = Stockfish(depth=10)  # Adjust search depth as needed
  stockfish.set_position(board_state)
  best_move = stockfish.get_best_move()
  stockfish.quit()
  return best_move

# Function to print the board in a user-friendly format
def print_board(board):
  ranks = '8 7 6 5 4 3 2 1'.split()
  files = 'abcdefgh'

  print('   ', end='')
  for f in files:
    print(f, end=' ')
  print()

  for r in ranks:
    print(r, end='  ')
    for f in files:
      piece = board.piece_at(chess.square(f, int(r)))
      if piece is None:
        print('-', end=' ')
      else:
        print(piece.symbol(), end=' ')
    print()

  print('  ', end='')
  for f in files:
    print(f, end=' ')
  print()


def main():
  # Initialize the chessboard and engine
  engine = Stockfish(depth=10)  # Adjust search depth as needed
  board = chess.Board()

  # Main game loop
  while True:
    print_board(board)

    # Get human player's move
    human_move = get_human_move(board)
    board.push(human_move)

    # Check for game over or other conditions
    if board.is_game_over():
      result = board.result()
      print(result)
      break

    # Get the best move from Stockfish
    best_move = get_best_move_from_stockfish(board.fen())
    print(f"Computer plays: {best_move}")

    # Play the computer's move using Stockfish engine
    engine.play(board, chess.Move.from_uci(best_move))

# Run the main game loop  
if __name__ == "__main__":
  main()
  
