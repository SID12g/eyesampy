import RPi.GPIO as g
import time
import Adafruit_DHT as dht


ideal_h,ideal_t = map(int,input().split())

try:
    while True:
        h,t = dht.read_retry(dht.DHT22,17)
        print(h, t)
      
except KeyboardInterrupt:
    g.cleanup()