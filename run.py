from SCEA.platform import *
from SCEA.algorithm import *
from SCEA.utils import load_data_csv, get_toolbox

import time
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

    # Create Platform object
    platform: Platform = Platform(data)

    # Generate DEAP Toolbox object using Platform object
    toolbox = get_toolbox(platform, args)

    # Initialise Population
    start = time.perf_counter()
    population = toolbox.createPopulation()
    end = time.perf_counter()
    print(f"Finished population generation of {args.SPECIES_SIZE*len(platform.projects)} individuals in {round(end-start,2)} seconds!")

    # Initial population evaluation
    # Representatives
    rep_pros = [
    {
        'representatives': species.representatives,
        'project': project
        } for species, project in zip(population, platform.projects)
    ]

    for idx, species in enumerate(population):
        _rep_pros = rep_pros[0:idx] + rep_pros[idx+1:]
        offsprings = {
            'children': species, # Initially all individuals have None fitness 
            'project': platform.projects[idx]
            }
        
        toolbox.evaluate(offsprings, _rep_pros)
        # Perform Non-Dominated sorting then Crowd-Distance sorting 
        # and update representatives and population.
        # Select best REP_SIZE individuals
        toolbox.select(species, k=len(species))
        species.representatives = toolbox.select(species, k=args.REP_SIZE)
        # Update rep_pros list
        rep_pros[idx]['representatives'] = species.representatives

    # Call CEA
    population = cea(population, platform, args, toolbox)