""" Back End Stack """

from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_ec2 as ec2,
)
from constructs import Construct
import utils_files.utils_cdk as utils_cdk


class BackStack(Stack):
    """Back Stack"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.suffix = f"{self.node.try_get_context('PROJECT_NAME')}-{self.node.try_get_context('STAGE')}"
        # The code that defines your stack goes here

        # example resource
        # sqs.Queue(
        #     self,
        #     id="back-SQS",
        #     queue_name="back-SQS-name",
        #     visibility_timeout=Duration.seconds(300),
        # )
        # ### GET VPC ### #
        self.vpc = ec2.Vpc.from_lookup(
            self,
            id="VPC",
            vpc_id=self.node.try_get_context("VPC_ID"),
            is_default=False,
        )

        # self.

        # ### LAYERS ### #
        layer_requests = lambda_.LayerVersion(
            self,
            id=f"LAYER-requests-{self.suffix}",
            code=lambda_.AssetCode("back/lambdas_layers/requests"),
            description="Layer containing the requests package.",
        )

        # ### SECURITY GROUPS ### #
        self.lambda_security_group = ec2.SecurityGroup(
            self,
            id=f"lambda-security-group-{self.suffix}",
            vpc=self.vpc,
            security_group_name=f"lambda_security-group-{self.suffix}",
        )
        # ### LAMBDAS ### #
        utils_cdk.create_lambda(self, "test_request", [layer_requests])
