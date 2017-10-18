#!/usr/bin/env python3

# Author: Kari Lavikka

from ev3dev.ev3 import *
from time import sleep
from pilot import Pilot


def interpolate(a, b, ratio):
    return a + (b - a) * ratio

if __name__ == "__main__":
    print("Kukkuu")

    btn = Button()
    col = ColorSensor()
    col.mode = 'COL-REFLECT'

    max_speed = 900.0

    pilot = Pilot(4.25, 14.2, LargeMotor("outA"), LargeMotor("outB"))

    while not btn.any():
        value = col.value()

        curve = (value - 24) / 10 

        speed = max_speed / (1 + abs(curve) * 2)
        if speed > pilot.max_speed:
            # Accelerate slowly
            speed = interpolate(pilot.max_speed, speed, 0.03)
        else:
            speed = interpolate(pilot.max_speed, speed, 0.8)

        #print("value: {}, curve: {}, speed: {}".format(value, curve, speed))

        pilot.curve = interpolate(pilot.curve, curve, 0.5)
        pilot.max_speed = speed
        pilot.travel_indefinitely()
        sleep(0.01)

    pilot.relax()





