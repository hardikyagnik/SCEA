from deap import tools, creator, base
from typing import List
import numpy as np

from SCEA.platform import Platform, Project

def get_cost(schedule_pair: List[List[int]], platform: Platform):
    pass

def create_schedule(project: Project, toolbox: base.Toolbox):
    nVars = project.IND_SIZE
    schedule = [None]*nVars
    original_schedule = project.original_schedule
    task_forward_dependency = project.task_forward_dependency
    duration = project.duration
    max_days = project.max_days
    id_map = project.task_idx_map

    def get_day(tid):
        if schedule[id_map[tid]] is not None:
            return schedule[id_map[tid]]
        if not task_forward_dependency[tid]:
            minD = original_schedule[id_map[tid]]
            day = toolbox.getRandInt(low=minD, high=max_days).item()
            schedule[id_map[tid]] = day
            return schedule[id_map[tid]]
        else:
            children = task_forward_dependency[tid]
            minD = original_schedule[id_map[tid]]
            maxD = min([get_day(cid) for cid in children]) - duration[tid]
            day = toolbox.getRandInt(low=minD, high=maxD).item()
            schedule[id_map[tid]] = day
            return schedule[id_map[tid]]

    for task_id in project.tasks:
        get_day(task_id)

    assert project.is_valid_dependency(schedule) == True

    return creator.Schedule(schedule)

def create_species(project: Project, toolbox: base.Toolbox, size: int):
    # Should I use multi processing here ?? 
    # Should I score indivuals here and generate initial representatives ??
    species = []
    for ind in range(size):
        schedule = toolbox.createSchedule(project)
        species.append(schedule)
    return creator.Species(species, representatives=creator.Representatives([]))

def create_population(platform: Platform, toolbox: base.Toolbox):
    population = []
    for project in platform.projects:
        species = toolbox.createSpecies(project=project)
        population.append(species)
    return creator.Population(population)

def get_toolbox(platform: Platform, args) -> base.Toolbox:
    toolbox = base.Toolbox()

    # Define Fitness 
    creator.create("MultiFitness", base.Fitness, weights=(-1,-1,-1))

    # Define individual class
    creator.create('Schedule', list, fitness=creator.MultiFitness)

    # Class for storing representatives per species.
    # A list best schedules per generation
    creator.create("Representatives", list)

    # Species Class for storing list of Schedules per Project per Generation
    # Stores Representatives which gets updated everytime specis gets updated
    creator.create('Species', list, representatives=creator.Representatives)

    # Class for storing list of species
    creator.create('Population', list)

    toolbox.register("getRandInt", np.random.randint, size=1)

    toolbox.register("createSchedule", create_schedule, toolbox=toolbox)

    toolbox.register(
        "createSpecies",
        create_species,
        toolbox=toolbox,
        size=args.SPECIES_SIZE
    )

    toolbox.register("createPopulation", create_population, platform=platform, toolbox=toolbox)

    return toolbox
