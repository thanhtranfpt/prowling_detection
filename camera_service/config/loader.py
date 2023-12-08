import yaml
import os

# path_to_service = "camera_service"
path_to_service = "."

# Reading config file:
path_to_config_file = os.path.join(path_to_service, "config", "config.yaml")
with open(path_to_config_file, "r") as file:
    cfg = yaml.safe_load(file)

# Assign variables:
CAMERAS = cfg["CAMERAS"]
NUM_THREADS = cfg["NUM_THREADS"]
resized_height, resized_width = cfg["resized_height"], cfg["resized_width"]
REDIS_HOSTNAME, REDIS_PORT, STREAM_MAXLEN = cfg["REDIS_HOSTNAME"], cfg["REDIS_PORT"], cfg["STREAM_MAXLEN"]
# Choose cameras:
CAMERAS = CAMERAS if NUM_THREADS > len(CAMERAS) else CAMERAS[:NUM_THREADS]