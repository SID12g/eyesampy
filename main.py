import RPi.GPIO as g
import time
import Adafruit_DHT as dht

buttonPin = 26
TRIGER = 24
ECHO = 23
buzzer = 13

g.setwarnings(False)

g.setmode(g.BCM)
g.setup(16, g.OUT) # 위험 단계 : 괜찮음 (초록색)
g.setup(20, g.OUT) # 위험 단계 : 주의 (노란색)
g.setup(21, g.OUT) # 위험 단계 : 위험 (빨간색)
g.setup(buttonPin, g.IN, pull_up_down = g.PUD_DOWN) # 위험 단계를 초기화 시키는 버튼
g.setup(12, g.OUT) # 위험 단계를 초기화 시키는 버튼 출력
g.setup(17, g.OUT) # 온도와 습도를 감지
g.setup(ECHO,g.IN) # 초음파 ECHO
g.setup(TRIGER,g.OUT) # 초음파 TRIGER
g.setup(buzzer, g.OUT) # 부저 등록

pwm = g.PWM(buzzer, 100)
pwm.start(50)

warnLevel = 1 # 1: 괜찮음 (혹은 정보 수집 전), 2: 주의, 3: 위험

while True:
    if warnLevel == 1:
        print('1')
    elif warnLevel == 2:
        print('2')
    elif warnLevel == 3:
        print('3')

        # 위험 상태 도달 시 부저로 알림
        pwm.ChangeDutyCycle(50)
        pwm.ChangeFrequency(261) 
        time.sleep(1.0)

    if g.input(buttonPin) == g.HIGH:
        warnLevel = 1
        print("정상화")
    try:
        while True:
            humidity, temperature = dht.read_retry(dht.DHT22,17) # 17번 핀으로 습도, 온도 감지, humidity = 습도, temperature = 온도
            
    except KeyboardInterrupt:
        g.cleanup()

    # 초음파 센서 부분   
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
    if dist1 <= 10 and dist2 <= 10:
        print("detect")
    else:
        print("no")

       
g.cleanup()
