#! /usr/bin/env python

import os
from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from __future__ import division

def crab_cmd(configuration):

    try:
        output = crabCommand(configuration['cmd'], **configuration['args'])
        return output
    except HTTPException as hte:
        print('Failed', configuration['cmd'], 'of the task: %s' % (hte.headers))
    except ClientException as cle:
        print('Failed', configuration['cmd'], 'of the task: %s' % (cle))
        

def parse_result(listOfTasks):

    testResult = []

    for task in listOfTasks:
        if task['dbStatus'] == 'SUBMITTED':
            total_jobs = sum(task['jobsPerStatus'].values())

            if ('finished', total_jobs) in task['jobsPerStatus'].items():
                result = 'TestPassed'
            elif any(k in task['jobsPerStatus'] for k in ('failed', 'held')):
                result = 'TestFailed'
            else:
                result = 'TestRunning'
        elif task['dbStatus'] in ['HOLDING', 'QUEUED', 'NEW']:
            result = 'TestRunning'
        else:
            result = 'TestFailed'

        testResult.append({'taskName': task['taskName'], 'testResult': result, 'jobsPerStatus': task['jobsPerStatus']})

    return testResult


def main():

    listOfTasks = []
    instance = os.environ['REST_Instance']

    with open('/artifacts/submitted_tasks') as fp:
        tasks = fp.readlines()

    for task in tasks:
        remake_dict = {'task': task, 'instance': instance}
        remake_dir = crab_cmd({'cmd': 'remake', 'args': remake_dict})

        status_dict = {'dir': remake_dir}
        status_command_output = crab_cmd({'cmd': 'status', 'args': status_dict})
        status_command_output.update({'taskName': task.rstrip()})
        listOfTasks.append(status_command_output)

    summary = parse_result(listOfTasks)

    with open('/artifacts/result', 'w') as fp:
        for result in summary:
            fp.write("%s\n" % result)


if __name__ == '__main__':
    main()

