import threading

from . import detector
from . import server


def main():
    detector_thread = threading.Thread(target=detector.run_detector)
    detector_thread.start()

    server.run_server()


if __name__ == "__main__":
    main()
