import RPi.GPIO as GPIO
import time
import pychess # INSTALL LIBRARY

# Define GPIO pins for LEDs (replace with your actual pin assignments)
LED_PINS = [18, 23, 24, 25]  # Example for the first 4 pins

# Define GPIO pins for hall effect sensors (replace with your actual pin assignments)
SENSOR_PINS = [4, 17, 27, 22]  # Example for the first 4 pins

# Chessboard rank and file constants for LED mapping (adjust based on your LED layout)
RANK_TO_LED = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7}
FILE_TO_LED = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PULLUP)

# Function to turn on a specific LED
def light_up_led(pin):
    GPIO.output(pin, GPIO.LOW)  # LEDs are typically active low

# Function to turn off a specific LED
def turn_off_led(pin):
    GPIO.output(pin, GPIO.HIGH)

# Function to read a single sensor
def read_sensor(pin):
    return GPIO.input(pin) == GPIO.LOW  # Sensor active low

# Function to convert pychess square coordinates to LED index
def get_led_index(square):
    rank, file = square
    return RANK_TO_LED[rank] * 8 + FILE_TO_LED[file]

# Function to update LEDs based on pychess move
def update_leds_with_move(move):
    # Get origin and destination squares from the move
    origin_square, destination_square = move.uci()[:2], move.uci()[2:]

    # Turn off LEDs for the origin and destination squares
    turn_off_led(get_led_index(origin_square))
    turn_off_led(get_led_index(destination_square))

    # Simulate a small delay to visualize the move (optional)
    time.sleep(0.2)

    # Turn on the LED for the destination square (assuming the move is valid)
    light_up_led(get_led_index(destination_square))

# Function to get user move from sensor (possibly from another file?) TO BE IMPLEMENTED
def get_user_move_from_sensor(sensor_pins):
    # Read sensor states
    sensor_states = [GPIO.input(pin) for pin in sensor_pins]

    # Implement specific mapping logic to convert sensor states to a chess move
    # This logic might involve checking combinations of sensor states and translating them to the corresponding chess move in Standard Algebraic Notation (SAN)

    # Example (replace with actual mapping):
    if sensor_states[0] == 0 and sensor_states[1] == 1:
        return "a2a3"  # Example mapping for sensor combination A-B
    else:
        return None  # Return None for invalid sensor combination

def main():
    # Set up GPIO pins and initialize chessboard (replace with our actual setup)
    try:
        GPIO.setmode(GPIO.BCM)
        for pin in LED_PINS:
            GPIO.setup(pin, GPIO.OUT)
        for pin in SENSOR_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PULLUP)
    except RuntimeError as e:
        print(f"Error setting up GPIO pins: {e}")
        return

    board = pychess.Board()

    # Game loop
    while True:
        # Get user move from sensor, ensuring validity and proper format 
        user_move = get_user_move_from_sensor(SENSOR_PINS) #TO BE IMPLEMENTED
        if not user_move or not pychess.Move.from_uci(user_move):
            print("Invalid sensor input. Please try again.")
            continue

        # Make the move on the chessboard
        board.push_san(user_move)

        # Update LEDs based on the move (replace with our LED mapping)
        update_leds_with_move(get_led_index(user_move))

        # Check for game end conditions (checkmate, stalemate, etc.)
        if board.is_game_over():
            print(f"Game over! {board.result()}")
            break

        # Implement AI move using a chess engine
        # Replace with our integration logic
        ai_engine = pychess.engine.AlphaZeroEngine()  # Example
        ai_move = ai_engine.play(board).move
        if ai_move:
            board.push_san(str(ai_move))  # Convert engine move to SAN format
            update_leds_with_move(get_led_index(str(ai_move)))  # Update LEDs using SAN

    # Clean up GPIO pins
    GPIO.cleanup()

if __name__ == "__main__":
    main()
