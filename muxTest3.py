#!/usr/bin/python

import RPi.GPIO as GPIO
import time

# Pin Definitions
input_pins = [14, 22, 27, 17, 10, 9, 11, 0]  # Mux outputs connected here, including the new GPIO pin 22
select_pins = [2, 3, 4]  # Mux select lines (S2, S1, S0)

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

def swap_values(chunk):
    # Swapping positions within each 4x2 chunk
    # Swap top left with bottom left
    chunk[0], chunk[6] = chunk[6], chunk[0]
    # Swap right upper middle with right lower middle
    chunk[3], chunk[5] = chunk[5], chunk[3]
    return chunk

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
                print_4x8_matrix(current_sensor_values[10], current_sensor_values[11], current_sensor_values[9],current_sensor_values[0], current_sensor_values[14], current_sensor_values[22], current_sensor_values[27], current_sensor_values[17])
                last_sensor_values = current_sensor_values.copy()
                
            # Delay between readings
            time.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
