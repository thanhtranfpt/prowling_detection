import yaml
import os

# path_to_service = "business_service"
path_to_service = "."

# Reading config file:
path_to_config_file = os.path.join(path_to_service, "config", "config.yaml")
with open(path_to_config_file, "r") as file:
    cfg = yaml.safe_load(file)

# Assign variables:
CAMERAS = cfg["CAMERAS"]
NUM_THREADS = cfg["NUM_THREADS"]
REDIS_HOSTNAME, REDIS_PORT, STREAM_MAXLEN = cfg["REDIS_HOSTNAME"], cfg["REDIS_PORT"], cfg["STREAM_MAXLEN"]
TIME_TOO_LONG = cfg["TIME_TOO_LONG"]
TIME_BETWEEN_WARNING = cfg["TIME_BETWEEN_WARNING"]
# Choose cameras:
CAMERAS = CAMERAS if NUM_THREADS > len(CAMERAS) else CAMERAS[:NUM_THREADS]