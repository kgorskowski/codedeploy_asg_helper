## A Serverless package to suspend and resume autoscaling processes during CodeDeploy Deployments


AWS has published a set of [scripts]( https://github.com/awslabs/aws-codedeploy-samples) for the  CodeDeploy/Autoscaling/LoadBalancing workflow.
Unfortunately they are not usable with the new Application Loadbalancer.
As we were running into some problems eventually when autoscaling processes disturbed our CodeDeploy workflow, I quickly hacked together a Python/Lambda function to recreate the functionality of the scripts with Lambda.

Instead of suspending and resuming the autoscaling processes on every instance of the deployment, I make use of Lambda and two SNS topics to trigger the function when a Deployment starts and ends.

As I said, this is a quick and dirty hack, feel free to fork, improve, rewrite it to your needs.


For easier deployment I really like the [Serverless Framework](https://serverless.com/) so I used it here again.

If you want to try it out, you can either just take the code or clone/fork this repository and change it to fit your needs.

For deployment with Serverless, rename `handler.py.template` to `handler.py` ~~and insert the name of the target autoscaling group~~. I ditchend the hardcoded ASG Name for a Tag on the ASG. Con: Works right now just with one single affected Autoscaling Group. Not sure how to further improve this. Anyways, if this is sufficient for you, create a Tag on your Autoscaling Group Key name `AutomatedASGScript`- Value `true` and in `serverless.yaml` enter the correct AWS region and deploy the function with `serverless deploy`.

Additionally the Lambda now initially checks the Autoscaling Group for the minimal number of instances and resets the value after a deployment (no matter if succesful or failed).

This should prevent the situation when the AWS helper decrement the minimal size of the group anf fail to reset the value.
So after every deployment, the minimal size of your Autoscaling Group will be set to the value it had when the deployment started.

Serverless creates the the function, the necessary IAM role and two SNS topics. To suspend and resume the autoscaling processes, create two Triggers in your Deployment settings - eg `suspendAutoscalingProcesses` and `resumeAutoscalingProcesses`.
Trigger `suspendAutoscalingProcesses` whenever a Deployment starts and `resumeAutoscalingProcesses` whenever a Deployment is successful, stops or fails so the processes are restored whenever a deployment stops, successful or unsuccesful.

There isn't any error checking or notification/alerting (yet?) intead of logging to CloudWatch Logs, so be advised to check them out if you think something went wrong.

So: Use at your own risk.
