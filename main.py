import cv2
import face_recognition
from threading import Thread
from typing import Optional, Tuple, List
from database_fetcher import DatabaseFetcher
from PIL import Image
from requests import get
from io import BytesIO
from settings import DB_PATH, KEY
from numpy import array


"""
Note:
The code only detects one person missing, I could add that functionality where it detects more than one per frame, but,
I feel like that would mess up the system especially with Arduino.

"""

DETECTION_INTERVAL = 60


class FaceRecognitionApp:
    __DEFAULT_DETECTION_INTERVAL = 60
    __DEFAULT_VIDEO_SOURCE = 0
    __DEFAULT_NAME = "Unknown"

    def __init__(self, video_source: int = __DEFAULT_VIDEO_SOURCE,
                 detection_interval: int = __DEFAULT_DETECTION_INTERVAL):
        self.__video_capture = cv2.VideoCapture(video_source)
        self.__detection_interval = detection_interval

        self.__known_face_encodings: List = []
        self.__known_face_names: List[str] = []

        self.__detected_face: bool = False
        self.__rectangle: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
        self.__current_name: Optional[str] = None

        self.__counter: int = 0

    def load_known_face(self, image_path: str, name: str) -> None:
        """
        Load a face from an image file and store its encoding with the given name.
        """
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        self.__known_face_encodings.append(encoding)
        self.__known_face_names.append(name)

    def load_known_face_with_url(self, image_url: str, name: str) -> None:
        """
        Load a face from an image file and store its encoding with the given name.
        """
        response = get(image_url)
        image = Image.open(BytesIO(response.content))

        image = image.convert("RGB")

        # noinspection PyTypeChecker
        image_np = array(image)

        encoding = face_recognition.face_encodings(image_np)[0]
        self.__known_face_encodings.append(encoding)
        self.__known_face_names.append(name)

    def __face_detection(self, frame) -> None:
        """
        Detect faces in the given frame and update the detection state.
        """
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.__known_face_encodings, face_encoding)
            self.__current_name = self.__DEFAULT_NAME

            if True in matches:
                first_match_index = matches.index(True)
                self.__current_name = self.__known_face_names[first_match_index]
                self.__detected_face = True
                self.__rectangle = ((left, top), (right, bottom))
                return

        self.__detected_face = False
        self.__rectangle = None
        self.__current_name = None

    def __edit_frame(self, frame) -> None:
        """
        Annotate the frame with detection results.
        """
        if self.__rectangle:
            cv2.rectangle(frame, self.__rectangle[0], self.__rectangle[1], (0, 0, 255), 2)
            cv2.putText(frame, self.__current_name, (self.__rectangle[0][0] + 6, self.__rectangle[1][1] - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        if self.__detected_face:
            cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    def run(self) -> None:
        """
        Main loop to capture video frames and process face detection.
        """
        while True:
            ret, frame = self.__video_capture.read()
            if not ret:
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if self.__counter % self.__detection_interval == 0:
                Thread(target=self.__face_detection, args=(frame,)).start()

            self.__edit_frame(frame)
            cv2.imshow('Video', frame)

            self.__counter += 1

        self.__cleanup()

    def __cleanup(self) -> None:
        """
        Release video resources and close all OpenCV windows.
        """
        self.__video_capture.release()
        cv2.destroyAllWindows()


def main() -> None:

    app = FaceRecognitionApp(detection_interval=DETECTION_INTERVAL)
    database_fetcher = DatabaseFetcher(db_url=DB_PATH, firebase_credentials_path=KEY)
    missing_people = list(database_fetcher.fetch_all_missing_people())
    for missing_person in missing_people:
        app.load_known_face_with_url(image_url=missing_person["image"], name=missing_person["name"])

    app.run()


if __name__ == "__main__":
    main()
