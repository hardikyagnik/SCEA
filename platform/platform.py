from SCEA.platform.project import *
from SCEA.utils import calculate_dependency, calculate_duration

import pandas as pd


class Platform(object):

    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.projects: list(Project) = []

        # Create Project object for each project df
        self.__fill_projects_list(data['projects'])
    
    def __fill_projects_list(projects: pd.DataFrame):
        for pdf in projects:
            task_dependency: dict = calculate_dependency(pdf)
            tasks: list = list(task_dependency.keys())
            duration: dict = calculate_duration(pdf, 'total')
            reg_duration: dict = calculate_duration(pdf, 'registration')
            data = {
                'task_dependency': task_dependency,
                'duration': duration,
                'reg_duration': reg_duration,
                'tasks': tasks
            }
            self.projects.append(Project(data))


