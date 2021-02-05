from SCEA.platform import *
from SCEA.algorithm import *
from SCEA.utils import load_data_csv, calculate_dependency

import pandas as pd


def __load_data(dataPath: str) -> dict:
    projects: list[pd.DataFrame] = load_data_csv(dataPath, 'project')
    similarity: pd.DataFrame = load_data_csv(dataPath, 'similarity')[0]
    failure_ratio: pd.DataFrame = load_data_csv(dataPath, 'failure')[0]

    data = {
        'projects': projects,
        'similarity': similarity,
        'failure_ratio': failure_ratio,
    }
    return data
    
def execute_scea(args):
    # Load Data
    data: dict = __load_data(args.dataPath)

    platform: Platform = Platform(data)
