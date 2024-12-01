import cv2
from copy import deepcopy
from deepface import DeepFace
from concurrent.futures import ThreadPoolExecutor

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
reference_img = cv2.imread("images/reference.png")
face_match = False
executor = ThreadPoolExecutor(max_workers=1)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def check_face(frame):
    global face_match
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            if DeepFace.verify(face_roi, deepcopy(reference_img))['verified']:
                face_match = True
                return
        face_match = False
    except Exception as e:
        print(f"Error: {e}")
        face_match = False

while True:
    ret, frame = cap.read()

    if ret:
        if counter % 100 == 0:  # Check every 100 frames
            executor.submit(check_face, frame.copy())
        counter += 1

        if face_match:
            cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        cv2.imshow('video', frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
executor.shutdown(wait=True)
cv2.destroyAllWindows()
