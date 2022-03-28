import aws_cdk as core
import aws_cdk.assertions as assertions

from back.back_stack import BackStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cdk_jenkins_cicd/aws_cdk_jenkins_cicd_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BackStack(app, "aws-cdk-jenkins-cicd")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
