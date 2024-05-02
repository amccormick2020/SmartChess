import RPi.GPIO as GPIO
import time
from rpi_ws281x import *
import chess

# Pin Definitions
input_pins = [14, 22, 27, 17, 10, 9, 11, 0]  # Mux outputs connected here, including the new GPIO pin 22
select_pins = [2, 3, 4]  # Mux select lines (S2, S1, S0)

ROWS = 8  # Chessboard rows & cols
NUM_SPACES = 64


''' --- LED CONFIGURATION --- '''
TOTAL_SKIPPED_LEDS = 8 + 14     # the column of 8 LEDs in the middle that need to be off + the overhanging LEDs on the outside of the board (looping)
LED_COUNT = NUM_SPACES + TOTAL_SKIPPED_LEDS

# colors
BRIGHT_WHITE = Color(255,255,255)
DULL_WHITE = Color(10,10,10)
DULL_BLUE = Color(0,0,10)
MAROON = Color(128,0,30)
PURPLE = Color(84,0,255) 
BLUE = Color(0,0,255)       # checkerboard
RED = Color(255,0,0)        # badddd
GREEN = Color(0,255,0)      # valid moves
YELLOW = Color(255,255,0)   # current space
OFF = Color(0,0,0)

LED_PIN        = 21       # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 70       # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0        # set to '1' for GPIOs 13, 19, 41, 45, or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

led_map = {}        # maps the individual LEDs with the location on the chess board
hall_map = {}       # when u want to get the location of a pin
board = chess.Board()


''' --- FUNCTIONS --- '''

def initialize_GPIO():
    GPIO.setmode(GPIO.BCM)
    for pin in input_pins:
        GPIO.setup(pin, GPIO.IN)
    for pin in select_pins:
        GPIO.setup(pin, GPIO.OUT)


''' --- LEDs --- '''
def turn_off_all_leds():
    """Turns off all LEDs on the strip."""
    for i in range(LED_COUNT):
        strip.setPixelColor(i, OFF)
    strip.show()

def turn_on_all_leds(color):
    """Turns on all of the LEDs on the strip using an algorithm that defines the LED pattern"""
    # the LEDs that are 'off' are found at indexes 5, 10, 11, 16, 21, 22, 27, etc...
    # this follows the pattern +5, +5, +1, +5, +5, +1, etc...
    
    loop_offset = 0   # counts the number of times +1 occurs and offsets the current pin accordingly
    led_pattern_index = 1

    for pin_number in range(LED_COUNT):
        current_pin = pin_number + 1    # just for debugging; starts the current pin at 1 instead of 0
        
        if (led_pattern_index % 3 == 0):
            led_pattern_index = 1
            loop_offset += 1
            #print(f"+1 -> ",current_pin)
        elif ((current_pin - loop_offset) % 5 == 0):
            led_pattern_index += 1
            #print(f"+5 -> ",current_pin)
        else:
            strip.setPixelColor(pin_number, color)
            strip.show()

def print_led_map():
    """Prints the led dict to the console in the format: <chess board coordinate> : <led pin number>"""
    for row in range(ROWS, 0, -1):
        for col in range(ord('a'), ord('h') + 1):
            # Get the chessboard coordinate for the current position
            chess_coord = chr(col) + str(row)
            print(chess_coord, ":", led_map[chess_coord], end='  ')
        print()
     
def populate_led_map():
    """Maps each chess board coordinate to a cooresponding LED"""
    loop_offset = 0   # counts the number of times +1 occurs and offsets the current pin accordingly
    total_offset = 0
    led_pattern_index = 1

    for pin_number in range(LED_COUNT):
        current_pin = pin_number + 1    # just for debugging; starts the current pin at 1 instead of 0
        
        if (led_pattern_index % 3 == 0):
            led_pattern_index = 1
            loop_offset += 1
            total_offset += 1
            #print(f"+1 -> ",current_pin)
        elif ((current_pin - loop_offset) % 5 == 0):
            led_pattern_index += 1
            total_offset += 1
            #print(f"+5 -> ",current_pin)
        else:
            #get the actual current pin
            #set the led map to be <chess space id, pin_number>
            curr_location = pin_number - total_offset
            row = curr_location // ROWS
            col = curr_location % ROWS
            if row % 2 == 0:  # Even column, top to bottom
                chess_coord = chr(ord('h') - col) + str(ROWS - row)
            else:  # Odd column, bottom to top
                chess_coord = chr(ord('a') + col) + str(ROWS - row)
            led_map[chess_coord] = pin_number

def turn_on_checkerboard():
    """Lights up the LEDs in a checkerboard pattern (useful for non-physical board view)"""
    for row in range(ROWS):
        for col in range(ROWS):
            chess_coord = chr(ord('a') + col) + str(ROWS - row)  # Chessboard coordinate
            # Alternate between dark and light colors based on even/odd positions
            if (row + col) % 2 == 0:
                strip.setPixelColor(led_map[chess_coord], DULL_BLUE)
            else:
                strip.setPixelColor(led_map[chess_coord], DULL_WHITE)
    strip.show()

def turn_on_square(chess_coord, color):
    strip.setPixelColor(led_map[chess_coord], color)
    strip.show()

def testAll():
    turn_on_checkerboard()
    time.sleep(.5)
    turn_on_all_leds(PURPLE)
    time.sleep(.5)
    turn_off_all_leds()
    turn_on_square('b4', BRIGHT_WHITE)
    time.sleep(1)
    turn_off_all_leds()


''' --- HALL EFFECT SENSORS --- '''
def read_sensor(input_channel):
    if GPIO.input(input_channel):
        return 0  # Assuming 0 means no magnet detected
    else:
        return 1  # Assuming 1 means magnet detected

def select_mux_channel(channel):
    """Select the given channel on the mux."""
    # Set select lines according to the channel number (0-7)
    for i, pin in enumerate(select_pins):
        GPIO.output(pin, channel & (1 << i))
        
def getCellIndexes(i):
    # adjusting for the way the hall effect sensors are stored thru the gpio
    index = i
    if (index >= ROWS // 2):
        index %= 4
    
    if (index % (ROWS // 2) == 1 or index % (ROWS // 2) == 2):
        left = index*2
        right = ROWS - (index*2 + 1)
    else:
        left = ROWS - (index+1)*2
        right = index*2 + 1
    return left, right

def getBreadboardPins(i):
    if (i < ROWS // 2):
        return [10, 9, 11, 0]
    else:
        return [14, 22, 27, 17]

def getBreadboards(chessboard, i):
    breadboards = []
    pins = getBreadboardPins(i)
    for pin in pins:
        breadboards.append(chessboard[pin])
    return breadboards

def print_sensors(sensors):
    # each input pin cooresponds with a breadboard, where each have a 4x2 matrix of hall sensors
    # each breadboard stores the hall sensors as a regular array but in weird order
    for i in range(ROWS):
        print(sensors[i])
    print()

def populate_sensor_array(chessboard):
    sensors = {}
    for i in range(ROWS):
        breadboards = getBreadboards(chessboard, i)
        left, right = getCellIndexes(i)
        
        first_pair = [breadboards[0][left], breadboards[0][right]]
        second_pair = [breadboards[1][left], breadboards[1][right]]
        third_pair = [breadboards[2][left], breadboards[2][right]]
        last_pair = [breadboards[3][left], breadboards[3][right]]
        
        sensors[i] = first_pair + second_pair + third_pair + last_pair
        # row i ==== breadboards, left, right
        
        chess_coord = chr(ord('a')) + str(ROWS - i)
        hall_map[chess_coord] = [0, breadboards, left]
        chess_coord = chr(ord('b')) + str(ROWS - i)
        hall_map[chess_coord] = [0, breadboards, right]
        chess_coord = chr(ord('c')) + str(ROWS - i)
        hall_map[chess_coord] = [1, breadboards, left]
        chess_coord = chr(ord('d')) + str(ROWS - i)
        hall_map[chess_coord] = [1, breadboards, right]
        chess_coord = chr(ord('e')) + str(ROWS - i)
        hall_map[chess_coord] = [2, breadboards, left]
        chess_coord = chr(ord('f')) + str(ROWS - i)
        hall_map[chess_coord] = [2, breadboards, right]
        chess_coord = chr(ord('g')) + str(ROWS - i)
        hall_map[chess_coord] = [3, breadboards, left]
        chess_coord = chr(ord('h')) + str(ROWS - i)
        hall_map[chess_coord] = [3, breadboards, right]
        print(chess_coord, sensors[i])
    print()
            
    return sensors

def getChangedPin(curr_sensors, prev_sensors):
    if (not prev_sensors):
        return None
    for key in hall_map:
        row = ROWS - int(key[1])
        col = ord(key[0]) - ord('a')
        if (curr_sensors[row][col] != prev_sensors[row][col]):
            return key
    

def hall():
    prev_board = {pin: [None] * 8 for pin in input_pins}
    prev_sensors = None
    lifted_piece_coord = None
    
    try:
        while True:
            curr_board = {pin: [] for pin in input_pins}
            for channel in range(8):
                select_mux_channel(channel)
                # Small delay to ensure the select lines have settled
                time.sleep(0.01)
                for pin in input_pins:
                    curr_board[pin].append(read_sensor(pin))

            # Check if there's any change in sensor values
            if any(curr_board[pin] != prev_board[pin] for pin in input_pins):
                sensors = populate_sensor_array(curr_board)
                
                chess_coord = getChangedPin(sensors, prev_sensors)
                print(chess_coord)
                if (chess_coord):
                    light_up_square(chess_coord)
                    square = chess.parse_square(chess_coord)
                    piece = board.piece_at(square)
                    
                    if lifted_piece_coord is not None:
                        possible_moves = get_possible_moves_from(lifted_piece_coord)
                        moved_spaces = False
                        for move in possible_moves:
                            if move == chess_coord:
                                print("placed to new spot", move)
                                turn_on_checkerboard()
                                
                                from_square = chess.parse_square(lifted_piece_coord)
                                print(lifted_piece_coord, ";", from_square)
                                movedTo = chess.Move(from_square, square)
                                board.push(movedTo)
                                lifted_piece_coord = None
                                moved_spaces = True
                        
                        if moved_spaces == False:
                            if chess_coord != lifted_piece_coord:
                                turn_on_all_leds(RED)
                                light_up_square(lifted_piece_coord)
                                print(lifted_piece_coord,"not in the right space,,", chess_coord)
                            else:
                                print("placed to same spot")
                                turn_on_checkerboard()
                                lifted_piece_coord = None
                    else:
                        lifted_piece_coord = chess_coord
            
                        if piece is not None:
                            light_up_square(chess_coord)
                            possible_moves = get_possible_moves_from(chess_coord)
                            light_up_possible_moves(possible_moves)
                        else:
                            # later, check if this was a valid move
                            turn_off_all_leds()
                            
                prev_board = curr_board.copy()
                prev_sensors = sensors.copy()
                
                print(board)
                
            # Delay between readings
            time.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()


''' --- BOARD --- '''
def get_possible_moves_from(chess_coord):
    possible_moves = []
    
    square = chess.parse_square(chess_coord)
    piece = board.piece_at(square)
    
    if piece is not None:
        # Generate all legal moves for the piece
        legal_moves = board.legal_moves
        print(list(legal_moves))
        # Filter out moves that are not valid according to the current board position
        for move in legal_moves:
            if move.from_square == square:
                possible_moves.append(chess.square_name(move.to_square))
    print(possible_moves)
    return possible_moves

def light_up_possible_moves(possible_moves):
    for move in possible_moves:
        pin = led_map[move]
        strip.setPixelColor(pin, GREEN)
        strip.show()

def light_up_square(chess_coord):
    pin = led_map[chess_coord]
    strip.setPixelColor(pin, YELLOW)
    strip.show()


''' --- PROGRAM START --- '''

# setup
initialize_GPIO()
populate_led_map()

print(board)
print()

# usage
#turn_off_all_leds()
hall()
turn_on_checkerboard()


# shutdown
GPIO.cleanup()




