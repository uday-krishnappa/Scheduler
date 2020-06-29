# Scheduler

## Usage

All responses will have this form 

'''json
{
    "data": "Mixed type holding the content of the response",
    "message": "Description if what happened"
}
'''

Subsequesnt response definitions will only detail the expected value of the 'data' field

### Requesting a new Job Schedueling

**Definition**

'POST /basic_Scheduler'

**Arguments**

-'"Scheduler ID":string' a globally unique identfier for the Scheduling job
-'"Job Ids and Time needed": List<Map>(['string' : 'number'])' List of unique job id's and the time needed to complete
-'"User Ids and their availability": List<Map>(['string' : 'number'])' List of unique user id's and thier available time

If the Scheduler id is already used, the existing scheduler will be overwritten.

**Response**

- '201 Scheduler created' on success

'''json
{
    "scheduler_Id" : 'String',
    "jobIds" :         '[string]',
    "time_needed" :    '[number]',
    "userIds" :        '[string]',
    "time_capacity" :  '[number]'
}

## Lookup Scheduler Results

**Defenition**

'GET /basic_Scheduler_Result/<Scheduler Id>'

**Response**

- '404 Not Found' if the Scheduler is not present
- '200 OK' on success

'''json
{
    [
        {
            "userId":"jobId"
        },
        {
            "userId":"jobId"
        }
    ]
}
'''