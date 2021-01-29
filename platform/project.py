
class Project(object):

    def __init__(self, data: dict) -> None:
        self.dependency_dict: dict = data['dependency']
        self.duration: list = data['duration']
        self.tasks: list = data['tasks']
        self.IND_SIZE = len(tasks)
    
    def is_valid_dependency(self, individual:list) -> bool:
        return True