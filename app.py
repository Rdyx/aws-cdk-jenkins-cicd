#!/usr/bin/env python3
import aws_cdk as cdk

from back.back_stack import BackStack
from front.front_stack import FrontStack


app = cdk.App()
ENV = cdk.Environment(
    region=app.node.try_get_context("AWS_REGION"),
    account=app.node.try_get_context("AWS_ACCOUNT"),
)
SUFFIX = app.node.try_get_context("SUFFIX")
STAGE = app.node.try_get_context("STAGE")

BackStack(app, f"back-{SUFFIX}-{STAGE}", env=ENV)
FrontStack(app, f"front-{SUFFIX}-{STAGE}", env=ENV)

app.synth()
