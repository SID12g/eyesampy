import RPi.GPIO as g
import time
import Adafruit_DHT as dht
import spidev

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
g.setup(12, g.OUT) # 위험 단계를 초기화 시키는 버튼 
g.setup(17, g.OUT) # 온도와 습도를 감지 온도 : tenprature, 습도 : humidity
g.setup(ECHO,g.IN) # 초음파 ECHO
g.setup(TRIGER,g.OUT) # 초음파 TRIGER 거리 : dist1
g.setup(buzzer, g.OUT) # 부저 등록

startTime = time.time()
endTime = time.time()

# 부저 코드
pwm = g.PWM(buzzer, 100)
pwm.start(50)

# 조도 센서 코드
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

warnLevel = 1 # 1: 괜찮음 (혹은 정보 수집 전), 2: 주의, 3: 위험

# 조도 센서 관련 함수
def ReadVol(vol):
    adc = spi.xfer2([1, (0x08+vol) << 4, 0])
    data = ((adc[1]&0x03) << 8) + adc[2]
    return data



while True:
    
    brightness = ReadVol(0) # 밝기 정의
    # 코드 쓸 때 brightness < 100 이런 식으로 작성 if문 사용
    if g.input(buttonPin) == g.HIGH:
        warnLevel = 1
        print("stop")
        exit(0)
        
    if warnLevel == 1:
        print('w1')
        g.output(16, False)
        g.output(20, False)
        g.output(21, False)
        g.output(16, True)
        pwm.ChangeFrequency(1)
    elif warnLevel == 2:
        print('w2')
        g.output(16, False)
        g.output(20, False)
        g.output(21, False)
        g.output(20, True)
        pwm.ChangeFrequency(1)
    elif warnLevel == 3:
        print('w3')
        g.output(16, False)
        g.output(20, False)
        g.output(21, False)
        g.output(21, True)
        pwm.ChangeFrequency(261)
        time.sleep(1)
    
        # 위험 상태 도달 시 부저로 알림
        pwm.ChangeDutyCycle(50)
        pwm.ChangeFrequency(261) 
        time.sleep(1.0)
    if g.input(buttonPin) == g.HIGH:
        warnLevel = 1
        print("정상화")
    
    
    g.output(TRIGER,g.LOW)
    time.sleep(0.1)
    
    g.output(TRIGER,g.HIGH)
    time.sleep(0.00001)
    g.output(TRIGER,g.LOW)
    
    while g.input(ECHO) == g.LOW:
        startTime = time.time()
        if g.input(ECHO) == g.HIGH:
            break
    while g.input(ECHO) == g.HIGH:
        endTime = time.time()
        if g.input(ECHO) == g.LOW:
            break
        
        
    period = endTime - startTime
    dist1 = round(period * 1000000/58,2)


    

    try:
        while True:
            humidity, temperature = dht.read_retry(dht.DHT11,17) # 17번 핀으로 습도, 온도 감지, humidity = 습도, temperature = 온도
            break
    # if 문으로 온습도에 따라서 단게 변경

    except KeyboardInterrupt:
        g.cleanup()

    

    if 700>brightness:
        warnLevel = 2
    if 100>brightness:
        warnLevel = 3
    if 20>dist1:
        warnLevel = 2
    if 10>dist1:
        warnLevel = 3
    
    print("temp : ", temperature)
    print("humi : ", humidity)
    print("dist:", dist1)
    print("bright : ", brightness)
    print("warnLevel : ", warnLevel)
       
g.cleanup()
