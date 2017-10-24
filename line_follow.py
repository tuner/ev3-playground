#!/usr/bin/env python3

# Author: Kari Lavikka

from ev3dev.ev3 import *
from time import sleep, time
from pilot import Pilot

sensor_distance = 5.5 # Distance from wheel axis

pilot = Pilot(4.25, 14.2, LargeMotor("outA"), LargeMotor("outB"))

col = ColorSensor()
col.mode = 'COL-REFLECT'


def interpolate(a, b, ratio):
    return a + (b - a) * ratio


def measure_line_reflections():
    print("Measuring reflections:")
    pilot.max_speed = 150
    pilot.travel_indefinitely()

    measurements = list()

    while pilot.get_travelled_distance() < 13:
        measurements.append((pilot.get_travelled_distance(), col.value()))
        sleep(0.05)
    
    pilot.relax()

    min_value = min(x[1] for x in measurements)
    max_value = max(x[1] for x in measurements)

    middle_value = (min_value + max_value) / 2
    
    bright_proportion = float(sum(x[1] > middle_value for x in measurements)) / len(measurements)
    white_on_black = bright_proportion < 0.5

    # Find edge position
    edge_pos = 0
    for distance, value in measurements:
        if (value > middle_value) ^ (not white_on_black):
            edge_pos = distance

    distance_to_edge = pilot.get_travelled_distance() - edge_pos

    pilot.max_speed = 150
    pilot.arc(distance_to_edge - sensor_distance, -90)
    pilot.travel(-sensor_distance)

    print("At the edge!")
    pilot.stop()

    print("min: {}, middle: {}, max: {}".format(min_value, middle_value, max_value))

    return (middle_value, max_value - min_value)


def bound(min_value, value, max_value):
    return max(min(value, max_value), min_value)

def follow(edge_value, reflection_scale):
    btn = Button()

    pilot.max_speed = 400
    max_speed = 900.0

    while not btn.any():
        value = col.value()

        curve = (value - edge_value) / reflection_scale * 3

        speed = max_speed / (1 + abs(curve) * 2)
        if speed > pilot.max_speed:
            # Accelerate slowly
            speed = interpolate(pilot.max_speed, speed, 0.03)
        else:
            speed = interpolate(pilot.max_speed, speed, 0.5)

        #print("value: {}, curve: {}, speed: {}".format(value, curve, speed))

        pilot.curve = curve #interpolate(pilot.curve, curve, 0.8)
        pilot.max_speed = speed
        #print("value: {}, curve: {}, speed: {}".format(value, pilot.curve, pilot.max_speed))
        pilot.travel_indefinitely()
        #sleep(0.01)

    pilot.relax()


def pid_follow(edge_value, reflection_scale):
    btn = Button()

    pilot.max_speed = 400
    max_speed = 900.0

    kp = 0.9
    ki = 1.5
    kd = 40.0

    integral_dampening = 0.98

    integral = 0.0

    previous_error = 0
    last_time = time()
    start_time = last_time

    while not btn.any():
        value = float(col.value())

        current_time = time()
        time_delta = current_time - last_time
        last_time = current_time

        # Error range is [-1, 1]
        error = (value - edge_value) / reflection_scale * 2
        error = bound(-1, error, 1)
        integral = (1 - integral_dampening * time_delta) * integral + error * time_delta
        derivative = (error - previous_error) * time_delta
        previous_error = error

        m_error = kp * error
        m_integral = ki * integral
        m_derivative = kd * derivative

        curve = m_error + m_integral + m_derivative
        curve = bound(-2, curve, 2)

        #speed = max_speed / (1 + min(abs(curve), 2) * 2)
        speed = max_speed * (1 - abs(error) * 0.9)
        if speed > pilot.max_speed:
            # Accelerate slowly
            speed = interpolate(pilot.max_speed, speed, 0.02)
        else:
            speed = interpolate(pilot.max_speed, speed, 0.08)

        #print("value: {}, curve: {}, speed: {}".format(value, curve, speed))

        pilot.curve = curve #interpolate(pilot.curve, curve, 0.8)
        pilot.max_speed = speed
        #print("{:10.3f}, error: {:10.3f}, integral: {:10.3f}, derivative: {:10.3f}, curve: {:10.3f}".format(
        #    current_time - start_time, m_error, m_integral, m_derivative, pilot.curve))
        pilot.travel_indefinitely()
        sleep(max(0, 0.01 - time_delta))

    pilot.relax()


if __name__ == "__main__":
    edge_value, scale = measure_line_reflections()

    pid_follow(edge_value, scale)


