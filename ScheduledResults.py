from .app import db
   
# Product Class/Model
class ScheduledResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedulerId = db.Column(db.String(18), unique=True)
    userId = db.Column(db.String(18), unique=True, nullable=False)
    jobId = db.Column(db.String(18), unique=True, nullable=False)

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

# Run Server
if (__name__ == '__main__'):
    app.run(debug=True)