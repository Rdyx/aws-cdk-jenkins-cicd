""" Unit Tests for Front Stack """
import aws_cdk as cdk

from aws_cdk import assertions

from back.back_stack import BackStack

app = cdk.App()
ENV = cdk.Environment(
    region=app.node.try_get_context("AWS_DEFAULT_REGION"),
    account=app.node.try_get_context("AWS_ACCOUNT"),
)
PROJECT_NAME = app.node.try_get_context("PROJECT_NAME")
STAGE = app.node.try_get_context("STAGE")

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cdk_jenkins_cicd/aws_cdk_jenkins_cicd_stack.py
def test_sqs_queue_created():
    """Example Unit Test"""
    stack = BackStack(app, f"back-{PROJECT_NAME}-{STAGE}", env=ENV)
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {"VisibilityTimeout": 300})
