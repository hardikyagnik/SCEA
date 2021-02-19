from SCEA.platform.project import *
from SCEA.utils import (
    calculate_forward_dependency, calculate_backward_dependency,
    calculate_duration, get_fr_inrange
    )

import pandas as pd


class Platform(object):

    def __init__(self, data: dict) -> None:
        self.projects: list(Project) = []
        self.similarity: pd.DataFrame = None
        self.failure_ratio: list = None
        self.s_date = None
        self.e_date = None
        self.max_days = None
        
        # Fill Failure ratio list along with s_date and e_date
        self.__fill_failure_ratio(data['failure_ratio'], data['projects'])

        # Create Project object for each project df
        self.__fill_projects_list(data['projects'])

        # Fill Task Similarity for all tasks on platform
        self.__fill_similarity(data['similarity'])

    def __fill_projects_list(self, projects: pd.DataFrame):
        for pdf in projects:
            task_forward_dependency: dict = calculate_forward_dependency(pdf)
            task_backward_dependency: dict = calculate_backward_dependency(pdf)
            tasks: list = list(task_forward_dependency.keys())
            duration: dict = calculate_duration(pdf, 'total')
            reg_duration: dict = calculate_duration(pdf, 'registration')

            delta = self.e_date - self.s_date
            self.max_days: int = delta.components[0] + round(delta.components[1]/10 - 0.2)

            data = {
                'task_forward_dependency': task_forward_dependency,
                'task_backward_dependency': task_backward_dependency,
                'tasks': tasks,
                'duration': duration,
                'reg_duration': reg_duration,
                's_date': self.s_date,
                'e_date': self.e_date,
                'max_days': self.max_days
            }
            self.projects.append(Project(data))

    def __fill_similarity(self, similarity: pd.DataFrame):
        all_tasks: list = sum([p.tasks for p in self.projects], [])
        self.similarity = similarity.loc[all_tasks,all_tasks]

    def __fill_failure_ratio(self, frdf: pd.DataFrame, projects: pd.DataFrame):
        """
        With this method we define a range of days in which we want our algorithm to
        search for the scheduling parameters (assign start days to each task).
        If we have multiple projects then this will consider 0th day as minimum 
        registrationStartDate of all those projects and nth day (maximum allowd day)
        as maxmimum submissionEndDate of all those projects.
        """
        self.s_date = min([min(pdf['registrationStartDate']) for pdf in projects])
        self.e_date = max([max(pdf['submissionEndDate']) for pdf in projects])
        self.failure_ratio = get_fr_inrange(frdf, self.s_date, self.e_date)
