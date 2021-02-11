import yaml
import pandas as pd
import os 
import glob
import datetime
from collections import defaultdict


def get_config_object(path: str) -> dict:
    with open(path, 'r') as fileobject:
        try:
            config = yaml.safe_load(fileobject)
        except yaml.YAMLError as exc:
            print(exc)
    return config

def load_data_csv(path: str, obj_type: str):
    """
    path: Path to the data directory
    obj_type: type of data in {'project', 'similarity', 'failure}
    returns: list of pd.DataFrames of projects in that folder
    note: file should contain its obj_type in its name. 
    ex: 'project' for project files
    """ 
    old_wd: str = os.getcwd()
    try:
        os.chdir(path)
    except FileNotFoundError as e:
        raise(e)

    objects: list[pd.DataFrame] = []
    for f in glob.glob(f"*{obj_type}*.csv"):
        objects.append(pd.read_csv(os.path.join(path, f)))
        if obj_type == 'project':
            cols = ['registrationStartDate', 'submissionEndDate', 'registrationEndDate']
            objects[-1] = __change_to_datetime(objects[-1], cols)
        elif obj_type == 'failure':
            cols = ['registrationStartDate']
            objects[-1] = __change_to_datetime(objects[-1], cols)
    os.chdir(old_wd)
    return objects

def __change_to_datetime(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    for col in columns:
        df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
    return df

def get_fr_inrange(frdf: pd.DataFrame, sDate: pd.Timestamp, eDate: pd.Timestamp):
    mask = (frdf['registrationStartDate'] >= sDate) & (frdf['registrationStartDate'] <= eDate)
    result_fr = frdf[mask]
    result_fr.sort_values(by='registrationStartDate', inplace=True)
    result_fr.reset_index(drop=True, inplace=True)
    return result_fr['failureRatio'].tolist()

def calculate_duration(df: pd.DataFrame, filter: str) -> dict:
    """
    df: Pandas DataFrame object representing one project
    filter: {'registration', 'total'}
    """
    filter_map = {
        'registration': 'registrationEndDate',
        'total': 'submissionEndDate'
    }
    duration: dict = {}
    for cid, start, end in zip(df['challengeId'], df['registrationStartDate'], df[filter_map[filter]]):
        delta = end - start
        if delta.components[1] >= 8:
            duration[cid] = delta.components[0]+1
        else:
            duration[cid] = delta.components[0]+1
    return duration

def calculate_dependency(df: pd.DataFrame) -> defaultdict(set):
    """
    Example return object
    task_dependency = {
        30039490: set(),
        30039499: {30040825},
        30040825: set(),
        30040824: {30040989},
        30040989: {30041350},
        30041350: {30041793},
        30041793: set(),
        30041791: set(),
        30041792: set(),
        30041790: set(),
        30041840: set(),
        30041881: set(),
        30042071: set(),
        30042072: set(),
        30042735: {30043754},
        30043754: set(),
        30043781: set(),
        30043742: {30043749},
        30043749: {30044439},
        30044439: {30044578, 30044837},
        30044578: set(),
        30044683: set(),
        30044837: {30045328},
        30045328: {30048590},
        30048590: set()
    }
    Acc to this representation until the task denoting key is not completed 
    the tasks in values are cannot be started. Value is dependent on Key.
    """
    task_dependency = defaultdict(set)
    for parents, cid in zip(df['Sequential Tasks'].astype('str'), df['challengeId']):
        dependents: set = task_dependency[cid]
        parent_tids = None if parents=='nan' else parents.split(',')
        if parent_tids:
            parent_cids = df[df['Task Id'].isin(parent_tids)]['challengeId'].tolist()
            for p_cid in parent_cids:
                task_dependency[p_cid].add(cid)
    return task_dependency


def old_calculate_dependency(df: pd.DataFrame) -> dict:
    """
    Example return object:
    taskDependency = {
        30041243: [],
        30041425: [30041243],
        30041528: [30041425],
        30041622: [30041425],
        30041699: [30041622],
        30041698: [30041622],
        30041993: [30041698],
        30042606: [30041993],
        30042738: [30041993],
        30043694: [30042738]
    }
    This representation mean task denoting key cannot be started until
    the tasks in values are not completed. Key is dependent on value.
    """
    task_dependency = dict()
    for parents, cid in zip(df['Sequential Tasks'], df['challengeId']):
        parent_tids = None if parents=='nan' else parents.split(',')
        if parent_tids:
            parent_cids = df[df['Task Id'].isin(parent_tids)]['challengeId'].tolist()
            task_dependency[cid] = parent_cids
        else:
            task_dependency[cid] = []
    return task_dependency
