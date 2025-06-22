from datetime import datetime, timedelta

class Job:
    def __init__(self):
        self.next_run = datetime.now() + timedelta(days=1)
        self.job_func = lambda: None
    def at(self, time_str):
        return self
    def do(self, func):
        self.job_func = func
        jobs.append(self)
        return self

jobs = []

def every():
    return Job()

def run_pending():
    for job in list(jobs):
        pass
