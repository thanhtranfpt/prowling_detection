from flask import Flask, render_template, Response, redirect, request, jsonify
from flask_cors import CORS
import os
import yaml
import ast
from config.loader import FLASK_HOSTNAME, FLASK_PORT


app = Flask(__name__, template_folder='./templates')
CORS(app)


#----------------------- Initialize global variables: -----------------------
micro_services = ["camera_service",
                  "tracking_service",
                  "business_service",
                  "visualization_service"]
#----------------------- END OF Initialize global variables. -----------------------

#----------------------- Functions: -----------------------
def modify_yaml_file(file_path, key_to_modify, new_value):
    # Open the YAML file for reading
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Modify the data as needed
    data[key_to_modify] = new_value

    # Open the same YAML file for writing (this will overwrite the existing file)
    with open(file_path, 'w') as file:
        yaml.dump(data, file)
        #----- set allow_unicode=True if you want to use Vietnamese in the file.


def string_to_list(input_string):
    try:
        # Using ast.literal_eval to safely evaluate the input string
        result = ast.literal_eval(input_string)
        if isinstance(result, list):
            return result
        else:
            raise ValueError("Input is not a valid list.")
    except (SyntaxError, ValueError) as e:
        print(f"Error: {e}")
        return []
    
#----------------------- END OF Functions. -----------------------


@app.route('/')
def index():
    return redirect('/config')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/config')
def config():
    return render_template("config.html")

@app.route('/demo')
def view_demo():
    with open("visualization_service/config/config.yaml", "r") as file:
        data = yaml.safe_load(file)
    FLASK_HOSTNAME_visualization = data["FLASK_HOSTNAME"]
    FLASK_PORT_visualization = data["FLASK_PORT"]
    return redirect(f"http://{FLASK_HOSTNAME_visualization}:{FLASK_PORT_visualization}/")

# --------------------------- START OF add camera: ---------------------------
@app.route('/add-camera', methods = ['GET', 'POST'])
def add_camera():
    if request.method == 'GET':
        return render_template("add_camera.html")
    
    # method = POST:
    try:
        # Code that may raise an exception:
        data = request.get_json()
        print("Received data = ", data)
        camera_id = data['camera_id']
        camera_rtsp = data['camera_rtsp']

        if camera_id == '' or camera_rtsp == '':
            raise Exception("camera_id and camera_rtsp must NOT be null.")
        
        # Load current cameras information:
        file_path = os.path.join("camera_service", "config", "config.yaml")
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        CAMERAS = data["CAMERAS"]
        print("Current CAMERAS = ", CAMERAS)
        camera_ids = [camera_info['id'] for camera_info in CAMERAS]

        if camera_id in camera_ids:
            response = {
                "status_code": 0,
                "message": "Camera ID existed.",
                "camera_id": camera_id,
                "camera_rtsp": ""
            }
            return jsonify(response)
        
        # Add a new camera
        camera_info = {
            'id': camera_id,
            'rtsp': camera_rtsp
        }

        CAMERAS.append(camera_info)

        # Modify .yaml config files:
        files_to_modify = [os.path.join(service, "config", "config.yaml") for service in micro_services]
        for file in files_to_modify:
            modify_yaml_file(file_path=file, key_to_modify="CAMERAS", new_value=CAMERAS)

    except Exception as e:
        # Code to handle the exception:
        print("ERROR: ", e)
        response = {
            "status_code": 0,
            "message": "Camera added failed.",
            "camera_id": "",
            "camera_rtsp": ""
        }

    else:
        # Code to run if no exceptions are raised
        response = {
            "status_code": 1,
            "message": "Camera added successfully.",
            "camera_id": camera_id,
            "camera_rtsp": camera_rtsp
        }

    return jsonify(response)

# --------------------------- END OF add camera. ---------------------------

# --------------------------- START OF config camera: ---------------------------
@app.route('/config-camera', methods = ['GET', 'POST'])
def config_camera():
    if request.method == 'GET':
        return render_template("config_camera.html")
    # method = POST:
    try:
        # Code that may raise an exception:
        data = request.get_json()
        print("Received data = ", data)
        CAMERA_FPS = data["CAMERA_FPS"]
        NUM_FRAMES_SKIP = data["NUM_FRAMES_SKIP"]
        resized_height = data["resized_height"]
        resized_width = data["resized_width"]

        # Convert received data into expected data type before writing to .yaml file:
        CAMERA_FPS = int(CAMERA_FPS) if CAMERA_FPS != '' else None
        NUM_FRAMES_SKIP = int(NUM_FRAMES_SKIP) if NUM_FRAMES_SKIP != '' else None
        resized_height = int(resized_height) if resized_height != '' else None
        resized_width = int(resized_width) if resized_width != '' else None

        data_to_config = {
            "CAMERA_FPS": CAMERA_FPS,
            "NUM_FRAMES_SKIP": NUM_FRAMES_SKIP,
            "resized_height": resized_height,
            "resized_width": resized_width
        }

        # Modify .yaml config file:
        file_to_modify = os.path.join("camera_service", "config", "config.yaml")

        with open(file_to_modify, 'r') as file:
            data = yaml.safe_load(file)

        # Modify the data as needed
        for key_to_modify, new_value in data_to_config.items():
            if new_value is not None:
                data[key_to_modify] = new_value

        # Open the same YAML file for writing (this will overwrite the existing file)
        with open(file_to_modify, 'w') as file:
            yaml.dump(data, file)


    except Exception as e:
        print("ERROR: ", e)
        response = {
            "status_code": 0,
            "message": "Config camera failed."
        }
    else:
        response = {
            "status_code": 1,
            "message": "Config camera successfully."
        }

    return jsonify(response)

# --------------------------- END OF config camera. ---------------------------

# --------------------------- START OF config tracking: ---------------------------
@app.route('/config-tracking', methods = ['GET', 'POST'])
def config_tracking():
    if request.method == 'GET':
        return render_template("config_tracking.html")
    # method = POST:
    try:
        # Code that may raise an exception:
        data = request.get_json()
        print("Received data = ", data)
        YOLO_MODEL_PATH = data["YOLO_MODEL_PATH"]

        # Convert received data into expected data type before writing to .yaml file:
        YOLO_MODEL_PATH = YOLO_MODEL_PATH if YOLO_MODEL_PATH != '' else None

        data_to_config = {
            "YOLO_MODEL_PATH": YOLO_MODEL_PATH
        }

        # Modify .yaml config file:
        file_to_modify = os.path.join("tracking_service", "config", "config.yaml")

        with open(file_to_modify, 'r') as file:
            data = yaml.safe_load(file)

        # Modify the data as needed
        for key_to_modify, new_value in data_to_config.items():
            if new_value is not None:
                data[key_to_modify] = new_value

        # Open the same YAML file for writing (this will overwrite the existing file)
        with open(file_to_modify, 'w') as file:
            yaml.dump(data, file)


    except Exception as e:
        print("ERROR: ", e)
        response = {
            "status_code": 0,
            "message": "Config tracking failed."
        }
    else:
        response = {
            "status_code": 1,
            "message": "Config tracking successfully."
        }

    return jsonify(response)

# --------------------------- END OF config tracking. ---------------------------

# --------------------------- START OF config business: ---------------------------
@app.route('/config-business', methods = ['GET', 'POST'])
def config_business():
    if request.method == 'GET':
        return render_template("config_business.html")
    # method = POST:
    try:
        # Code that may raise an exception:
        data = request.get_json()
        print("Received data = ", data)
        TIME_TOO_LONG = data["TIME_TOO_LONG"]
        TIME_BETWEEN_WARNING = data["TIME_BETWEEN_WARNING"]

        # Convert received data into expected data type before writing to .yaml file:
        TIME_TOO_LONG = int(TIME_TOO_LONG) if TIME_TOO_LONG != '' else None
        TIME_BETWEEN_WARNING = int(TIME_BETWEEN_WARNING) if TIME_BETWEEN_WARNING != '' else None
        
        data_to_config = {
            "TIME_TOO_LONG": TIME_TOO_LONG,
            "TIME_BETWEEN_WARNING": TIME_BETWEEN_WARNING
        }

        # Modify .yaml config file:
        file_to_modify = os.path.join("business_service", "config", "config.yaml")

        with open(file_to_modify, 'r') as file:
            data = yaml.safe_load(file)

        # Modify the data as needed
        for key_to_modify, new_value in data_to_config.items():
            if new_value is not None:
                data[key_to_modify] = new_value

        # Open the same YAML file for writing (this will overwrite the existing file)
        with open(file_to_modify, 'w') as file:
            yaml.dump(data, file)


    except Exception as e:
        print("ERROR: ", e)
        response = {
            "status_code": 0,
            "message": "Configure business-related settings failed."
        }
    else:
        response = {
            "status_code": 1,
            "message": "Configure business-related settings successfully."
        }

    return jsonify(response)

# --------------------------- END OF config business. ---------------------------

# --------------------------- START OF config visualization: ---------------------------
@app.route('/config-visualization', methods = ['GET', 'POST'])
def config_visualization():
    if request.method == 'GET':
        return render_template("config_visualization.html")
    # method = POST:
    try:
        # Code that may raise an exception:
        data = request.get_json()
        print("Received data = ", data)
        FLASK_HOSTNAME = data["FLASK_HOSTNAME"]
        FLASK_PORT = data["FLASK_PORT"]
        demo_height = data["demo_height"]
        demo_width = data["demo_width"]

        # Convert received data into expected data type before writing to .yaml file:
        FLASK_HOSTNAME = FLASK_HOSTNAME if FLASK_HOSTNAME != '' else None
        FLASK_PORT = int(FLASK_PORT) if FLASK_PORT != '' else None
        demo_height = int(demo_height) if demo_height != '' else None
        demo_width = int(demo_width) if demo_width != '' else None
        
        data_to_config = {
            "FLASK_HOSTNAME": FLASK_HOSTNAME,
            "FLASK_PORT": FLASK_PORT,
            "demo_height": demo_height,
            "demo_width": demo_width
        }

        # Modify .yaml config file:
        file_to_modify = os.path.join("visualization_service", "config", "config.yaml")

        with open(file_to_modify, 'r') as file:
            data = yaml.safe_load(file)

        # Modify the data as needed
        for key_to_modify, new_value in data_to_config.items():
            if new_value is not None:
                data[key_to_modify] = new_value

        # Open the same YAML file for writing (this will overwrite the existing file)
        with open(file_to_modify, 'w') as file:
            yaml.dump(data, file)


    except Exception as e:
        print("ERROR: ", e)
        response = {
            "status_code": 0,
            "message": "Config visualization failed."
        }
    else:
        response = {
            "status_code": 1,
            "message": "Config visualization successfully."
        }

    return jsonify(response)

# --------------------------- END OF config visualization. ---------------------------

# --------------------------- START OF config env: ---------------------------
@app.route('/config-env', methods = ['GET', 'POST'])
def config_env():
    if request.method == 'GET':
        return render_template("config_env.html")
    # method = POST:
    try:
        # Code that may raise an exception:
        data = request.get_json()
        print("Received data = ", data)
        NUM_THREADS = data["NUM_THREADS"]
        env_selected = data["env_selected"]
        envs_list = data["envs_list"]

        # Convert received data into expected data type before writing to .yaml file:
        NUM_THREADS = int(NUM_THREADS) if NUM_THREADS != '' else None
        env_selected = int(env_selected) if env_selected != '' else None
        envs_list = string_to_list(envs_list) if envs_list != '' else None
        
        data_to_config = {
            "NUM_THREADS": NUM_THREADS,
            "env_selected": env_selected,
            "envs_list": envs_list
        }

        # Modify .yaml config files:
        files_to_modify = [os.path.join(service, "config", "config.yaml") for service in micro_services]

        for file_path in files_to_modify:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)

            for key_to_modify, new_value in data_to_config.items():
                if new_value is not None:
                    data[key_to_modify] = new_value
            
            with open(file_path, 'w') as file:
                yaml.dump(data, file)


    except Exception as e:
        print("ERROR: ", e)
        response = {
            "status_code": 0,
            "message": "Config running environment failed."
        }
    else:
        response = {
            "status_code": 1,
            "message": "Config running environment successfully."
        }

    return jsonify(response)

# --------------------------- END OF config env. ---------------------------

# --------------------------- START OF config redis: ---------------------------
@app.route('/config-redis', methods = ['GET', 'POST'])
def config_redis():
    if request.method == 'GET':
        return render_template("config_redis.html")
    # method = POST:
    try:
        # Code that may raise an exception:
        data = request.get_json()
        print("Received data = ", data)
        REDIS_HOSTNAME = data["REDIS_HOSTNAME"]
        REDIS_PORT = data["REDIS_PORT"]
        STREAM_MAXLEN = data["STREAM_MAXLEN"]

        # Convert received data into expected data type before writing to .yaml file:
        REDIS_HOSTNAME = REDIS_HOSTNAME if REDIS_HOSTNAME != '' else None
        REDIS_PORT = int(REDIS_PORT) if REDIS_PORT != '' else None
        STREAM_MAXLEN = int(STREAM_MAXLEN) if STREAM_MAXLEN != '' else None
        
        data_to_config = {
            "REDIS_HOSTNAME": REDIS_HOSTNAME,
            "REDIS_PORT": REDIS_PORT,
            "STREAM_MAXLEN": STREAM_MAXLEN
        }

        # Modify .yaml config files:
        files_to_modify = [os.path.join(service, "config", "config.yaml") for service in micro_services]

        for file_path in files_to_modify:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)

            for key_to_modify, new_value in data_to_config.items():
                if new_value is not None:
                    data[key_to_modify] = new_value
            
            with open(file_path, 'w') as file:
                yaml.dump(data, file)


    except Exception as e:
        print("ERROR: ", e)
        response = {
            "status_code": 0,
            "message": "Configure redis server failed."
        }
    else:
        response = {
            "status_code": 1,
            "message": "Configure redis server successfully."
        }

    return jsonify(response)

# --------------------------- END OF config redis. ---------------------------


if __name__ == '__main__':
    app.run(host = FLASK_HOSTNAME, port = FLASK_PORT, debug = True)