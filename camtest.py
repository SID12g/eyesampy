import cv2
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if cap.isOpened():
    ret, frame = cap.read()
    while ret:
        ret, frame = cap.read()
        rect = cv2.rectangle(frame, (9, 9), (200, 200,), (0, 0, 255), 1)
        roi_img = frame[10:200, 10:200]
        gray_img = cv2.cvtColor(roi_img, cv2.COLOR_RGB2GRAY)
        mod_frame = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2RGB)

        frame[10:200, 10:200] = mod_frame
        cv2.imshow("camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()