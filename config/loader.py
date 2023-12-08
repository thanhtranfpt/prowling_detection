import yaml
import os


path_to_config_file = os.path.join("config", "config.yaml")

# Reading config file:
with open(path_to_config_file, "r") as file:
    cfg = yaml.safe_load(file)

# Assign variables:
FLASK_HOSTNAME = cfg["FLASK_HOSTNAME"]
FLASK_PORT = cfg["FLASK_PORT"]