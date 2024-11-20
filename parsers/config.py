import yaml
from easydict import EasyDict as edict


def get_config(config, seed, scaler1, scaler2):
    config_dir = f'./config/{config}.yaml'
    config = edict(yaml.load(open(config_dir, 'r'), Loader=yaml.FullLoader))
    config.seed = seed
    config.scaler1=scaler1
    config.scaler2=scaler2
    return config