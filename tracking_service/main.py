import redis
import json
import cv2
from multiprocessing import Process
import numpy as np
from ultralytics import YOLO
from utils.redis import serialize_img
from utils.redis import get_last
from utils.tracking_helper import Tracker
from config.loader import cfg, CAMERAS, NUM_THREADS, REDIS_HOSTNAME, REDIS_PORT, STREAM_MAXLEN, YOLO_MODEL_PATH


#----------------------- Initialize global variables: -----------------------
global last_ids
last_ids = {}
for index, camera_info in enumerate(CAMERAS):
    camera_id = camera_info['id']
    last_ids[camera_id] = 0
#----------------------- END OF Initialize global variables. -----------------------

# Init Redis
conn = redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT)
if not conn.ping():
    raise Exception("Redis unavailable")
print("Connect Redis successfully")

def tracking(tracker, frame):
    current_people = tracker.track(frame=frame)
    tracking_results = {
        "current_people": current_people
    }
    return tracking_results

def run(camera_info):
    global last_ids

    camera_id = camera_info["id"]
    topic = f'camera:{camera_id}'

    tracker = Tracker(yolo_model_path=YOLO_MODEL_PATH)
    
    while True:
        last_ids[camera_id], frame, json_data = get_last(conn, topic, last_id=last_ids[camera_id])
        if frame is None:
            continue

        # json_data = {
        #     "frame_info": frame_info
        # }

        frame_info = json_data["frame_info"]

        tracking_results = tracking(tracker, frame)

        # Create msg to push to redis:
        
        json_data = {
            "frame_info": frame_info,
            "tracking_results": tracking_results
        }
        msg = {
            "frame": serialize_img(frame),
            "json_data": json.dumps(json_data)
        }

        # Push to redis

        conn.xadd(f'tracking_camera:{camera_id}', msg, maxlen=STREAM_MAXLEN)


if __name__ == '__main__':
    for index, camera_info in enumerate(CAMERAS):
        p = Process(target=run, args=(camera_info,))
        p.start()