""" Back End Stack """

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_ec2 as ec2,
)
from constructs import Construct
from utils_files import utils_cdk


class BackStack(Stack):
    """Back Stack"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.project_name = self.node.try_get_context("PROJECT_NAME")
        self.stage = self.node.try_get_context("STAGE")
        self.suffix = f"{self.project_name}-{self.stage}"

        # ### GET VPC ### #
        self.vpc = ec2.Vpc.from_lookup(
            self,
            id="VPC",
            vpc_id=self.node.try_get_context("VPC_ID"),
            is_default=True,
        )

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
