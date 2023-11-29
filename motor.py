import RPi.GPIO as g
import time

RIGHT_PWM = 12
RIGHT_FORWARD = 19
RIGHT_BACKWARD = 26

g.setmode(g.BCM)

g.setup(RIGHT_PWM,g.OUT)
g.setup(RIGHT_FORWARD,g.OUT)
g.setup(RIGHT_BACKWARD,g.OUT)

RIGHT_MOTOR = g.PWM(RIGHT_PWM, 100)
RIGHT_MOTOR.start(0)

def rightMotor(forward, backward, pwm):
    g.output(RIGHT_FORWARD, forward)
    g.output(RIGHT_BACKWARD, backward)
    RIGHT_MOTOR.ChangeDutyCycle(pwm)
    
while True:
    rightMotor(1,0,70)
    time.sleep(2)
