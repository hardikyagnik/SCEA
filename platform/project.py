

class Project(object):

    def __init__(self, data: dict) -> None:
        self.task_dependency: dict = data['task_dependency']
        self.duration: dict = data['duration']
        self.reg_duration: dict = data['reg_duration']
        self.tasks: list = data['tasks']
        self.IND_SIZE = len(tasks)
    
    def is_valid_dependency(self, individual:list) -> bool:
        return True