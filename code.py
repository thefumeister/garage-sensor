# System import
import time
import board
from adafruit_circuitplayground import cp
import digitalio
import adafruit_hcsr04

# setting up proximity sensor
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.RX, echo_pin=board.TX)
distance = sonar.distance

# setting up sound sensor and creating a list to measure for average noise over a period (numlist) seconds
noise = cp.sound_level
noiseAverage = [0, 0, 0, 0, 0, 0]

# setting up PIR motion sensor
PIR_PIN = board.A1
pir = digitalio.DigitalInOut(PIR_PIN)
pir.direction = digitalio.Direction.INPUT

# setting up neopixel output and color variables
cp.pixels.brightness = 0.5
tooFar = [200, 200, 200]
far = [0, 100, 200]
optimal = [0, 200, 0]
close = [200, 200, 0]
tooClose = [200, 0, 0]
unknown = [100, 100, 100]

# variables for detecting a moving vehicle
motion = False
car = False
timer = time.monotonic()

# variable to prevent system from triggering due to background noise
noiseThreshold = 150
# variables for checking sound over 5 seconds
soundTime = time.monotonic()
soundInt = 1

while True:

    # check for the average noise level over a period of 6 seconds
    # as that is how long it takes for a garage door to lift up
    if time.monotonic() >= soundTime:
        # add one second to soundTime so loop tiggers in full second intervals
        soundTime += soundInt
        # adding current sound level to a list and dropping the oldest sound reading in the list
        noiseAverage.append(cp.sound_level)
        noiseAverage.pop(0)
        # finding the average sound value out of the 5 values in the list
        noiseLevel = sum(noiseAverage) / len(noiseAverage)
    # Change a variable when the motion sensor is triggered for 20 seconds before reading the motion sensor again
    if pir.value:
        motion = True
        timer = time.monotonic()
    # 20 seconds is used, but can be replaced
    elif (timer + 20) <= time.monotonic():
        motion = False
    # Change another variable so that if there is motion and a loud consistent noise
    # then the program will recognize there is a car and change the variable accordingly
    if motion == True and noiseLevel >= noiseThreshold:
        car = True
    else:
        car = False
    # When a car is detected, the LED Neopixels will activate
    if car == True:
        # Assign the proximity sensor reading to a variable
        carDistance = sonar.distance
        # Above 3  meters, the car is too far and the LEDs shine White
        if 1000 > carDistance > 300:
            cp.pixels.fill(tooFar)
        # Between 3 and 1 meter, the car is far and the LEDs shine Blue
        elif 300 >= carDistance > 100:
            cp.pixels.fill(far)
        # Between 1 and 0.5 meter, the car is in a good spot and the LEDs shine Green
        elif 100 >= carDistance > 50:
            cp.pixels.fill(optimal)
        # Between 0.5 and 0.3 meter, the car is too close and the LEDs shine Yellow
        elif 50 >= carDistance > 30:
            cp.pixels.fill(close)
        # Below 0.3 meter, the car is in danger of crashing into the wall and the LEDs shine Red
        elif 30 > carDistance:
            cp.pixels.fill(tooClose)
        # Safety for read errors
        else:
            cp.pixels.fill(unknown)
    # If the sound level is above the threshold but motion is not detected
    # it will be assumed that the car is flooding the house with carbon monoxide
    # and the program will trigger a sound indicator
    elif car == False and noiseLevel >= noiseThreshold:
        print("alert")
        cp.play_tone(4800, 0.1)
        cp.pixels.fill(0)
        motion = False
    # if sound levels are below the threshold then lights are turned off
    else:
        cp.pixels.fill(0)
