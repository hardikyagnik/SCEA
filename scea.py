import argparse
import os

from .utils import data_utils
from .run import execute_scea

def get_parser(config: dict):
    parser = argparse.ArgumentParser(
        prog='SCEA',
        description='refer README.md',
        usage='python -m SCEA [options]',
        allow_abbrev=False,
    )

    parser.add_argument(
        '-cxpb',
        action='store',
        type=float,
        default=config['Algorithm']['CX_PB'],
        dest='CX_PB',
        help=f"Crossover Probability. default {config['Algorithm']['CX_PB']}"
    )

    parser.add_argument(
        '-mupb',
        action='store',
        type=float,
        default=config['Algorithm']['MU_PB'],
        dest='MU_PB',
        help=f"Mutation Probability. default {config['Algorithm']['MU_PB']}"
    )

    parser.add_argument(
        '-spop',
        action='store',
        type=float,
        default=config['Algorithm']['SPECIES_SIZE'],
        dest='SPECIES_SIZE',
        help=f"Population per Species. default {config['Algorithm']['SPECIES_SIZE']}"
    )

    parser.add_argument(
        '-ngen',
        action='store',
        type=float,
        default=config['Algorithm']['GEN_SIZE'],
        dest='GEN_SIZE',
        help=f"Number of generations. default {config['Algorithm']['GEN_SIZE']}"
    )

    parser.add_argument(
        '-hpop',
        action='store',
        type=float,
        default=config['Algorithm']['HOF_SIZE'],
        dest='HOF_SIZE',
        help=f"Number of Elite to preserve per generation. default {config['Algorithm']['HOF_SIZE']}"
    )
    
    return parser

def main():
    filepath = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config = data_utils.get_config_object(path=filepath)
    parser = get_parser(config=config)
    args = parser.parse_args()
    
    execute_scea(args)

if __name__ == '__main__':
    main()
