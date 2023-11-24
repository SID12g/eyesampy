import RPi.GPIO as g
import time
import Adafruit_DHT as dht

buttonPin = 26

g.setwarnings(False)

g.setmode(g.BCM)
g.setup(16, g.OUT) # 위험 단계 : 괜찮음 (초록색)
g.setup(20, g.OUT) # 위험 단계 : 주의 (노란색)
g.setup(21, g.OUT) # 위험 단계 : 위험 (빨간색)
g.setup(buttonPin, g.IN, pull_up_down = g.PUD_DOWN) # 위험 단계를 초기화 시키는 버튼
g.setup(12, g.OUT) # 위험 단계를 초기화 시키는 버튼 출력
g.setup(17, g.OUT) # 온도와 습도를 감지

warnLevel = 1 # 1: 괜찮음 (혹은 정보 수집 전), 2: 주의, 3: 위험

while True:
    if warnLevel == 1:
        print('1')
    elif warnLevel == 2:
        print('2')
    elif warnLevel == 3:
        print('3')
    if g.input(buttonPin) == g.HIGH:
        warnLevel = 1
        print("정상화")
    try:
        while True:
            humidity, temperature = dht.read_retry(dht.DHT22,17) # 17번 핀으로 습도, 온도 감지, humidity = 습도, temperature = 온도
            
    except KeyboardInterrupt:
        g.cleanup()

g.cleanup()
