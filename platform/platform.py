from SCEA.platform.project import *
from SCEA.utils import calculate_dependency, calculate_duration, get_fr_inrange

import pandas as pd


class Platform(object):

    def __init__(self, data: dict) -> None:
        self.projects: list(Project) = []
        self.similarity: pd.DataFrame = None
        self.failure_ratio_df = data['failure_ratio']

        # Create Project object for each project df
        self.__fill_projects_list(data['projects'])
        
        # Fill Task Similarity for all tasks on platform
        self.__fill_similarity(data['similarity'])

    def __fill_projects_list(self, projects: pd.DataFrame):
        for pdf in projects:
            task_dependency: dict = calculate_dependency(pdf)
            tasks: list = list(task_dependency.keys())
            duration: dict = calculate_duration(pdf, 'total')
            reg_duration: dict = calculate_duration(pdf, 'registration')
            s_date = min(pdf["registrationStartDate"])
            e_date = max(pdf["submissionEndDate"])
            failure_ratio: list = get_fr_inrange(self.failure_ratio_df, s_date, e_date)

            delta = e_date-s_date
            max_days: int = delta.components[0] + round(delta.components[1]/10 - 0.2)
            
            data = {
                'task_dependency': task_dependency,
                'duration': duration,
                'reg_duration': reg_duration,
                'failure_ratio': failure_ratio,
                'tasks': tasks,
                's_date': s_date,
                'e_date': e_date,
                'max_days': max_days
            }
            self.projects.append(Project(data))

    def __fill_similarity(self, similarity: pd.DataFrame):
        all_tasks: list = sum([p.tasks for p in self.projects], [])
        self.similarity = similarity.loc[all_tasks,all_tasks]
