import argparse
import os

from SCEA.utils import data_utils, get_toolbox
from SCEA.run import execute_scea


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
        '-rpop',
        action='store',
        type=float,
        default=config['Algorithm']['REP_SIZE'],
        dest='REP_SIZE',
        help=f"Number of Representatives to preserve per generation. default {config['Algorithm']['REP_SIZE']}"
    )
    
    parser.add_argument(
        '-data',
        action='store',
        type=str,
        default=os.path.join(os.path.dirname(__file__), config['Path']['Data']),
        dest='dataPath',
        help=f"Path to the directory containing Data"
    )

    parser.add_argument(
        '-out',
        action='store',
        type=str,
        default=os.path.join(os.path.dirname(__file__), config['Path']['Output']),
        dest='outputPath',
        help=f"Path to the Output directory for logs, results and checkpoints"
    )
    return parser


filepath = os.path.join(os.path.dirname(__file__), 'config.yaml')
config = data_utils.get_config_object(path=filepath)
parser = get_parser(config=config)
args = parser.parse_args()

toolbox = get_toolbox(args=args)

def main():
    execute_scea(args=args, toolbox=toolbox)
