import time
import RPi.GPIO as GPIO

# Set up Raspberry Pi GPIO pins
GPIO.setmode(GPIO.BCM)

# Define motor pins using Raspberry Pi GPIO pins
MOTOR_PINS = {
    "horizontal_1": {"pulse": 18, "direction": 23},  
    "horizontal_2": {"pulse": 24, "direction": 25},  
    "gantry": {"pulse": 26, "direction": 21}        
}

ENABLE_PIN = 14  
GPIO.setup(ENABLE_PIN, GPIO.OUT)
for motor in MOTOR_PINS.values():
    GPIO.setup(motor["pulse"], GPIO.OUT)
    GPIO.setup(motor["direction"], GPIO.OUT)

GPIO.output(ENABLE_PIN, False)

def enable_motors(enable=True):
    GPIO.output(ENABLE_PIN, not enable)  

def move_stepper(motor_pins, steps, direction):
    enable_motors(True)  
    GPIO.output(motor_pins["direction"], direction)  

    for _ in range(steps):
        GPIO.output(motor_pins["pulse"], True)
        time.sleep(0.00025)  
        GPIO.output(motor_pins["pulse"], False)
        time.sleep(0.00025)  

    enable_motors(False)  

def move_powder_stepper(motor_pins, steps):
    enable_motors(True)  
    for step in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)
    enable_motors(False)  

def move_gantry_to_position(powder_variety):
    gantry_steps = {
        1: (0, 0, 9000),
        2: (4000, 4000, 9000),
        3: (7800, 7800, 9000),
        4: (11500, 11500, 9000),
        5: (15500, 15500, 9000),
        6: (19500, 19500, 9000),
        7: (23600, 23600, 9000),
        8: (27900, 27900, 9000),
        9: (31400, 31400, 9000),
    }
    
    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(powder_variety, (0, 0, 0))

    enable_motors(True)

    GPIO.output(MOTOR_PINS['horizontal_1']['direction'], True)  
    GPIO.output(MOTOR_PINS['horizontal_2']['direction'], True)  
    GPIO.output(MOTOR_PINS['gantry']['direction'], False)  

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

def dispense_powder(variety, qty, servings=None):
    try:
        powder_motor_pins = {
            1: {'pulse': 4},  
            2: {'pulse': 17},  
            3: {'pulse': 27},  
            4: {'pulse': 22},  
            5: {'pulse': 10},  
            6: {'pulse': 9},   
            7: {'pulse': 11},  
            8: {'pulse': 0},   
            9: {'pulse': 5},   
        }

        if variety not in powder_motor_pins:
            raise ValueError("Invalid powder variety selected, choose between 1 and 9.")

        motor_pins = powder_motor_pins[variety]

        GPIO.setup(motor_pins['pulse'], GPIO.OUT)

        if variety in [1, 4, 7]:  
            if qty != 400:
                raise ValueError("This variety is only available in 400ml.")
            steps_per_revolution = 200
            stepper_rotations = 90  
            powder_weight = 100    
        else:  
            if qty != 200:
                raise ValueError("This variety is only available in 200ml.")
            if servings == 1:
                powder_weight = 33
                stepper_rotations = 31  
            elif servings == 2:
                powder_weight = 64
                stepper_rotations = 60  
            else:
                raise ValueError("Invalid serving size. Choose 1 or 2.")

            steps_per_revolution = 200

        print(f"Dispensing {powder_weight} g of selected powder...")

        steps_to_dispense = steps_per_revolution * stepper_rotations

        move_powder_stepper(motor_pins, steps_to_dispense)

        print(f"{powder_weight}g of powder dispensed.")
    
    except Exception as e:
        print(f"Error dispensing powder: {e}")

def main():
    try:
        print("Select a variety of powders:")
        print("1, 4, 7 → Mass Gainer (Only available in 400ml)")
        print("2, 3, 5, 6, 8, 9 → Whey Protein (Only available in 200ml)")

        variety = int(input("Enter the powder variety number (1-9): "))

        if variety in [1, 4, 7]:  
            qty = 400
        elif variety in [2, 3, 5, 6, 8, 9]:  
            qty = 200
            servings = int(input("How many servings? (1 or 2): "))
            if servings not in [1, 2]:
                raise ValueError("Invalid selection. Please enter 1 or 2.")
        else:
            raise ValueError("Invalid variety selected.")

        move_gantry_to_position(variety)
        
        if variety in [1, 4, 7]:  
            dispense_powder(variety, qty)
        else:  
            dispense_powder(variety, qty, servings)

    except Exception as e:
        print(f"Error in main program: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
