import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)  # Uses Broadcom pin-numbering scheme

# select lines for muxes
select_pins = [17, 27, 22]  # GPIO pins for select lines
sensor_pin = 23  # sensor matrix input

# Set up the select pins as outputs and sensor pin as input
GPIO.setup(select_pins, GPIO.OUT)
GPIO.setup(sensor_pin, GPIO.IN)

def select_sensor(sensor_number):
    # Selects the sensor based on the sensor number (0-63)
    # Determine the binary representation of the sensor number
    # and set the select pins accordingly
    for i in range(3):
        GPIO.output(select_pins[i], (sensor_number >> i) & 1)

def read_sensor():
    ## Reads the current sensor value
    return GPIO.input(sensor_pin)

def main():
    try:
        while True:
            for sensor_number in range(64):  # 64 sensors in the 8x8 matrix
                select_sensor(sensor_number)
                # Small delay to ensure the MUX switches before reading
                time.sleep(0.01)  
                sensor_state = read_sensor()
                print(f"Sensor {sensor_number}: {'ON' if sensor_state else 'OFF'}")
                
                # CALL CHESS API HERE, USE THIS CODE TO INPUT INTO CHESS ENGINE
                
            # Delay before the next cycle through all sensors
            time.sleep(0.5)  # Adjust this delay as necessary
            
    except KeyboardInterrupt:
        # Clean up GPIO state before exiting
        GPIO.cleanup()

if __name__ == "__main__":
    main()
