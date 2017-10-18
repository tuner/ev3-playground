#!/usr/bin/env python3

# Author: Kari Lavikka

import math
from ev3dev.ev3 import *
from time import sleep
from pilot import Pilot


if __name__ == "__main__":
    print("Kukkuu")

    pilot = Pilot(4.25, 14.2, LargeMotor("outA"), LargeMotor("outB"))

    ir = InfraredSensor() 
    assert ir.connected, "Connect a single infrared sensor to any sensor port"
    ir.mode = 'IR-PROX'

    btn = Button()

    wall_distance = ir.value()
    print("Initial wall distance: " + str(wall_distance))

    pilot.travel_indefinitely()
    last_blocked = pilot.get_travelled_distance()
    previous_print = -10000000


    while True:
        wall_distance = ir.value()
        travel_distance = pilot.get_travelled_distance()

        if travel_distance - previous_print > 5:
            print("Travelled {} cm, wall distance: {}".format(pilot.get_travelled_distance(), wall_distance))
            previous_print = travel_distance

        if wall_distance < 20:
            # Blocked
            last_blocked = travel_distance
            Leds.set_color(Leds.LEFT, Leds.RED)

        else:
            Leds.set_color(Leds.LEFT, Leds.GREEN)
            if travel_distance - last_blocked >= 40:
                pilot.stop()
                pilot.arc(15, -90, stop_action="coast")
                pilot.travel(-8, stop_action="coast")
                pilot.arc(-10, 90)
                break

    Sound.beep()       
    Leds.set_color(Leds.LEFT, Leds.GREEN)  

    pilot.relax()

