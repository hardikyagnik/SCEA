from typing import List, Tuple
from deap import tools, creator, base
import numpy as np
import itertools as it
import multiprocessing
multiprocessing.set_start_method('spawn', True)
import concurrent.futures
from operator import mul
import time, os
import logging

from SCEA.platform import Platform, Project


def get_duration_cost(schedule: List[int], project:Project):
    duration = project.duration
    tasks = project.tasks
    end_days = [duration[tid]+start for tid, start in zip(tasks, schedule)]
    p_duration = max(end_days) - min(schedule)
    return p_duration

def get_failure_ratio_cost(schedule: List[int], platform:Platform):
    failure_ratio = platform.failure_ratio
    _fr = 0
    for day in schedule:
        _fr += failure_ratio[day]
    return 100 * (_fr / len(schedule))

def get_similarity_cost(schedule_pair: List[List[int]], projects:List[Project], platform:Platform):
    similarity = platform.similarity
    tasks_list: List[List[int]] = [project.tasks for project in projects]
    reg_duration: dict = projects[0].reg_duration
    reg_end: List[int] = []
    for tid, start in zip(tasks_list[0], schedule_pair[0]): # calculate regEndDate for offspring
        reg_end.append(start + reg_duration[tid])

    offspring, *reps = schedule_pair # unpack schedules
    project, *rep_pros = projects # unpack projects
    tasks, *rep_tasks = tasks_list # unpack tasks

    simi_cost = []
    for idx, (start, end) in enumerate(zip(offspring, reg_end)):
        cost = []
        tid = tasks[idx]
        other = offspring[0:idx] + offspring[idx+1:]
        conflictingIDs = []
        for i, day in enumerate(other):
            if start <= day <= end:
                conflictingIDs.append((tasks[i], day) if i < idx else (tasks[i+1], day))
        for rep, rep_task in zip(reps, rep_tasks):
            for i, day in enumerate(rep):
                if start <= day <= end:
                    conflictingIDs.append((rep_task[i], day))
        for ctid, day in conflictingIDs:
            simi = similarity.loc[tid, ctid]
            if 0.6 <= simi <= 0.7:
                cost.append(simi)
        if cost:
            simi_cost.append(np.mean(cost))

    return np.mean(simi_cost)*100 if simi_cost else 0

def concurrent_eval(schedule:List[int], combinations:Tuple[int], project:Project, rep_pro:List[dict], platform:Platform):
    # print(logging.info(f"Starting concurrent evaluation: {os.getpid()}"))
    duration_cost = get_duration_cost(schedule, project)
    fr_cost = get_failure_ratio_cost(schedule, platform)
    simis = []
    for (idx, *ris) in combinations:
        schedule_pair =  [schedule]
        projects = [project]
        for pi, ri in enumerate(ris):
            projects.append(rep_pro[pi]['project'])
            schedule_pair.append(rep_pro[pi]['representatives'][ri])
        simi = get_similarity_cost(schedule_pair, projects, platform)
        simis.append(simi)
    simi_cost = np.mean(simis)

    schedule.fitness.values = duration_cost, fr_cost, simi_cost # set fitness values
    # print(logging.info(f"func:= concurrent_eval; msg:= Eval for ind={combinations[0][0]}, cost={schedule.fitness.values}"))

    return schedule

def evaluate(offsprings: dict, rep_pro: List[dict], platform:Platform):
    """
    Input parameters schema
    offsprings = {
        'children': List[List[int]],
        'project': Project
    }
    rep_pro = [
        {
            'reps': Optional[List[List[int]]],
            'project': Project
        }
    ]
    """
    # evaluate offspring pop here
    start = time.perf_counter()
    offspring_inds = offsprings['children']
    offspring_project = offsprings['project']
    rep_pro = [d for d in rep_pro if len(d['representatives'])]
    if rep_pro:
        combi_per_ind = list(it.accumulate([len(d['representatives']) for d in rep_pro], mul))[-1]
        indices = [list(range(len(offspring_inds)))] + [list(range(len(d['representatives']))) for d in rep_pro]
    else:
        combi_per_ind = 1
        indices = [list(range(len(offspring_inds)))] 

    combinations = list(it.product(*indices))
    N = len(offspring_inds)*combi_per_ind

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for idx in range(0, N, combi_per_ind):
            schedule = offspring_inds[combinations[idx][0]]
            combis = combinations[idx : idx+combi_per_ind]
            # print(f"func:= evaluate; msg:= Evaluating {combinations[idx][0]} with fitness={schedule.fitness.values}")
            ex = executor.submit(
                concurrent_eval,
                schedule=schedule,
                combinations=combis,
                project=offspring_project,
                rep_pro=rep_pro,
                platform=platform)
            result = ex.result()
            offspring_inds[combinations[idx][0]] = result
            # print(f"func:= evaluate; msg:= Done Eval {combinations[idx][0]}; fitness={result.fitness.values}")
    # executor.shutdown()

    end = time.perf_counter()
    # print(f"Completed evaluating {len(combinations)} combinations in {round(end-start,4)} seconds.")

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
    species = creator.Species(species)
    return species

def create_population(platform: Platform, toolbox: base.Toolbox):
    population = []
    for project in platform.projects:
        species = toolbox.createSpecies(project=project)
        population.append(species)
    return creator.Population(population)

def get_toolbox(args) -> base.Toolbox:
    toolbox = base.Toolbox()

    # Define Fitness 
    creator.create("MultiFitness", base.Fitness, weights=(-1,-1,-1))

    # Define individual class
    creator.create('Schedule', list, fitness=creator.MultiFitness)

    # Species Class for storing list of Schedules per Project per Generation
    # Stores Representatives which gets updated everytime specis gets updated
    creator.create('Species', list)

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

    toolbox.register("createPopulation", create_population, toolbox=toolbox)
    toolbox.register("evaluate", evaluate)

    toolbox.register("select", tools.selNSGA2)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes)

    return toolbox
