import serial
import time
import RPi.GPIO as GPIO
import os

# Constants for servo positions
SERVO_ID = 1  # Default Servo ID

RIGHT_90_POSITION = 0
LEFT_90_POSITION = 650

# Stepper motor control pins (example)
STEP_PIN = 16  # Stepper motor step pin
DIR_PIN = 20   # Stepper motor direction pin

# MCP23017 address and gear motor pins
MCP23017_ADDRESS = 0x26 # I2C address of MCP23017
MCP_IN1_PIN = 8        # MCP23017 pin for gear motor IN1
MCP_IN2_PIN = 11       # MCP23017 pin for gear motor IN2

# File to store order count
ORDER_COUNT_FILE = "order_count.txt"

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

# Initialize MCP23017
# Function to calculate checksum
def calculate_checksum(data):
    checksum = 0
    for byte in data[2:]:  # Skip header bytes
        checksum += byte
    checksum = ~checksum & 0xFF
    return checksum

# Function to send a position command to the servo
def move_servo(ser, position, move_time):
    position_l = position & 0xFF
    position_h = (position >> 8) & 0xFF
    time_l = move_time & 0xFF
    time_h = (move_time >> 8) & 0xFF

    # LX-224HV move command
    command = [
        0x55, 0x55,          # Header
        SERVO_ID,            # Servo ID
        7,                   # Data length (7 bytes)
        1,                   # Move command
        position_l, position_h, time_l, time_h,
        0                    # Checksum (to be calculated)
    ]
    command[-1] = calculate_checksum(command)  # Calculate checksum

    ser.write(bytearray(command))  # Send command to servo
    time.sleep(0.1)  # Small delay for processing

# Function to test the servo motor
def test_servo():
    # Open serial connection for servo control
    ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)

    try:
        print("Testing servo motor...")
        move_servo(ser, LEFT_90_POSITION, 1000)  # Move to left position (650)
        time.sleep(2)
        move_servo(ser, RIGHT_90_POSITION, 1000)  # Move to right position (0)
        time.sleep(2)
        print("Servo test complete.")

    except Exception as e:
        print(f"Error during servo test: {e}")
    finally:
        ser.close()  # Close the serial connection

# Main function for testing the servo
if __name__ == "__main__":
    test_servo()
