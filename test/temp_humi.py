import RPi.GPIO as g
import time
import Adafruit_DHT as dht

g.setmode(g.BCM)
g.setup(17, g.OUT)


try:
    while True:
        h,t = dht.read_retry(dht.DHT22,17)
        print(h, t)
      
except KeyboardInterrupt:
    g.cleanup()