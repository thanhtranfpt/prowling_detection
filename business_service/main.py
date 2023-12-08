import redis
import json
from multiprocessing import Process
import numpy as np
import time
import math
import cv2
from utils.redis import serialize_img
from utils.redis import get_last
from utils.business_helper import check_prowling, get_warning_list, LimitedDict
from config.loader import cfg, CAMERAS, NUM_THREADS, REDIS_HOSTNAME, REDIS_PORT, STREAM_MAXLEN, \
    TIME_TOO_LONG, TIME_BETWEEN_WARNING


#----------------------- Initialize global variables: -----------------------
global last_ids
last_ids = {}
for index, camera_info in enumerate(CAMERAS):
    camera_id = camera_info['id']
    last_ids[camera_id] = 0

global prev_warning_time
prev_warning_time = {}
for index, camera_info in enumerate(CAMERAS):
    camera_id = camera_info['id']
    prev_warning_time[camera_id] = time.time()

global person_start_time, person_last_warning_time
person_start_time, person_last_warning_time = {}, {}
for camera_info in CAMERAS:
    camera_id = camera_info['id']
    person_start_time[camera_id] = LimitedDict(max_size=1000)
    person_last_warning_time[camera_id] = LimitedDict(max_size=1000)
#----------------------- END OF Initialize global variables -----------------------

# Init Redis
conn = redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT)
if not conn.ping():
    raise Exception("Redis unavailable")
print("Connect Redis successfully")

def business(tracking_results, camera_id):
    # tracking_results = {
    #     "current_people": current_people
    # }

    global prev_warning_time, person_start_time, person_last_warning_time

    current_people = tracking_results["current_people"]
    
    current_person_ids = list(current_people.keys())
    prowling_list, person_start_time[camera_id] = check_prowling(current_person_ids, person_start_time[camera_id], TIME_TOO_LONG)
    warning_list, person_last_warning_time[camera_id] = get_warning_list(prowling_list, person_last_warning_time[camera_id], TIME_BETWEEN_WARNING)
    warning = False
    if warning_list and (time.time() - prev_warning_time[camera_id]) > TIME_BETWEEN_WARNING:
        warning = True
        prev_warning_time[camera_id] = time.time()

    business_results = {
        "prowling_list": prowling_list,
        "warning_list": warning_list,
        "warning": warning,
        "current_people": current_people
    }

    return business_results

def run(camera_info):
    global last_ids

    camera_id = camera_info["id"]
    topic = f'tracking_camera:{camera_id}'

    while True:
        last_ids[camera_id], frame, json_data = get_last(conn, topic, last_id=last_ids[camera_id])
        if frame is None:
            continue

        # json_data = {
        #     "frame_info": frame_info,
        #     "tracking_results": tracking_results
        # }

        frame_info, tracking_results = json_data["frame_info"], json_data["tracking_results"]

        business_results = business(tracking_results, camera_id)

        # Create msg to push to redis:

        json_data = {
            "frame_info": frame_info,
            "business_results": business_results
        }

        msg = {
            "frame": serialize_img(frame),
            "json_data": json.dumps(json_data)
        }

        # Push to redis:

        conn.xadd(f'business_camera:{camera_id}', msg, maxlen=STREAM_MAXLEN)

        
if __name__ == '__main__':
    for index, camera_info in enumerate(CAMERAS):
        p = Process(target=run, args=(camera_info,))
        p.start()