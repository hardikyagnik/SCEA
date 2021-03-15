

class Project(object):

    def __init__(self, data: dict) -> None:
        self.task_forward_dependency: dict = data['task_forward_dependency']
        self.task_backward_dependency: dict = data['task_backward_dependency']
        self.tasks: list = data['tasks']
        self.duration: dict = data['duration']
        self.reg_duration: dict = data['reg_duration']
        self.s_date = data['s_date']
        self.e_date = data['e_date']
        self.max_days = data['max_days']

        self.IND_SIZE = len(self.tasks)
        self.task_idx_map: dict = {task: idx for idx, task in enumerate(self.tasks)}
        self.original_schedule: list = self.__create_original_schedule()

    def is_valid_dependency(self, schedule:list) -> bool:
        for tid, idx in self.task_idx_map.items():
            children = self.task_forward_dependency[tid]
            if not children:
                continue
            edate = schedule[idx] + self.duration[tid]
            for cid in children:
                if schedule[self.task_idx_map[cid]] <= edate:
                    # print(f'Failed for tid: {tid} and cid: {cid}')
                    return False
        return True

    def __create_original_schedule(self):
        original_schedule_map = {}
        def get_date(tid):
            if tid in original_schedule_map:
                return original_schedule_map[tid]
            if not self.task_backward_dependency[tid]:
                original_schedule_map[tid] = 0
                return original_schedule_map[tid]
            else:
                parents = self.task_backward_dependency[tid]
                day = max([(get_date(pid)+self.duration[pid]) for pid in parents]) + 1
                original_schedule_map[tid] = day
                return original_schedule_map[tid]

        os = [get_date(tid) for tid in self.tasks]
        return os
