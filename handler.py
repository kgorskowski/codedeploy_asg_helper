import json
import boto3
import time
import json
import os

autoscaling = boto3.client('autoscaling')
processes_to_suspend = ["AZRebalance", "AlarmNotification", "ScheduledActions", "ReplaceUnhealthy"]
ASG_TAGS = { 'AutomatedASGScript': 'true' }

def update_autoscaling_group(autoscaling_group, asg_min_size):
    print("Trying to reset %s to minimal size of %i instances" % (autoscaling_group, asg_min_size))
    client = boto3.client('autoscaling')
    response = client.update_auto_scaling_group(
        AutoScalingGroupName=autoscaling_group,
        MinSize=asg_min_size
        )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("DEBUG: Updating Autoscaling Group minimal size successfull")
        return True
    else:
        print("ERROR: Unable to reset minimal size of '" + autoscaling_group_name + "'")
        return False

def get_asg_min_size(autoscaling_group):
    client = boto3.client('autoscaling')
    response = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=
        [ autoscaling_group ]
    )
    asg_min_size = int(response['AutoScalingGroups'][0]['MinSize'])
    return asg_min_size

def get_autoscaling_group(tags):
    client = boto3.client('autoscaling')
    filter = list();
    for key, value in tags.items():
        filter.extend(
            [
                { 'Name': "key", 'Values': [ key ] },
                { 'Name': "value", 'Values': [ value ] }
            ]
        )
    response = client.describe_tags(Filters=filter)
    return response['Tags'][0]['ResourceId']

def suspend_processes( autoscaling_group_name, processes_to_suspend ):
    response = autoscaling.suspend_processes(
        AutoScalingGroupName=autoscaling_group_name,
        ScalingProcesses=processes_to_suspend
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("DEBUG: Autoscaling Processes suspended")
        return True
    else:
        print("ERROR: Unable to suspend_processes on '" + autoscaling_group_name + "'")
        return False

def resume_processes( autoscaling_group_name, processes_to_suspend ):

    response = autoscaling.resume_processes(
        AutoScalingGroupName=autoscaling_group_name,
        ScalingProcesses=processes_to_suspend
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("DEBUG: Autoscaling Processes resumed")
        return True
    else:
        print("ERROR: Unable to resume_processes on '" + autoscaling_group_name + "'")
        return False

def autoscale(event, context):
    autoscaling_group_name = get_autoscaling_group(ASG_TAGS)

    asg_min_size = get_asg_min_size(autoscaling_group_name)

    print("Found ASG %s with min. size of %s instances" % (autoscaling_group_name, asg_min_size))

    topic_arn = event['Records'][0]['Sns']['TopicArn']
    print('Got Message from %s' % topic_arn)
    if "suspendAutoscaling" in topic_arn:
        item = suspend_processes(autoscaling_group_name, processes_to_suspend)
        body = {
        "message": "Suspending Autoscaling Processes",
            "successful": item

        }
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

    elif "resumeAutoscaling" in topic_arn:
        update_autoscaling_group(autoscaling_group_name, asg_min_size)

        item = resume_processes(autoscaling_group_name, processes_to_suspend)
        body = {
        "message": "Resuming Autoscaling Processes",
            "succesful": item

        }
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
    else:
        print('Recieved Message from unknown SNS Topic %s - Exiting ' % topic_arn)
        return False
    print(response)
    return response
