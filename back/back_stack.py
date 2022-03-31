""" Back End Stack """

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_dynamodb as ddb,
    aws_iam as iam,
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

        # ### ROLES ### #
        role_lambda_access_ddb = utils_cdk.create_role(
            self,
            role_id="IAM-role-access-ddb",
            inline_policies={
                "ec2_kms_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["dynamodb:*"],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                            sid="lambdaDDBAccess",
                        ),
                    ]
                )
            },
        )

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

        # ### DYNAMODB ### #
        ddb_request_count = utils_cdk.create_dynamodb(
            self,
            table_name="request-count",
            partition_key=ddb.Attribute(
                name="status_code", type=ddb.AttributeType.NUMBER
            ),
            on_demand=True,
        )

        # ### LAMBDAS ### #
        utils_cdk.create_lambda(
            self,
            name="test_request",
            layers=[layer_requests],
            environment={"TABLE_REQUEST_COUNT": ddb_request_count.table_name},
            role=role_lambda_access_ddb,
        )
