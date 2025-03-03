import time
import RPi.GPIO as GPIO
import threading  # Only for the washing operation; no full threading for everything else
import os
# Import motor control functions
from cupback import dispense_cup
from waterback import dispense_water
from powderback import dispense_powder, move_gantry_to_position
from blenderback import move_gantry_to_position_blender
from blendermechanism import run_blender_process, washing_operation
from washingcontainer import change_washing_water

# Ensure GPIO mode is set only once
if not GPIO.getmode():
    GPIO.setmode(GPIO.BCM)  # Using Broadcom pin numbering

GPIO.setwarnings(False)

# Define GPIO Pins for Stepper Motors
MOTOR_PINS = {
    "horizontal_1": {"pulse": 18, "direction": 23},  # Define actual GPIO pins
    "horizontal_2": {"pulse": 24, "direction": 25},
    "gantry": {"pulse": 26, "direction": 21}
}

# Shared Enable Pin for all motors
ENABLE_PIN = 14

# File to store order count
ORDER_COUNT_FILE = "order_count.txt"
MAX_ORDERS_BEFORE_WATER_CHANGE = 20  # Change water after 20 orders

# Set up GPIO pins
GPIO.setup(ENABLE_PIN, GPIO.OUT)
for motor in MOTOR_PINS.values():
    GPIO.setup(motor["pulse"], GPIO.OUT)
    GPIO.setup(motor["direction"], GPIO.OUT)

# Function to enable or disable motors
def enable_motors(enable=True):
    GPIO.output(ENABLE_PIN, GPIO.LOW if enable else GPIO.HIGH)

# Function to pulse the motor
def pulse_motor(motor_pins, steps, direction):
    enable_motors(True)
    GPIO.output(motor_pins["direction"],
                GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.000025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)

    enable_motors(False)

# Move horizontal motors synchronously
def move_horizontal_synchronously(motor_pins_1, motor_pins_2, steps, direction):
    enable_motors(True)
    GPIO.output(motor_pins_1["direction"],
                GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_pins_2["direction"],
                GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(steps):
        GPIO.output(motor_pins_1["pulse"], GPIO.HIGH)
        GPIO.output(motor_pins_2["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins_1["pulse"], GPIO.LOW)
        GPIO.output(motor_pins_2["pulse"], GPIO.LOW)
        time.sleep(0.00025)

    enable_motors(False)




# Move three motors synchronously
def move_three_motors_synchronously(motor_pins_1, motor_pins_2, motor_pins_3, steps_1, steps_2, steps_3, direction):
    enable_motors(True)
    GPIO.output(motor_pins_1["direction"],
                GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_pins_2["direction"],
                GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_pins_3["direction"],
                GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(max(steps_1, steps_2, steps_3)):
        if step < steps_1:
            GPIO.output(motor_pins_1["pulse"], GPIO.HIGH)
        if step < steps_2:
            GPIO.output(motor_pins_2["pulse"], GPIO.HIGH)
        if step < steps_3:
            GPIO.output(motor_pins_3["pulse"], GPIO.HIGH)

        time.sleep(0.00025)

        if step < steps_1:
            GPIO.output(motor_pins_1["pulse"], GPIO.LOW)
        if step < steps_2:
            GPIO.output(motor_pins_2["pulse"], GPIO.LOW)
        if step < steps_3:
            GPIO.output(motor_pins_3["pulse"], GPIO.LOW)

        time.sleep(0.00025)

    enable_motors(False)

# Move single stepper motor
def move_stepper(motor_pins, steps, direction):
    enable_motors(True)
    GPIO.output(motor_pins["direction"],
                GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)

    enable_motors(False)



# Function to load order count from file
def load_order_count():
    if os.path.exists(ORDER_COUNT_FILE):
        with open(ORDER_COUNT_FILE, "r") as file:
            try:
                return int(file.read().strip())  # Read and convert to int
            except ValueError:
                return 0  # Reset if file is corrupted
    return 0  # Default if file does not exist

# Function to save order count to file
def save_order_count(order_count):
    with open(ORDER_COUNT_FILE, "w") as file:
        file.write(str(order_count))

# Function to simulate the washing water change
def change_washing_water():
    print("Washing water changed.")

# Load the order count when script starts
order_count = load_order_count()


# Function to process an order
def process_order():
    global order_count

    while True:  # Keeps the program running until the user chooses to exit
        cup_type = input("Enter cup type (machine/user): ").strip().lower()
        while cup_type not in ['machine', 'user']:
            print("Invalid input. Please enter 'machine' or 'user'.")
            cup_type = input("Enter cup type (machine/user): ").strip().lower()

        print("Select a variety of powders:")
        print("1, 4, 7 → Mass Gainer (Only available in 400ml)")
        print("2, 3, 5, 6, 8, 9 → Whey Protein (Only available in 200ml)")

        try:
            variety = int(input("Enter the powder variety number (1-9): "))
            if variety in [1, 4, 7]:  
                qty = 400
                water_quantity = 400
                servings = None
            elif variety in [2, 3, 5, 6, 8, 9]:  
                qty = 200
                servings = int(input("How many servings? (1 or 2): "))
                if servings not in [1, 2]:
                    raise ValueError("Invalid selection. Please enter 1 or 2.")
                water_quantity = int(input("Enter water quantity (200 or 400): "))
                while water_quantity not in [200, 400]:
                    print("Invalid water quantity. Please enter 200 or 400.")
                    water_quantity = int(input("Enter water quantity (200 or 400): "))
            else:
                raise ValueError("Invalid variety selected.")
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue

        print(f"\nProcessing order: Cup Type: {cup_type}, Powder Variety: {variety}, Water Quantity: {water_quantity} ml, Servings: {servings if servings else 'None'}\n")

        try:
            # Step 1: Move to home position
            print("Step 1: At home position (Cup Dispensing Station)...")
            move_horizontal_synchronously(
                MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 0, "reverse")
            move_stepper(MOTOR_PINS["gantry"], 0, "reverse")
            time.sleep(0.5)

            if cup_type == "machine":
                print("Step 2: Dispensing cup...")
                dispense_cup()
            else:
                print("Step 2: Moving to delivery point for user cup...")
                move_horizontal_synchronously(
                    MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 35000, "forward")
                move_stepper(MOTOR_PINS["gantry"], 1500, "forward")
                print("Please place your cup in the designated area.")
                time.sleep(5)
                print("User cup detected.")

            if cup_type == "machine":
                # For machine cup: move to water dispensing station with specific steps
                print("Step 3: Moving to water dispensing station for machine cup...")
                move_stepper(MOTOR_PINS["gantry"], 10000, "reverse")
                move_horizontal_synchronously(
                    MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 7000, "reverse")
            else:
                # For user cup: move to water dispensing station with different steps and direction
                print("Step 3: Moving to water dispensing station for user cup...")
                move_three_motors_synchronously(
                    MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"], 41850, 41850, 10000, "reverse")

            # Call the function to dispense the water after moving to the dispensing station
            dispense_water(water_quantity)
            time.sleep(1)

            # Step 4: Move to powder dispensing station
            print("Step 4: Moving to powder dispensing station...")
            move_gantry_to_position(variety)
            time.sleep(0.5)
            if variety in [1, 4, 7]:  
                dispense_powder(variety, qty)
            else:  
                dispense_powder(variety, qty, servings)
            time.sleep(1)

            # Step 5: Move to blender station
            print("Step 5: Moving to blender station...")
            move_gantry_to_position_blender(variety)
            run_blender_process(water_quantity)
            time.sleep(0.5)
            washing_operation()
            print("Step 6: Moving to delivery point...")
            #washing_thread = threading.Thread(target=washing_operation)
            #washing_thread.start()  # Start washing operation in the background

            move_three_motors_synchronously(
                MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"], 4750, 4750, 11750, "forward")
            print("Please Take Your Drink.")
            time.sleep(3)

            # Step 7: Returning to home position (Three motors synchronously)
            print("Step 7: Returning to home position (Cup Dispensing Station)...")
            move_three_motors_synchronously(
                MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"], 34750, 34750, 6000, "reverse")
            move_stepper(MOTOR_PINS["gantry"], 3750, "forward")

            print("Process complete")
            


            order_count += 1  # Increment order count
            save_order_count(order_count)  # Save updated order count
            print(f"Order {order_count} completed.")

            # Trigger water change after every MAX_ORDERS_BEFORE_WATER_CHANGE orders
            if order_count % MAX_ORDERS_BEFORE_WATER_CHANGE == 0:
                print(f"{MAX_ORDERS_BEFORE_WATER_CHANGE} orders completed. Changing washing water...")
                change_washing_water()
                order_count = 0  # Reset order count
                save_order_count(order_count)  # Save reset order count

        except Exception as e:
            print(f"Error occurred: {str(e)}")

        # Ask if the user wants to place another order
        another_order = input(
            "Would you like to place another order? (yes/no): ").strip().lower()
        while another_order not in ["yes", "no"]:
            another_order = input(
                "Invalid input. Please enter 'yes' or 'no': ").strip().lower()

        if another_order == 'no':
            print("Thank you for using the vending machine!")
            break  # Exit the loop, ending the program


# Main execution block
if __name__ == "__main__":
    process_order()
