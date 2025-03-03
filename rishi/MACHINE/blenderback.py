import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Define motor control pins using Raspberry Pi GPIO
MOTOR_PINS = {
    "horizontal_1": {"pulse": 18, "direction": 23},  # Replace with actual GPIO pins
    "horizontal_2": {"pulse": 24, "direction": 25},  # Replace with actual GPIO pins
    "gantry": {"pulse": 26, "direction": 21},        # Replace with actual GPIO pins
}

# Define shared enable pin
ENABLE_PIN = 14  # Replace with actual GPIO pin

# Set up GPIO pin modes
GPIO.setup(ENABLE_PIN, GPIO.OUT)
for motor in MOTOR_PINS.values():
    GPIO.setup(motor["pulse"], GPIO.OUT)
    GPIO.setup(motor["direction"], GPIO.OUT)

# Set enable pin to LOW (active state)
GPIO.output(ENABLE_PIN, False)

# Function to enable/disable motors
def enable_motors(enable=True):
    GPIO.output(ENABLE_PIN, not enable)  # LOW = enabled, HIGH = disabled

# Function to move the motors
def move_stepper(motor_pins, steps, direction):
    enable_motors(True)  # Enable motors
    GPIO.output(motor_pins["direction"], direction)  # Set direction

    for _ in range(steps):
        GPIO.output(motor_pins["pulse"], True)
        time.sleep(0.00025)  # Pulse ON time
        GPIO.output(motor_pins["pulse"], False)
        time.sleep(0.00025)  # Pulse OFF time

    enable_motors(False)  # Disable motors

# Function to move the gantry to a specific position
def move_gantry_to_position_blender(flavor_position):
    gantry_steps = {
        1: (36950, 36950, 9500),
        2: (33000, 33000, 9500),
        3: (29200, 29200, 9500),
        4: (25450, 25450, 9500),
        5: (21500, 21500, 9500),
        6: (17650, 17650, 9500),
        7: (13400, 13400, 9500),
        8: (9200, 9200, 9500),
        9: (5600, 5600, 9500),
    }

    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(flavor_position, (0, 0, 0))

    enable_motors(True)

    # Set directions
    GPIO.output(MOTOR_PINS['horizontal_1']['direction'], steps_motor_1 > 0)
    GPIO.output(MOTOR_PINS['horizontal_2']['direction'], steps_motor_2 > 0)
    GPIO.output(MOTOR_PINS['gantry']['direction'], steps_motor_3 > 0)

    # Move gantry motor first if flavor = 8 or 9
    if flavor_position in [8, 9]:
        for _ in range(abs(steps_motor_3)):
            GPIO.output(MOTOR_PINS['gantry']['pulse'], True)
            time.sleep(0.00025)
            GPIO.output(MOTOR_PINS['gantry']['pulse'], False)
            time.sleep(0.00025)

        for step in range(max(abs(steps_motor_1), abs(steps_motor_2))):
            if step < abs(steps_motor_1):
                GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], True)
            if step < abs(steps_motor_2):
                GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], True)
            time.sleep(0.00025)
            GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], False)
            GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], False)
            time.sleep(0.00025)

    else:
        for step in range(max(abs(steps_motor_1), abs(steps_motor_2), abs(steps_motor_3))):
            if step < abs(steps_motor_1):
                GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], True)
            if step < abs(steps_motor_2):
                GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], True)
            if step < abs(steps_motor_3):
                GPIO.output(MOTOR_PINS['gantry']['pulse'], True)
            time.sleep(0.00025)
            GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], False)
            GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], False)
            GPIO.output(MOTOR_PINS['gantry']['pulse'], False)
            time.sleep(0.00025)

    enable_motors(False)

# Main execution
if __name__ == "__main__":
    try:
        flavor = int(input("Enter the flavor number (1-9): "))
        qty = int(input("Enter the quantity (200 or 400 ml): "))

        move_gantry_to_position_blender(flavor)

    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Program exited.")
