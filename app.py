#!/usr/bin/env python3
import aws_cdk as cdk

from back.back_stack import BackStack
from front.front_stack import FrontStack


app = cdk.App()
ENV = cdk.Environment(
    region=app.node.try_get_context("AWS_DEFAULT_REGION"),
    account=app.node.try_get_context("AWS_ACCOUNT"),
)
PROJECT_NAME = app.node.try_get_context("PROJECT_NAME")
STAGE = app.node.try_get_context("STAGE")

BackStack(app, f"back-{PROJECT_NAME}-{STAGE}", env=ENV)
FrontStack(app, f"front-{PROJECT_NAME}-{STAGE}", env=ENV)

app.synth()
