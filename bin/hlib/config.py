from importlib.resources import files
import yaml


def load_config():
    config_file = files("hlib.resources").joinpath("config.yaml")
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    return config

