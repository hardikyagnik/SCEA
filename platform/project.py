

class Project(object):

    def __init__(self, data: dict) -> None:
        self.task_dependency: dict = data['task_dependency']
        self.duration: dict = data['duration']
        self.failure_ratio: list = date['failure_ratio']
        self.reg_duration: dict = data['reg_duration']
        self.tasks: list = data['tasks']
        self.s_date = data['s_date']
        self.e_date = data['e_date']
        self.IND_SIZE = len(self.tasks)
    
    def is_valid_dependency(self, individual:list) -> bool:
        return True