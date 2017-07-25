## A Serverless package to suspend and resume autoscaling processes during CodeDeploy Deployments


AWS has published a set of [scripts]( https://github.com/awslabs/aws-codedeploy-samples) for the  CodeDeploy/Autoscaling/LoadBalancing workflow.
Unfortunately they are not usable with the new Application Loadbalancer.
As we were running into some problems eventually when autoscaling processes disturbed our CodeDeploy workflow, I quickly hacked together a Python/Lambda function to recreate the functionality of the scripts with Lambda.

Instead of suspending and resuming the autoscaling processes on every instance of the deployment, I make use of Lambda and two SNS topics to trigger the function when a Deployment starts and ends.

As I said, this is a quick and dirty hack, feel free to fork, improve, rewrite it to your needs.


For easier deployment I really like the [Serverless Framework](https://serverless.com/) so I used it here again.

If you want to try it out, you can either just take the code or clone/fork this repository and change it to fit your needs.

For deployment with Serverless, rename `handler.py.template` to `handler.py` and insert the name of the target autoscaling group. In `serverless.yaml` enter the correct AWS region and deploy the function with `serverless deploy`.

Serverless creates the the function, the reeded IAM role and two SNS topics. To suspend and resume the autoscaling processes, create two Triggers in your Deployment settings - eg `suspendAutoscalingProcesses` and `resumeAutoscalingProcesses`.
Trigger `suspendAutoscalingProcesses` whenever a Deployment starts and `resumeAutoscalingProcesses` whenever a Deployment is successful, stops or fails.
