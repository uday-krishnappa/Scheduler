from __future__ import print_function
from ortools.sat.python import cp_model
import time
import numpy as np
from .ScheduledResults import ScheduledResult

class SimpleSolver():
    
    def __init__(self, scheduler_Id, jobIds, time_needed, userIds, time_capacity):
        self.scheduler_Id = scheduler_Id
        self.jobIds = jobIds
        self.time_needed = time_needed
        self.userIds = userIds
        self.time_capacity = time_capacity
        self.jobSize = len(jobIds)
        self.employeeSize = len(userIds)

    def solve(self):
        model = cp_model.CpModel()

        start = time.time()

        # Makes a matrix of shape: employeeSize * jobSize and makes all values equal to one
        cost = np.ones((self.employeeSize, self.jobSize), dtype=int)

        sizes = self.time_needed
        total_size_max = 15
        num_workers = self.employeeSize
        num_tasks = self.jobSize

        # Variables
        x = []
        for i in range(num_workers):
            t = []
            for j in range(num_tasks):
                t.append(model.NewIntVar(0, 1, "x[%i,%i]" % (i, j)))
            x.append(t)
        x_array = [x[i][j] for i in range(num_workers) for j in range(num_tasks)]

        # Constraints

        # Each task is assigned to at least one worker.
        [model.Add(sum( x[i][j] for i in range(num_workers) ) >= 1)
        for j in range(num_tasks)]

        # Total size of tasks for each worker is at most total_size_max.

        [ model.Add(sum( sizes[j] * x[i][j] for j in range(num_tasks) ) <= self.time_capacity[i])
        for i in range(num_workers) ]
        
        model.Minimize(sum([np.dot(x_row, cost_row) for (x_row, cost_row) in zip(x, cost)]))
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        toInsert = []

        if status == cp_model.OPTIMAL:

            for i in range(num_workers):
                for j in range(num_tasks):

                    if solver.Value(x[i][j]) == 1:
                        r = ScheduledResult(self.scheduler_Id, self.userIds[i], self.jobIds[j])
                        toInsert.append(r)

            db.session.add(toInsert)
            db.session.commit

            return scheduledResults_schema(toInsert)
        else :
            return 'Bad Request'

if __name__ == '__main__':
  main()