#!/usr/bin/python

import RPi.GPIO as GPIO
import time
from rpi_ws281x import *

# Pin Definitions
input_pins = [14, 22, 27, 17, 10, 9, 11, 0]  # Mux outputs connected here, including the new GPIO pin 22
select_pins = [2, 3, 4]  # Mux select lines (S2, S1, S0)

# Additional LED strip configuration

# Assuming an 8x8 chessboard with a snake pattern LED strip
ROWS = 8  # Chessboard rows
COLS = 8  # Chessboard columns
LEDs_PER_ROW = 9
SKIPPED_LEDs_BETWEEN_ROWS = 2
# Adjust the total LED count to match your setup
LED_COUNT = 150


LED_PIN        = 21       # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0        # set to '1' for GPIOs 13, 19, 41, 45, or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()



# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN)
for pin in select_pins:
    GPIO.setup(pin, GPIO.OUT)

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

def print_4x8_matrix(sensor_values_10, sensor_values_11, sensor_values_9, sensor_values_0, sensor_values_14, sensor_values_22, sensor_values_27, sensor_values_17):
    # Print the sensor values as a 4x6 matrix
    for i in range(4):
        row_10 = sensor_values_10[i*2:(i+1)*2]
        row_11 = sensor_values_11[i*2:(i+1)*2]
        row_9 = sensor_values_9[i*2:(i+1)*2]
        row_0 = sensor_values_0[i*2:(i+1)*2]
        combined_row = row_10 + row_9 + row_11 + row_0  # Combine rows for a 4x8 matrix
        print(combined_row)
    for i in range(4):
		
        row_14 = sensor_values_14[i*2:(i+1)*2]
        row_22 = sensor_values_22[i*2:(i+1)*2]
        row_27 = sensor_values_27[i*2:(i+1)*2]
        row_17 = sensor_values_17[i*2:(i+1)*2]
        
        combined_row = row_14 + row_22 + row_27 + row_17  # Combine rows for a 4x8 matrix
        print(combined_row)
    print()
def generate_8x8_matrix(sensor_values_10, sensor_values_11, sensor_values_9, sensor_values_0, sensor_values_14, sensor_values_22, sensor_values_27, sensor_values_17):
    matrix = []  # Initialize the matrix that will hold the 8x8 grid
    # First 4 rows
    for i in range(4):
        row_10 = sensor_values_10[i*2:(i+1)*2]
        row_11 = sensor_values_11[i*2:(i+1)*2]
        row_9 = sensor_values_9[i*2:(i+1)*2]
        row_0 = sensor_values_0[i*2:(i+1)*2]
        combined_row = row_10 + row_9 + row_11 + row_0  # Combine rows for a 4x8 matrix
        matrix.append(combined_row)  # Add the combined row to the matrix
    # Second 4 rows
    for i in range(4):
        row_14 = sensor_values_14[i*2:(i+1)*2]
        row_22 = sensor_values_22[i*2:(i+1)*2]
        row_27 = sensor_values_27[i*2:(i+1)*2]
        row_17 = sensor_values_17[i*2:(i+1)*2]
        combined_row = row_14 + row_22 + row_27 + row_17  # Combine rows for a 4x8 matrix
        matrix.append(combined_row)  # Add the combined row to the matrix
    
    return matrix  # Return the complete 8x8 matrix

def swap_values(chunk):
    # Swapping positions within each 4x2 chunk
    # Swap top left with bottom left
    chunk[0], chunk[6] = chunk[6], chunk[0]
    # Swap right upper middle with right lower middle
    chunk[3], chunk[5] = chunk[5], chunk[3]
    return chunk
def calculate_led_index(chess_row, chess_col):
    """
    Calculate the LED index in the strip based on the chess piece's row and column,
    accounting for the "snake pattern" and skipped LEDs between rows.
    """
    # Adjust this logic based on your specific LED layout
    row_start_index = chess_row * (LEDs_PER_ROW + SKIPPED_LEDs_BETWEEN_ROWS)
    if chess_row % 2 == 0:  # Even rows go right to left
        index = row_start_index + chess_col
    else:  # Odd rows go left to right
        index = row_start_index + (COLS - 1 - chess_col)
    return index

def update_led_for_piece(strip, chess_row, chess_col, color):
    """
    Update a single LED based on the chess piece's position.
    """
    led_index = calculate_led_index(chess_row, chess_col)
    strip.setPixelColor(led_index, color)


def calculate_led_index_from_sensor_position(sensor_position):
    # Assuming sensors are displayed and thus mapped in a specific custom order
    # For simplicity, let's assume an 8x8 grid, with sensors mapped row by row in the order they're displayed
    row = (sensor_position - 1) // 8
    col = (sensor_position - 1) % 8

    # If we're in the second half of the chessboard, adjust the row index
    if sensor_position > 32:
        row = (sensor_position - 33) // 8 + 4  # Adjust for the second half starting at sensor 33
        col = (sensor_position - 33) % 8

    # Calculate the LED index based on the "snake pattern"
    if row % 2 == 0:
        # Even row: left to right in LED strip terms
        led_index = row * LEDs_PER_ROW + col
    else:
        # Odd row: right to left in LED strip terms
        led_index = row * LEDs_PER_ROW + (7 - col)

    return led_index
    
def turn_off_all_leds(strip):
    """Turns off all LEDs on the strip."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()


def calculate_led_index_based_on_s_pattern(row, col):
    # Calculate the LED index based on the S-shaped configuration
    # Flip every other row's direction to follow the S-shape
    if row % 2 == 0:
        # For even rows, go left to right
        index = row * COLS + col
    else:
        # For odd rows, go right to left
        index = row * COLS + (COLS - 1 - col)
    return index
def get_led_index(sensor_index):
    # Custom mapping logic since sensor order in array is practically random
    mapping = {
        16: 0,  # Sensor 1 activates LED 30 (index 29)
        56: 1,  # Sensor 2 activates LED 56 (index 55)
        15: 2,  # Sensor 3 activates LED 29 (index 28)
        55: 3,  # Sensor 4 activates LED 57 (index 56)
        54: 5,
        13: 7,
        53: 8,
        21: 11,
		45: 12,
        46: 14,
        23: 15,
        47: 16,
        24: 18,
        48: 19,

		32: 22,
		40: 23,
        31: 24,
		39: 25,
		30: 26,
		38: 28,
		29: 29,
		37: 30,
		5: 33,
		61: 34,

		6: 35,

		62: 36,
		7: 38,
		63: 39,
		8: 40,
		64: 41,
		12: 44,
		52: 45,
		11: 46,
		51: 47,
		10: 48,
		50: 50,
		9: 51,
		49: 52,
		18: 57,
		42: 58,
		19: 60,
		43: 61,
		20: 62,
		44: 63,
		28: 66,
		36: 67,
		27: 68,
		35: 69,
		26: 71,
		34: 72,
		2: 79,
		58: 80,
		3: 81,
		59: 83,
		4: 84,
		60: 85
        # Add further mappings here based on the pattern you've observed
    }
    # Return the LED index for the sensor, default to the sensor index if not specified (minus 1 to align with 0-based indexing)
    return mapping.get(sensor_index, sensor_index - 1)

def update_leds_based_on_sensor_values(strip, sensor_values):
    """
    Update the LED strip based on the sensor values.
    """
    for sensor_position, sensor_state in enumerate(sensor_values, start=1):
        # Calculate the LED index based on the sensor position
        led_index = calculate_led_index_from_sensor_position(sensor_position)
        if sensor_state == 1:
            # If the sensor is active (magnet detected), set the LED to green
            strip.setPixelColor(led_index, Color(0, 255, 0))  # Green color
        else:
            # If the sensor is not active, turn off the LED
            strip.setPixelColor(led_index, Color(0, 0, 0))  # Turn off LED
    strip.show()  # Update the LED strip
    
def main():
    time.sleep(1)  # Initial delay for setup stabilization

    try:
        while True:
            current_sensor_values = []  # Store current sensor values

            # Read sensor states
            for channel in range(8):  # Assuming 8 channels for the multiplexer
                select_mux_channel(channel)
                time.sleep(0.01)  # Allow time for the channel selection to settle
                for pin in input_pins:
                    sensor_state = read_sensor(pin)
                    current_sensor_values.append(sensor_state)

            print("Activated Sensors:", [i + 1 for i, state in enumerate(current_sensor_values) if state == 1])

            # First, reset all LEDs to ensure a clean state
            for i in range(LED_COUNT):
                strip.setPixelColor(i, Color(0, 0, 0))

            # Update LEDs based on sensor values
            update_leds_based_on_sensor_values(strip, current_sensor_values)

            # Finally, apply all changes at once
            # strip.show()
            time.sleep(0.1)  # Small delay to limit update speed

    except KeyboardInterrupt:
        # Turn off all LEDs on exit
        turn_off_all_leds(strip)
        GPIO.cleanup()




if __name__ == "__main__":
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    main()
