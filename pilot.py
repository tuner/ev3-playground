
# Author: Kari Lavikka

import math
from ev3dev.ev3 import *
from time import sleep


class Pilot(object):
    """
    Pilot is a high-level steering abstraction for a two-wheeled robot.
    This is inspired by the leJOS DiffrerentialPilot class. 
    """

    def __init__(self, wheel_diameter, track_width, motor_left, motor_right):
        self.motors = [motor_left, motor_right]
        self.motor_offsets = [-track_width / 2, track_width / 2]
        self.max_speed = 500
        self.curve = 0

        self.offset_start = self._current_offset()
        self.distance_angle_ratio = 1.0 / (math.pi * wheel_diameter) * 360.0
    

    def _current_offset(self):
        return sum((m.position for m in self.motors)) / 2


    def get_travelled_distance(self):
        return (self._current_offset() - self.offset_start) / self.distance_angle_ratio
    

    def get_rotation_difference(self):
        pass

    def _wait_motors(self):
        for m in self.motors:
            m.wait_while("running")
        

    def travel(self, distance, stop_action="hold"):
        motor_degrees = distance * self.distance_angle_ratio

        for m in self.motors:
            m.run_to_rel_pos(position_sp=motor_degrees, speed_sp=self.max_speed, stop_action=stop_action)
        
        self._wait_motors()
    

    def travel_indefinitely(self, forward=True):
        #self.offset_start = self._current_offset()

        speeds = self._get_curved_speed()
        for i, m in enumerate(self.motors):
            m.run_forever(speed_sp=speeds[i] * (1 if forward else -1))


    def _get_curved_speed(self):
        ABSOLUTELY_MAX_SPEED = 1000

        normal = self.max_speed
        slow = max(-ABSOLUTELY_MAX_SPEED, self.max_speed - self.max_speed * abs(self.curve))
        return [slow, normal] if self.curve < 0 else [normal, slow]


    def calc_distance(self, radius, degrees):
        return 2 * math.pi * radius * degrees / 360.0 * self.distance_angle_ratio


    def arc(self, radius, degrees, stop_action="hold"):
        motor_degrees = [self.calc_distance(-radius - r, -degrees) for r in self.motor_offsets]

        max_degrees = max((abs(d) for d in motor_degrees))
        motor_speeds = [abs(d) / max_degrees * self.max_speed for d in motor_degrees]

        for i, m in enumerate(self.motors):
            m.run_to_rel_pos(position_sp=motor_degrees[i], speed_sp=motor_speeds[i], stop_action=stop_action)
        
        self._wait_motors()


    def stop(self, stop_action="hold"):
        for m in self.motors:
            m.stop(stop_action=stop_action)


    def relax(self):
        self.stop("brake") 

