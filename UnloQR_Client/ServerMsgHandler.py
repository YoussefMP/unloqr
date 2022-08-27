import os
import time
from datetime import datetime
import cv2
try:
    import RPi.GPIO as GPIO
    __raspberry__ = True
    print(f"RPi correctly imported")
except ModuleNotFoundError:
    __raspberry__ = False
    print("problem while importing RPi")


c_man = None
client_obj = None


def set_c_man(config_manager):
    global c_man
    c_man = config_manager


def set_client(client):
    global client_obj
    client_obj = client


# ######################################################### #
# ############ Camera Variables and Methods ############### #
# ######################################################### #
STD_DIMS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080)
}

VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}


def set_res(cap, res):
    """
    Sets capture's resolution
    :param cap: the video captured
    :param res: the wished resolution
    :return:
    """
    width, height = STD_DIMS[res]
    cap.set(3, width)
    cap.set(4, height)
    return width, height


def get_video_type(filename):
    """
    Get video type according to the extension the file will be saved under
    :param filename:
    :return:
    """
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
        return VIDEO_TYPE[ext]
    return VIDEO_TYPE["avi"]


def record_video(file_path):
    """
    Records a video and saves it under the path filename
    :param file_path: path to save the video
    :return:
    """
    frames_per_second = 24.0
    res = "480p"

    cap = cv2.VideoCapture(0)
    dims = set_res(cap, res=res)
    video_type = get_video_type(file_path[file_path.rfind("/") + 1:])

    out = cv2.VideoWriter(file_path, video_type, frames_per_second, dims)

    cap_start = datetime.now()
    while True:
        ret, frame = cap.read()
        out.write(frame)
        try:
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()
            # cv2.imshow('frame', frame)
        except:
            break

        cap_end = datetime.now()
        if (cap_end - cap_start).seconds > 5:
            break

    cap.release()
    cv2.destroyAllWindows()


# ######################################################### #
# ############ Lock Variables and Methods ############### #
# ######################################################### #
def open_lock():
    """
    Opens the lock for seven seconds then close it back
    :return:
    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(13, GPIO.OUT)

    GPIO.output(13, 1)
    time.sleep(5)
    GPIO.output(13, 0)


# ######################################################### #
# ############ Main response handling methods ############# #
# ######################################################### #
def read_msg(response):
    print(response["message"])


def set_id(response):
    response = dict(response)
    new_id = response["idx"]
    c_man.initialize_config_file(new_id)


def grant_access(response):
    """
    Grants access to the user, by opening the lock after capturing a video of the request sender
    :param response:
    :return:
    """
    if response["ID"] == 10:
        print("GOT THE TEST EMIT")
        return
    
    print(f"response = {response}")
    uid = response["uid"]
    did = response["did"]
    date = response["date"]
    
    print(f"User Id requesting access is {uid}")
    
    if uid != -1:
        filename = f"{uid}_{did}_{date}.avi"
        filepath = f"./static/{filename}"

        # TODO Uncomment and test when camera is here
        record_video(filepath)

    else:
        time.sleep(1)

    if __raspberry__:
        open_lock()
    
    if uid != -1:
        client_obj.upload_file(filepath, filename)


# Dictionary containing the mapping of the response methods to the server msgs
response_ids = {
    "hello": read_msg,
    "set_ID": set_id,
    "access_granted": grant_access
}
