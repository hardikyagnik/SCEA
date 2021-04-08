from SCEA.platform import *
from SCEA.algorithm import *
from SCEA.utils import load_data_csv, get_toolbox

import pandas as pd
import numpy as np
from deap import tools
import functools
import time


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

def execute_scea(args, toolbox):
    # Load Data
    data: dict = __load_data(args.dataPath)

    # Create Platform object
    platform: Platform = Platform(data)

    # Generate DEAP Toolbox object using Platform object
    # toolbox = get_toolbox(platform, args)

    # Initialise Population
    start = time.perf_counter()
    population = toolbox.createPopulation(platform=platform)
    end = time.perf_counter()
    print(f"Finished population generation of {args.SPECIES_SIZE*len(platform.projects)} individuals in {round(end-start,2)} seconds!")

    # Statistics
    myMin = round_decorator(np.min)
    myMean = round_decorator(np.mean)
    myStd = round_decorator(np.std)

    duration_stat = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    filure_stat = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    similarity_stat = tools.Statistics(key=lambda ind: ind.fitness.values[2])
    stats = tools.MultiStatistics(duration=duration_stat, failure=filure_stat, similarity=similarity_stat)
    stats.register("avg", myMean)
    stats.register("std", myStd)
    stats.register("min", myMin)

    # Call CEA
    population = cea(population, platform, args, toolbox, stats=stats, verbose=True)

def round_decorator(func, k=2):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        return round(value,k)
    return wrapper