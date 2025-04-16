# DC motor
import RPi.GPIO as GPIO
import time
# Controller
import evdev
import numpy as np
# LED
import threading
import pigpio
# GPIO Mode (Uses pin numbers)
GPIO.setmode(GPIO.BOARD)

# Pin Variables
# Left Motor
left_motor_pin1 = 11
left_motor_pin2 = 13

# Right motor
right_motor_pin1 = 19
right_motor_pin2 = 21

# Turret Motor
turret_pin_left = 18
turret_pin_right = 16

# IR LED Emitter Pin
emitter_pin = 12 # pigpio needs gpio numbers

# Fire Indicator LED Pin
indicator_pin = 22

# Health Indicator LED Pin
health_pin = 33

# Sensor Pin
sensor_vout_pin = 31

# pigpio stuff
# pigpio instance
pi = pigpio.pi()
if not pi.connected:
    print("Could not connect to pigpio daemon!")
    exit(1)

# Motors
# Left Motor
GPIO.setup(left_motor_pin1, GPIO.OUT)
GPIO.setup(left_motor_pin2, GPIO.OUT)
left1_pwm = GPIO.PWM(left_motor_pin1, 10000)
left2_pwm = GPIO.PWM(left_motor_pin2, 10000)  # 10000 is PWM
left1_pwm.start(0)
left2_pwm.start(0)

# Right Motor
GPIO.setup(right_motor_pin1, GPIO.OUT)
GPIO.setup(right_motor_pin2, GPIO.OUT)
right3_pwm = GPIO.PWM(right_motor_pin1, 10000)
right4_pwm = GPIO.PWM(right_motor_pin2, 10000)  # 10000 is PWM
right3_pwm.start(0)
right4_pwm.start(0)

# Turret Motor
GPIO.setup(turret_pin_left, GPIO.OUT)
GPIO.setup(turret_pin_right, GPIO.OUT)
turret_left_pwm = GPIO.PWM(turret_pin_left, 10000)
turret_right_pwm = GPIO.PWM(turret_pin_right, 10000)
turret_left_pwm.start(0)
turret_right_pwm.start(0)

# Pin for Sensors
#GPIO.setup(sensor_vout_pin,GPIO.IN)
GPIO.setup(sensor_vout_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_hit_time = 0


# Trigger for Firing
GPIO.setup(emitter_pin,GPIO.OUT)
emitter=GPIO.PWM(emitter_pin,9250)
emitter.start(0)

GPIO.setup(indicator_pin,GPIO.OUT)
indicator=GPIO.PWM(indicator_pin,1000)
indicator.start(0)

cooldown_time = 1 # To implement 1 second firing cooldown
firing = False

def handle_firing():
    global firing
    firing = True
    indicator.ChangeDutyCycle(100)

    # Start 37kHz PWM with 50% duty cycle on GPIO 12
    pi.hardware_PWM(emitter_pin, 37000, 500000)  # GPIO 12, 37kHz, 50%

    time.sleep(0.1)  # Duration of firing — adjust as needed

    # Stop PWM
    pi.hardware_PWM(emitter_pin, 0, 0)
    indicator.ChangeDutyCycle(0)

    time.sleep(cooldown_time)
    firing = False



# Health
GPIO.setup(health_pin, GPIO.OUT)
health_pwm = GPIO.PWM(health_pin, 1000)
health_pwm.start(100)

last_blink = time.time()
led_on = True
health = 3
last_health = health

def health_led_blink_loop():
    global last_blink, led_on, health
    while True:
        now = time.time()
        if health == 3:
            health_pwm.ChangeDutyCycle(100)
        elif health == 2 and now - last_blink >= 1:
            last_blink = now
            health_pwm.ChangeDutyCycle(0 if led_on else 100)
            led_on = not led_on
        elif health == 1 and now - last_blink >= 0.5:
            last_blink = now
            health_pwm.ChangeDutyCycle(0 if led_on else 100)
            led_on = not led_on
        elif health <= 0:
            health_pwm.ChangeDutyCycle(0)
            led_on = False
        time.sleep(0.05)

# Check Sensor
def sensor_check_loop():
    global health, last_hit_time
    while True:
        if GPIO.input(sensor_vout_pin) == GPIO.LOW and (time.time() - last_hit_time) > 1:
            health -= 1
            print(f"Current Health: {health}")
            last_hit_time = time.time()
        time.sleep(0.05)

# Controller
def map_value_backward(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_min, out_max])

def map_value_forward(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_max, out_min])
# The above function swaps out_max and out_min to correctly modify speed
# When the joystick is pushed forward its value decreases to 0 and the output speed should be 100

# Controller Event Number
device = evdev.InputDevice('/dev/input/event9')
print(device)

# Motor control methods
# Left Motor
def left_forward(speed):
    print(f"Going Forward at {speed}%")
    GPIO.output(left_motor_pin1, True)
    GPIO.output(left_motor_pin2, False)
    left1_pwm.ChangeDutyCycle(speed)

def left_backward(speed):
    print(f"Going Backward at {speed}%")
    GPIO.output(left_motor_pin2, True)
    GPIO.output(left_motor_pin1, False)
    left2_pwm.ChangeDutyCycle(speed)

# Right Motor
def right_forward(speed):
    print(f"Going Forward at {speed}%")
    GPIO.output(right_motor_pin1, True)
    GPIO.output(right_motor_pin2, False)
    right3_pwm.ChangeDutyCycle(speed)

def right_backward(speed):
    print(f"Going Backward at {speed}%")
    GPIO.output(right_motor_pin2, True)
    GPIO.output(right_motor_pin1, False)
    right4_pwm.ChangeDutyCycle(speed)

# Turret Motor
def turret_left():
    print(f"Turret Rotating Left")
    GPIO.output(turret_pin_left, True)
    GPIO.output(turret_pin_right, False)
    turret_left_pwm.ChangeDutyCycle(50)

def turret_right():
    print(f"Turret Rotating Right")
    GPIO.output(turret_pin_left, False)
    GPIO.output(turret_pin_right, True)
    turret_right_pwm.ChangeDutyCycle(50)


# Threads
# Health Blink Thread
blink_thread = threading.Thread(target=health_led_blink_loop, daemon=True)
blink_thread.start()

# Sensor Thread
sensor_thread = threading.Thread(target=sensor_check_loop, daemon=True)
sensor_thread.start()

try:
    for event in device.read_loop():
        # Grab Current Time
        current_time = time.time()

        if event.type == evdev.ecodes.EV_ABS:
            # Left Motor
            # Forward
            if event.code == evdev.ecodes.ABS_Y and event.value <= 31100:
                speed = round(map_value_forward(event.value, 0, 31100, 0, 100))
                print(f"Left Joystick Up: {event.value}")
                left_forward(speed) # Left Trigger Up Is 0
            # Backward
            elif event.code == evdev.ecodes.ABS_Y and event.value >= 43100:
                speed = round(map_value_backward(event.value, 43100, 65535, 0, 100))
                print(f"Left Joystick Down: {event.value}")
                left_backward(speed)
            # Joystick Neutral Zone
            elif event.code == evdev.ecodes.ABS_Y: 
                print(f"left neutral zone value: {event.value}")
                left1_pwm.ChangeDutyCycle(0)
                left2_pwm.ChangeDutyCycle(0)
                GPIO.output(left_motor_pin1, False)
                GPIO.output(left_motor_pin2, False)

            # Right Motor
            # Forward
            if event.code == evdev.ecodes.ABS_RZ and event.value <= 32000:
                speed = round(map_value_forward(event.value, 0, 32000, 0, 100)) 
                print(f"Right Joystick Up: {event.value}")
                right_forward(speed) # Right Trigger up is 0
            # Backward
            elif event.code == evdev.ecodes.ABS_RZ and event.value >= 34600:
                speed = round(map_value_backward(event.value, 34600, 65535, 0, 100))
                print(f"Right Joystick Down: {event.value}")
                right_backward(speed)
            # Joystick Neutral Zone
            elif event.code == evdev.ecodes.ABS_RZ:
                print(f"right neutral zone value: {event.value}")
                right3_pwm.ChangeDutyCycle(0) 
                right4_pwm.ChangeDutyCycle(0) 
                GPIO.output(right_motor_pin1, False)
                GPIO.output(right_motor_pin2, False)

            # Right Trigger (Fire)
            # Check for Fully Pressed Trigger (1023 value)
            if event.code == evdev.ecodes.ABS_GAS and event.value == 1023:
                if not firing:
                    print("Right Trigger Fire")
                    threading.Thread(target=handle_firing, daemon=True).start()
                else:
                    print("Can't fire during cooldown period")


        # Bumpers
        if event.type == evdev.ecodes.EV_KEY:
            # Left Bumper (Rotate Turret Left)
            if event.code == evdev.ecodes.BTN_TL and event.value == 1:
                turret_left()
            elif event.code == evdev.ecodes.BTN_TL and event.value == 0:
                print(f"Left Bumper Released")
                turret_left_pwm.ChangeDutyCycle(0)
                turret_right_pwm.ChangeDutyCycle(0)
                GPIO.output(turret_pin_left, False)
                GPIO.output(turret_pin_right, False)
                
            # Right Bumper (Rotate Turret Right)
            if event.code == evdev.ecodes.BTN_TR and event.value == 1:
                turret_right()
            elif event.code == evdev.ecodes.BTN_TR and event.value == 0:
                print(f"Right Bumper Released")
                turret_left_pwm.ChangeDutyCycle(0)
                turret_right_pwm.ChangeDutyCycle(0)
                GPIO.output(turret_pin_left, False)
                GPIO.output(turret_pin_right, False)

            # Start Button Health Reset
            if event.code == evdev.ecodes.BTN_START and event.value == 1:
                print(f"Health Reset to 3")
                health = 3
                led_on = True
                last_blink = time.time()
            if event.code == evdev.ecodes.BTN_START and event.value == 0:
                print(f"Start Button Released")

            # Pseudo Hit (A Button)
            if event.code == evdev.ecodes.BTN_SOUTH and event.value == 1:
                print(f"Pseudo Hit")
                health -= 1
            if event.code == evdev.ecodes.BTN_SOUTH and event.value == 0:
                print(f"A button released")

# Ctrl + C to End Program and Clean GPIO
except KeyboardInterrupt:
    print("\nProgram interrupted! Cleaning up GPIO and exiting...")
    pass
finally:
    pi.stop()
    GPIO.cleanup()

# To Do --------------------------------------------------------------
