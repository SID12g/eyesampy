import RPi.GPIO as g
import time

TRIGER = 24
ECHO = 23


g.setmode(g.BCM)
g.setup(ECHO,g.IN)
g.setup(TRIGER,g.OUT)

startTime = time.time()

while True:
    g.output(TRIGER,g.LOW)
    time.sleep(0.1)
    
    g.output(TRIGER,g.HIGH)
    time.sleep(0.00001)
    g.output(TRIGER,g.LOW)
    
    while g.input(ECHO) == g.LOW:
        startTime = time.time()
    while g.input(ECHO) == g.HIGH:
        endTime = time.time()
        
    period = endTime - startTime
    dist1 = round(period * 1000000/58,2)
    dist2 = round(period * 17241,2)
    
    print(dist1,dist2)
   