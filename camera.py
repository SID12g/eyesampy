import cv2
import dlib
from functools import wraps
from scipy.spatial import distance
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Firebase Admin SDK에서 다운로드한 서비스 계정 키(JSON 파일) 경로
# Firestore 클라이언트 초기화
cred = credentials.Certificate('./eyesam-e6e07-firebase-adminsdk-4dy60-2b086dfa75.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
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

# 변수 및 상수 설정
blink_count = 0
start_time = time.time()
last_blink_time = start_time

# gpio 셋팅
last_save = 0

def counter(func):
    @wraps(func)
    def tmp(*args, **kwargs):
        tmp.count += 1
        time.sleep(0.05)
        global last_save
        global start_time
        elapsed_time = time.time() - start_time
        if elapsed_time > 10:  # 30초이 지나면 초기화
            start_time = time.time()
            # 저장할 데이터
            new_data = {
                "blink":tmp.count
            }
            # 데이터를 저장할 컬렉션 및 문서 참조 생성
            collection_ref = db.collection("info")
            doc_id = "set1"
            doc_ref = collection_ref.document(doc_id)
            doc_ref.update(new_data)
            print("확인하세요")
            # 새로 생성된 문서의 ID 출력
            print("Document added with ID:", doc_ref.id)
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