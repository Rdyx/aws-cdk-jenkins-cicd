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
            role_id=f"access-ddb-{self.suffix}",
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
            id=f"SG-lambda-{self.suffix}",
            vpc=self.vpc,
        )

        # ### DYNAMODB ### #
        ddb_url_request_count = utils_cdk.create_dynamodb(
            self,
            table_id=f"url-request-count-{self.suffix}",
            partition_key=ddb.Attribute(name="url", type=ddb.AttributeType.STRING),
            # Set table name only when you're certain about your partition_key & sort_key
            # if you're using one. Changing a table name is not possible afterwise unless
            # you delete the stack.
            # table_name="url-request-count",
            sort_key=ddb.Attribute(name="status_code", type=ddb.AttributeType.NUMBER),
        )

        # ### LAMBDAS ### #
        lambda_auth = utils_cdk.create_lambda(self, name=f"auth")

        lb_request_and_increment_url_counter = utils_cdk.create_lambda(
            self,
            name="request_and_increment_url_counter",
            layers=[layer_requests],
            environment={
                "TABLE_URL_REQUEST_COUNT_NAME": ddb_url_request_count.table_name
            },
            role=role_lambda_access_ddb,
        )

        lb_get_url_counter = utils_cdk.create_lambda(
            self,
            name="get_url_counter",
            layers=[layer_requests],
            environment={
                "TABLE_URL_REQUEST_COUNT_NAME": ddb_url_request_count.table_name
            },
            role=role_lambda_access_ddb,
        )

        # ### API GATEWAY ### #
        api_gateway = utils_cdk.create_api_gateway(
            self,
            apigw_id=self.suffix,
            lambda_auth=lambda_auth,
        )

        # ### API GATEWAY ROUTES ### #
        # /increment-url-counter
        increment_url_counter_route = api_gateway.root.add_resource(
            "increment-url-counter"
        )
        utils_cdk.add_apigw_lambda_route(
            increment_url_counter_route,
            "POST",
            lb_request_and_increment_url_counter,
            201,
        )

        # /get-url-counter
        get_url_counter_route = api_gateway.root.add_resource("get-url-counter")
        utils_cdk.add_apigw_lambda_route(
            get_url_counter_route, "GET", lb_get_url_counter, 200
        )
