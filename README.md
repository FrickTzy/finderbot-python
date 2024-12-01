# FinderBot Python

FinderBot is a Python-based face recognition iot device designed to help locate missing persons by recognizing known faces. The bot uses computer vision and deep learning techniques to detect faces in real-time video feeds. It's integrated with a database to fetch missing person's data and their associated images.

## Features

- **Face Recognition:** Detects and matches faces in real-time using the `face_recognition` library.
- **Database Integration:** Fetches missing person data (name and image URL) from a Firebase database.
- **Video Processing:** Captures video frames and processes them for face detection.

## Installation

```bash
git clone https://github.com/yourusername/finderbot-python.git
cd finderbot-python
