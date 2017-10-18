#!/usr/bin/env python3

from ev3dev.ev3 import *
from time import sleep
from ev3dev.ev3 import Sound
import random

screen_width = 178
screen_height = 128

lcd = Screen()

ts = TouchSensor()
m1 = LargeMotor('outB')
m2 = LargeMotor('outC')

class Racket:
    width = 30
    thickness = 2
    distance_from_edge = 3

    bound_upper = width / 2
    bound_lower = screen_height - width / 2

    def __init__(self, side, motor):
        ''' side: -1 = left, 1 = right '''
        self.side = side
        self.pos = screen_height / 2
        self.motor = motor

        motor.reset()
        motor.position = self.pos

    def update(self):
        self.pos = self.motor.position

        if self.pos < self.bound_upper:
            self.pos = self.bound_upper
            self.motor.position = self.bound_upper

        if self.pos > self.bound_lower:
            self.pos = self.bound_lower
            self.motor.position = self.bound_lower
        

    def draw(self):
        x = self.distance_from_edge if self.side < 0 else screen_width - self.thickness - self.distance_from_edge - 1
        y = self.pos - self.width / 2

        lcd.draw.rectangle((x, y, x + self.thickness, y + self.width), fill = "black")


racket_left = Racket(-1, m1)
racket_right = Racket(1, m2)

class Ball:
    def __init__(self):
        self.radius = 3
        self.reset()

    def reset(self):
        self.x = screen_width / 2
        self.y = screen_height / 2
        self.xv = random.choice((-6, -4, 4, 6))
        self.yv = random.choice((-4, -3, -2, 2, 3, 4))

    def update(self):
        self.x += self.xv
        self.y += self.yv

        if self.x - self.radius <= racket_left.thickness + racket_left.distance_from_edge:
            if self.y < racket_left.pos - racket_left.width / 2 or self.y > racket_left.pos + racket_left.width:
                Sound.tone(250, 100).wait()
                Sound.tone(500, 100).wait()
                self.reset()
            else:
                self.xv = -self.xv
                self.yv += 1 if self.y > racket_left.pos else -1
                m1.run_timed(time_sp = 20, speed_sp = 900 * self.yv / abs(1 if self.yv == 0 else self.yv))

        if self.x + self.radius >= screen_width - racket_left.thickness - racket_left.distance_from_edge:
            if self.y < racket_right.pos - racket_right.width / 2 or self.y > racket_right.pos + racket_right.width:
                Sound.tone(250, 100).wait()
                Sound.tone(500, 100).wait()
                self.reset()
            else:
                self.xv = -self.xv
                self.yv += 1 if self.y > racket_right.pos else -1
                m2.run_timed(time_sp = 20, speed_sp = 900 * self.yv / abs(1 if self.yv == 0 else self.yv))

        if self.y + self.radius >= screen_height or self.y - self.radius <= 0:
            self.yv = -self.yv
            Sound.tone(2000, 5)

    def draw(self):
        lcd.draw.ellipse(
                (self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius),
                fill = "black")



ball = Ball()

objects = (ball, racket_left, racket_right)

while not ts.value():
    lcd.clear()

    for o in objects:
        o.draw()
    
    lcd.update()

    sleep(0.01)

    for o in objects:
        o.update()

    
