from __future__ import print_function
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from ortools.sat.python import cp_model
import time
import numpy as np

import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath( os.path.dirname(__file__) )
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db

db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Product Class/Model
class ScheduledResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedulerId = db.Column(db.String(16), unique=True)
    userId = db.Column(db.String(16), unique=True, nullable=False)
    jobId = db.Column(db.String(16), unique=True, nullable=False)

    def __init__(self, schedulerId, userId, jobId):
        self.schedulerId = schedulerId
        self.userId = userId
        self.jobId = jobId

# Product Schema
class SchedulerSchema(ma.Schema):
    class Meta:
        fields = ('schedulerId', 'userId', 'jobId')

# Init schema
scheduledResult_schema = SchedulerSchema()
scheduledResults_schema = SchedulerSchema(many = True)

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
                        print('i = '+self.userIds[i]+' j = '+self.jobIds[j])
                        r = ScheduledResult(self.scheduler_Id, self.userIds[i], self.jobIds[j])
                        toInsert.append(r)

            db.session.add_all(toInsert)
            db.session.commit

            return scheduledResults_schema.jsonify(toInsert)
        else :
            return 'Bad Request'

def checkSize(jobIds, time_needed, userIds, time_capacity):
    if ( (len(jobIds) == len(time_needed)) and (len(userIds) == len(time_capacity)) ):
        return True
    else:
        return False

@app.route('/simpleScheduler', methods = ['POST'])
def build_model():
    scheduler_Id = request.json['scheduler_Id']
    jobIds = request.json['jobIds']
    time_needed = request.json['time_needed']
    userIds = request.json['userIds']
    time_capacity = request.json['time_capacity']
    print(jobIds)
    if checkSize(jobIds, time_needed, userIds, time_capacity):
        problem = SimpleSolver(scheduler_Id,jobIds,time_needed, userIds, time_capacity)

        return problem.solve()
    else :
        return 'Bad Request'
        
# Run Server
if __name__ == '__main__':
    app.run(debug = True)
