import yaml

def get_config_object(path: str) -> dict:
    with open(path, 'r') as fileobject:
        try:
            config = yaml.safe_load(fileobject)
        except yaml.YAMLError as exc:
            print(exc)
    return config

