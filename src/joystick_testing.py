# DC motor
import RPi.GPIO as GPIO
import time
# Controller
import evdev
import numpy as np
from evdev import InputDevice, categorize, ecodes, KeyEvent

gamepad = InputDevice('/dev/input/event9')
last = {
    "ABS_RZ": 33953
}

# Varuiable
Fuzz = 255

# Motor
GPIO.setmode(GPIO.BOARD)
# Rear Left Motor
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
left1_pwm = GPIO.PWM(11, 10000)
left2_pwm = GPIO.PWM(13, 10000)  # 10000 is PWM
left1_pwm.start(0)
left2_pwm.start(0)

#Rear Right Motor
GPIO.setup(19, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
right3_pwm = GPIO.PWM(19, 10000)
right4_pwm = GPIO.PWM(21, 10000)  # 10000 is PWM
right3_pwm.start(0)
right4_pwm.start(0)

# Controller
def map_value_backward(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_min, out_max])

def map_value_forward(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_max, out_min])
# The above function swaps out_max and out_min to correctly modify speed
# When the joystick is pushed forward its value decreases to 0 and the output speed should be 100

device = evdev.InputDevice('/dev/input/event9')
print(device)

# Motor control methods
# Left Motor
def left_forward(speed):
    print(f"Going Forward at {speed}%")
    GPIO.output(11, True)
    GPIO.output(13, False)
    left1_pwm.ChangeDutyCycle(speed)

def left_backward(speed):
    print(f"Going Backward at {speed}%")
    GPIO.output(13, True)
    GPIO.output(11, False)
    #left1_pwm.ChangeDutyCycle(0)
    left2_pwm.ChangeDutyCycle(speed)

# Right Motor
def right_forward(speed):
    print(f"Going Forward at {speed}%")
    GPIO.output(19, True)
    GPIO.output(21, False)
    right3_pwm.ChangeDutyCycle(speed)

def right_backward(speed):
    print(f"Going Backward at {speed}%")
    GPIO.output(21, True)
    GPIO.output(19, False)
    right4_pwm.ChangeDutyCycle(speed)


try:
    # Event loop
    for event in device.read_loop():
        #absevent = categorize(event)
        if event.type == evdev.ecodes.EV_ABS:
            # Left Motor
            # Forward
            if event.code == evdev.ecodes.ABS_Y and event.value <= 32000:
                speed = round(map_value_forward(event.value, 0, 31100, 0, 100))
                print(f"left event value: {event.value}")
            if event.code == evdev.ecodes.ABS_RZ and event.value <= 32000:
                speed = round(map_value_forward(event.value, 0, 32000, 0, 100)) 
                print(f"right event value: {event.value}")


except KeyboardInterrupt:
    print("\nProgram interrupted! Cleaning up GPIO and exiting...")
    pass
finally:
    GPIO.cleanup()