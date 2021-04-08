from deap import tools
from deap import algorithms
import random
import os, time
import joblib, pickle

from SCEA.platform import Project


def cea(population, platform, args, toolbox, stats=None, verbose=__debug__):

    # Make Output dir(s)
    log_dir = os.path.join(args.outputPath, 'Log')
    op_data_dir = os.path.join(args.outputPath, 'Data')
    cp_dir = os.path.join(args.outputPath, 'Checkpoints')
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(op_data_dir, exist_ok=True)
    os.makedirs(cp_dir, exist_ok=True)
    log_eval_path = os.path.join(log_dir, 'log_eval.txt')

    # Save Platform data
    with open(os.path.join(op_data_dir, 'platform.pickle'), 'wb') as f:
        pickle.dump(platform, f)

    # Projects obj array
    projects = platform.projects

    # Initialise Logbook
    logbook = tools.Logbook()
    logbook.header = ["gen", "species", "nevals"] + (list(stats.keys()) if stats else [])
    for key in stats.keys():
        logbook.chapters[key].header = (stats[key].fields)

    # Representatives
    rep_pros = [
    {   
        'hof': tools.ParetoFront(),
        'representatives': [],
        'project': project
        } for species, project in zip(population, projects)
    ]

    # Initial population evaluation
    for idx, species in enumerate(population):
        _rep_pros = rep_pros[0:idx] + rep_pros[idx+1:]
        offsprings = {
            'children': species, # Initially all individuals have None fitness 
            'project': projects[idx]
            }

        toolbox.evaluate(offsprings, _rep_pros, platform=platform)
        # Perform Non-Dominated sorting then Crowd-Distance sorting 
        # and update representatives and population.
        species = toolbox.select(species, k=args.SPECIES_SIZE)

        # Select top REP_SIZE from it as new representatives
        rep_pros[idx]['representatives'] = toolbox.select(species, k=args.REP_SIZE)

        # Maintain Elite individuals
        rep_pros[idx]['hof'].update(species) 

        # Logging
        record = stats.compile(species) if stats else {}
        logbook.record(gen=0, species=idx+1, nevals=len(species), **record)
        log_stream = logbook.stream
        if verbose:
            print(log_stream)
        with open(log_eval_path, 'a') as log_file:
            log_file.write(f"{log_stream}\n")

    for gen in range(args.GEN_SIZE):
        for idx, species in enumerate(population):

            # Select parent chromosomes using tournament selection based on CD
            offspring = tools.selTournamentDCD(species, len(species))

            # Var And Operation with hard constraint
            offspring = varAndWithHardConstraint(
                species,
                projects[idx],
                toolbox=toolbox,
                cxpb=args.CX_PB,
                mutpb=args.MU_PB)

            # Evaluate children
            offspring_ind = [ind for ind in offspring if not ind.fitness.valid]
            nevals = len(offspring_ind)
            # print(sum([i==s for i,s in zip(offspring_ind, species)]))
            _rep_pros = rep_pros[0:idx] + rep_pros[idx+1:]
            offsprings = {
                'children': offspring_ind,
                'project': projects[idx]
                }
            # print(f"GEN={gen} SPECIES={idx} CHILD_COUNT={len(offspring_ind)}")
            toolbox.evaluate(offsprings, _rep_pros, platform=platform)

            # Update Elite Individuals
            offspring_ind.extend(rep_pros[idx]['hof'].items)
            rep_pros[idx]['hof'].update(offspring_ind)

            # Select best performing individuals for next generation
            # Select top SPECIES_SIZE from it as new species
            species = toolbox.select(species + offspring_ind, k=args.SPECIES_SIZE)

            # Select top REP_SIZE from it as new representatives
            rep_pros[idx]['representatives'] = toolbox.select(species + offspring_ind, k=args.REP_SIZE)

            # Set new species
            population[idx] = species

            # Logging
            record = stats.compile(species) if stats else {}
            logbook.record(gen=gen+1, species=idx+1, nevals=nevals, **record)
            log_stream = logbook.stream
            if verbose:
                print(log_stream)
            with open(log_eval_path, 'a') as log_file:
                log_file.write(f"{log_stream}\n")

        if gen % 5 == 0:
            cp = dict(
                generation = gen,
                representatives = [rep['representatives'] for rep in rep_pros],
                population = population
            )
            with open(os.path.join(cp_dir, f'checkpoint_{gen}.pickle'), 'wb') as f:
                pickle.dump(cp, f)
    cp = dict(
        generation = gen,
        representatives = [rep['representatives'] for rep in rep_pros],
        population = population
    )
    with open(os.path.join(cp_dir, f'checkpoint_{gen}.pickle'), 'wb') as f:
        pickle.dump(cp, f)

    return population

def varAndWithHardConstraint(species, project: Project, toolbox, cxpb, mutpb):
    offspring = [toolbox.clone(ind) for ind in species]

    # Apply crossover and mutation on the offspring
    for i in range(1, len(offspring), 2):
        if random.random() < cxpb:
            c1 = toolbox.clone(offspring[i-1])
            c2 = toolbox.clone(offspring[i])
            c1, c2 = toolbox.mate(c1, c2)
            if project.is_valid_dependency(c1):
                offspring[i - 1] = c1
                del offspring[i - 1].fitness.values
            if project.is_valid_dependency(c2):
                offspring[i] = c2
                del offspring[i].fitness.values

    for i in range(len(offspring)):
        if random.random() < mutpb:
            c = toolbox.clone(offspring[i])
            c, = toolbox.mutate(c, indpb=1.0/project.IND_SIZE)
            if project.is_valid_dependency(c):
                offspring[i] = c
                del offspring[i].fitness.values

    return offspring
