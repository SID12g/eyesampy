import RPi.GPIO as g
import time
import Adafruit_DHT as dht
import spidev
import cv2
import dlib
from functools import wraps
from scipy.spatial import distance

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




# 카메라 관련 함수

def calculate_EAR(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear_aspect_ratio = (A + B) / (2.0 * C)
    return ear_aspect_ratio

# 카메라 셋팅
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# dlib 인식 모델 정의
hog_face_detector = dlib.get_frontal_face_detector()
dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# gpio 셋팅
lastsave = 0

def counter(func):
    @wraps(func)
    def tmp(*args, **kwargs):
        tmp.count += 1
        time.sleep(0.05)
        global lastsave
        if time.time() - lastsave > 5:
            lastsave = time.time()
            tmp.count = 0
        return func(*args, **kwargs)
    tmp.count = 0
    return tmp

@counter
def close():
    cv2.putText(frame, "DROWSY", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 4)

def sound():
    print("Driver is sleeping")
    # 여기에 알람을 울리기 위한 코드 추가

while True:
    ret, frame = cap.read()

    # 비디오 프레임이 비어 있는지 확인
    if not ret:
        print("비디오 프레임을 읽을 수 없습니다.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = hog_face_detector(gray)
    for face in faces:
        face_landmarks = dlib_facelandmark(gray, face)
        leftEye = []
        rightEye = []

        for n in range(36, 42):
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            leftEye.append((x, y))
            next_point = n + 1
            if n == 41:
                next_point = 36
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

        for n in range(42, 48):
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            rightEye.append((x, y))
            next_point = n + 1
            if n == 47:
                next_point = 42
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

        left_ear = calculate_EAR(leftEye)
        right_ear = calculate_EAR(rightEye)

        EAR = (left_ear + right_ear) / 2
        EAR = round(EAR, 2)

        if EAR < 0.19:
            close()
            print(f'close count: {close.count}')
            if close.count == 15:
                sound()
        print(EAR)

    cv2.imshow("Are you Sleepy", frame)

    key = cv2.waitKey(30)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()


#




while True:
    brightness = ReadVol(0) # 밝기 정의
    # 코드 쓸 때 brightness < 100 이런 식으로 작성

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
