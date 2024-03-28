import RPi.GPIO as GPIO
import time
import chess

input_pins = [14, 22, 27, 17, 10, 9, 11, 0]  # Mux outputs
select_pins = [2, 3, 4]  # Mux select lines (S2, S1, S0)
start_button = 25

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN)
for pin in select_pins:
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(start_button, GPIO.IN)

board = chess.Board()

# Invert signal since Hall effect sensors output 1 with no magnet and 0 with a magnet present
def read_sensor(input_channel):
    if GPIO.input(input_channel):
        return 0  # Assuming 0 means no magnet detected
    else:
        return 1  # Assuming 1 means magnet detected

# Function to swap between select line combinations
def select_mux_channel(channel):
    
    # Set select lines according to the channel number (0-7)
    for i, pin in enumerate(select_pins):
        GPIO.output(pin, channel & (1 << i))

def print_8x8_matrix(sensor_values):
    matrix = []
    
    # Construct the 8x8 matrix from sensor values
    for i in range(8):  # For each row
        row = []
        for sensor_group in sensor_values:  # For each sensor group
            row.extend(sensor_group[i*2:(i+1)*2])
        matrix.append(row)
    
    # Print the 8x8 matrix
    for row in matrix:
        print(row)
    print()
    
    return matrix

# Function to swap sensor values to resemble physical sensor layout per 4x2 chunk
def swap_values(chunk):
    
    # Swap top left with bottom left
    chunk[0], chunk[6] = chunk[6], chunk[0]
    # Swap right upper middle with right lower middle
    chunk[3], chunk[5] = chunk[5], chunk[3]
    return chunk

def chess_matrix_converter(binary_matrix):
    """Convert binary matrix to a chessboard setup matrix if correctly set up."""
    # Define the initial setup for chess pieces on an 8x8 board
    initial_setup = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]
    
    # Check if the board is set up correctly (top two and bottom two rows are all 1s)
    if all(all(row) for row in binary_matrix[:2] + binary_matrix[-2:]):
        print('Match Initiated')
        return initial_setup
    else:
        print("The board is set up incorrectly.")
        return None

def sensor_to_square(row, col):
    # Assuming row and col are 0-indexed and map directly to squares
    # Adjust if your sensor mapping is different
    file = chr(ord('a') + col)
    rank = 8 - row
    return file + str(rank)

def generate_legal_moves(square):
    """
    Generate legal moves for the piece on the given square.
    """
    moves = list(board.legal_moves)
    legal_moves = [move.uci() for move in moves if move.from_square == chess.parse_square(square)]
    return legal_moves

def main():
    last_sensor_values = {pin: [None] * 8 for pin in input_pins}
    
    try:
        while True:
            current_sensor_values = {pin: [] for pin in input_pins}
            for channel in range(8):
                select_mux_channel(channel)
                # Small delay to ensure the select lines have settled
                time.sleep(0.01)
                for pin in input_pins:
                    current_sensor_values[pin].append(read_sensor(pin))
                    
            for pin in input_pins:
                current_sensor_values[pin] = swap_values(current_sensor_values[pin])        
            # Check if there's any change in sensor values
            if any(current_sensor_values[pin] != last_sensor_values[pin] for pin in input_pins):
                matrix = print_8x8_matrix([
                    current_sensor_values[10], current_sensor_values[9], 
                    current_sensor_values[11], current_sensor_values[0], 
                    current_sensor_values[14], current_sensor_values[22], 
                    current_sensor_values[27], current_sensor_values[17]
                ])
                ############# convert binary matrix to type matrix
                
                piece_picked_up = None
                for row_idx, row in enumerate(matrix):
                    for col_idx, value in enumerate(row):
                        if last_sensor_values[input_pins[col_idx % 8]][row_idx] == 1 and value == 0:

                            time.sleep(0.1) # Wait in case piece was accidentally moved
                            if value == 0:
                                piece_picked_up = (row_idx, col_idx)
                            break
                    if piece_picked_up:
                        break
                
                if piece_picked_up:
                    print(f"Piece picked up at: {sensor_to_square(*piece_picked_up)}")
                    legal_moves = generate_legal_moves(piece_picked_up)
                    print(f"Legal moves: {legal_moves}")
                

                if GPIO.input(start_button):  # Check if setup_pin is high
                    char_matrix = chess_matrix_converter(matrix)
                    if char_matrix:
                        # The char_matrix can now be used for further processing
                        print("Board Set Up Correctly, White moves first:")
                        for row in char_matrix:
                            print(row)
                        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                        board.set_fen(fen)

                last_sensor_values = current_sensor_values.copy()
                
            # Delay between readings
            time.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
