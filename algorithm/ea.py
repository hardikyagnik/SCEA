from deap import tools
from deap import algorithms
import random

from SCEA.platform import Project


def cea(population, platform, args, toolbox):
    # Enable Multi processing

    # Representatives
    rep_pros = [
    {
        'representatives': species.representatives,
        'project': project
        } for species, project in zip(population, platform.projects)
    ]

    # Projects obj array
    projects = platform.projects

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
            _rep_pros = rep_pros[0:idx] + rep_pros[idx+1:]
            offsprings = {
                'children': offspring_ind,
                'project': projects[idx]
                }
            toolbox.evaluate(offsprings, _rep_pros)

            # Select best performing individuals for next generation
            # Select top SPECIES_SIZE from it as new species
            # Select top REP_SIZE from it as new representatives
            species = toolbox.select(species + offspring_ind, k=args.SPECIES_SIZE)
            species.representatives = toolbox.select(species + offspring_ind, k=args.REP_SIZE)
            
            # Update rep_pros list
            rep_pros[idx]['representatives'] = species.representatives
    print(0)
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
