import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(20, GPIO.OUT)  # Set GPIO 20 as an output

GPIO.output(20, GPIO.HIGH)  # Set GPIO 20 to HIGH
print("GPIO 20 is now HIGH")

# Keep GPIO 20 HIGH (do not clean up)
# GPIO.cleanup()  # Uncomment this if you want the pin to reset after the script ends
