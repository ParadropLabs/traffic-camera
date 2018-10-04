import json
import os
import time

import cv2
import requests


INSTALL_DIR = os.path.abspath(os.path.dirname(__file__))


# Should we save captured frames? If SAVE_FRAMES_DIR is not None, we will save
# all caputured frames to that directory. This should only be enabled for
# testing or training purposes because it will accumulate a lot of images.
SAVE_FRAMES_DIR = os.environ.get("SAVE_FRAMES_DIR", None)

# URL which provides video frames. Default to localhost assuming
# paradrop-imserve is installed as a virtual camera.
IMAGE_SOURCE_URL = os.environ.get("IMAGE_SOURCE_URL", "http://localhost:7466/park/video.jpg")

# File to load with cascade parameters.
CASCADE_FILE = os.environ.get("CASCADE_FILE", "vehicle.xml")
CASCADE_FILE = os.path.join(INSTALL_DIR, CASCADE_FILE)

# The optional mask file is used to ignore detections in certain regions of
# the frame. It should be a grayscale image with valid regions in white.
MASK_FILE = os.environ.get("MASK_FILE", None)

# Maximum length of history to keep (e.g. one hour of counts).
MAX_HISTORY_LENGTH = int(os.environ.get("MAX_HISTORY_LENGTH", 3600))

PARADROP_DATA_DIR = os.environ.get("PARADROP_DATA_DIR", "/tmp")


try:
    mask = cv2.imread(os.path.join(INSTALL_DIR, MASK_FILE))
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
except:
    mask = None


def check_mask(x, y, w, h):
    """
    Check if the object is in a valid region according to the mask.

    This implementation checks the center pixel of the bounding box.

    Returns True if valid or False otherwise.
    """
    i = int(y + h/2)
    j = int(x + w/2)
    return mask[i, j] > 128


def remove_masked(detections):
    """
    Remove detection results that are excluded by the mask.
    """
    result = []

    if mask is None:
        return detections

    for x, y, w, h in detections:
        if check_mask(x, y, w, h):
            result.append((x, y, w, h))

    return result


def remove_overlaps(detections):
    """
    Remove detection results that are fully enclosed (redundant).
    """
    keep = set(range(len(detections)))

    for i in range(len(detections)):
        x1, y1, w1, h1 = detections[i]

        for j in range(i+1, len(detections)):
            x2, y2, w2, h2 = detections[j]

            if j in keep and \
                    x2 >= x1 and y2 >= y1 and \
                    x2 + w2 <= x1 + w1 and y2 + h2 <= y1 + h1:
                keep.remove(j)
            elif i in keep and \
                    x1 >= x2 and y1 >= y2 and \
                    x1 + w1 <= x2 + w2 and y1 + h1 <= y2 + h2:
                keep.remove(i)

    return [detections[i] for i in keep]


def run_detector():
    counts = []

    cascade = cv2.CascadeClassifier(CASCADE_FILE)

    # Use a session to preserve cookies across requests.
    session = requests.Session()

    while True:
        timestamp = int(time.time())

        # Download the next frame.
        response = session.get(IMAGE_SOURCE_URL)

        path = os.path.join(PARADROP_DATA_DIR, "frame.jpg")
        with open(path, "wb") as output:
            output.write(response.content)

        img = cv2.imread(path)

        # Convert to grayscale for detection.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Run the detector.
        detections = cascade.detectMultiScale(gray, 1.1, 1)

        # Filter out masked and overlapping objects.
        detections = remove_masked(detections)
        detections = remove_overlaps(detections)

        # Annotate image with bounding boxes.
        for (x,y,w,h) in detections:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,0,255), 2)

        # Save the marked image.
        path = os.path.join(PARADROP_DATA_DIR, "marked.jpg")
        cv2.imwrite(path, img)

        # Append the detection count and maintain maximum length.
        counts.append({
            "time": timestamp,
            "count": len(detections)
        })
        counts = counts[-MAX_HISTORY_LENGTH:]

        path = os.path.join(PARADROP_DATA_DIR, "counts.json")
        with open(path, "w") as output:
            output.write(json.dumps(counts))

        time.sleep(1)
