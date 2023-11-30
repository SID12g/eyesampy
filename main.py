# 필요한 파일을 임포트
import RPi.GPIO as g
import time
import Adafruit_DHT as dht
import spidev
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
import os 

# .env에서 파이어베이스 관련 파일 주소 가져오기
load_dotenv()
MAIN_PATH = os.environ.get('MAIN_PATH')

# Firebase Admin SDK에서 다운로드한 서비스 계정 키(JSON 파일) 경로
# Firestore 클라이언트 초기화
cred = credentials.Certificate(MAIN_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 핀 지정
buttonPin = 6
TRIGER = 24
ECHO = 23
buzzer = 13
soundPin = 7
RIGHT_PWM = 12
RIGHT_FORWARD = 19
RIGHT_BACKWARD = 26

# 경고 False
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
g.setup(soundPin, g.IN) # 사운드 센서
g.setup(RIGHT_PWM,g.OUT) # 아래까지 모터 관련 핀 지정
g.setup(RIGHT_FORWARD,g.OUT)
g.setup(RIGHT_BACKWARD,g.OUT)

# 모터 관련 pwm 코드
RIGHT_MOTOR = g.PWM(RIGHT_PWM, 100)
RIGHT_MOTOR.start(0)

# 초음파 센서를 위해 값 초기화
startTime = time.time()
endTime = time.time()


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

# 모터 관련 함수
def rightMotor(forward, backward, pwm):
    g.output(RIGHT_FORWARD, forward)
    g.output(RIGHT_BACKWARD, backward)
    RIGHT_MOTOR.ChangeDutyCycle(pwm)
    



while True:
    # 부저 초기화
    g.output(buzzer, False)
    # 모터 초기화
    rightMotor(0,0,0)
    brightness = ReadVol(0) # 밝기 정의

    # 버튼이 눌릴 경우, 코드 종료
    if g.input(buttonPin) == g.HIGH:
        warnLevel = 1
        print("stop")
        exit(0)
        
    # 1레벨일 경우 초록 LED
    if warnLevel == 1:
        print('w1')
        g.output(16, False)
        g.output(20, False)
        g.output(21, False)
        g.output(16, True)

    # 2레벨일 경우 노란 LED
    elif warnLevel == 2:
        print('w2')
        g.output(16, False)
        g.output(20, False)
        g.output(21, False)
        g.output(20, True)

    # 3레벨일 경우 빨간 LED와 여러 장치 실행
    elif warnLevel == 3:
        print('w3')
        g.output(16, False)
        g.output(20, False)
        g.output(21, False)
        g.output(21, True)

        # 위험 상태 도달 시 부저로 알림
        g.output(buzzer, True)
        # 모터 회전
        rightMotor(1, 0, 100)
        time.sleep(8)
        rightMotor(0,0,0)


    # 초음파로 거리 측정
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

    soundLevel = g.input(soundPin)
        
    
    # 온도, 습도 측정 후 반환
    try:
        while True:
            humidity, temperature = dht.read_retry(dht.DHT11,17) # 17번 핀으로 습도, 온도 감지, humidity = 습도, temperature = 온도
            break
    # if 문으로 온습도에 따라서 단게 변경

    except KeyboardInterrupt:
        g.cleanup()

    # 밝기 재정의
    brightness = ReadVol(0)

    # 조건문에 따라 레벨 지정

    if 700>brightness:
        warnLevel = 2
    if 20>dist1:
        warnLevel = 2
    if 300>brightness:
        warnLevel = 3
    if 10>dist1:
        warnLevel = 3
    
    # 정보 출력
    print("temp : ", temperature)
    print("humi : ", humidity)
    print("dist:", dist1)
    print("bright : ", brightness)
    print("warnLevel : ", warnLevel)
    print("soundLevel", soundLevel)
    time.sleep(10)

   # 저장할 데이터
    new_data = {
        "temp":temperature,
        "humi":humidity,
        "dist":dist1,
        "bright":brightness,
        "sound":soundLevel
    }

    # 데이터를 저장할 컬렉션 및 문서 참조 생성

    collection_ref = db.collection("info")
    doc_id = "set1"
    doc_ref = collection_ref.document(doc_id)
    doc_ref.update(new_data)
    # 데이터 전송 확인
    print("확인하세요")
       
g.cleanup()
