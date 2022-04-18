""" Back End Stack """

from aws_cdk import (
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_apigateway as apigw,
)
from constructs import Construct
from utils_files import utils_cdk


class BackStack(utils_cdk.CommonStacksVars):
    """Back Stack"""

    # pylint: disable=too-many-locals
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
        self.vpc = utils_cdk.get_vpc(self)

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
        lambda_auth = utils_cdk.create_lambda(self, name="auth")

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

        # ### AUTHORIZERS ### #
        authorizer = utils_cdk.create_authorizer(
            self,
            auth_id="token_auth",
            header_token="AuthToken",
            validation_regex="MyAccessToken",
            authorizer=lambda_auth,
        )

        # ### API GATEWAY ### #
        api_gateway = utils_cdk.create_api_gateway(
            self,
            apigw_id=self.suffix,
            # Setting an authorizer on the whole RestAPI will set it up on OPTIONS HTTP methods
            # Which will block CORS requests. It's better to set it manually on each
            # RestAPI route manually if you want to be able to use CORS.
            # Known "bug": https://github.com/aws/aws-cdk/issues/8615
            # authorizer=authorizer,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_headers=apigw.Cors.DEFAULT_HEADERS + ["AuthToken"],
                allow_methods=["GET", "POST", "OPTIONS"],
            ),
        )

        # ### API GATEWAY ROUTES ### #
        # Adding CORS rules for our routes
        method_response_parameters = {
            "method.response.header.Access-Control-Allow-Origin": True
        }
        # Note the single quotes around the wildcard, they are very important
        integration_response_parameters = {
            "method.response.header.Access-Control-Allow-Origin": "'*'"
        }

        # /increment-url-counter
        increment_url_counter_route = api_gateway.root.add_resource(
            "increment-url-counter"
        )
        utils_cdk.add_apigw_lambda_route(
            route=increment_url_counter_route,
            method="POST",
            handler_lambda=lb_request_and_increment_url_counter,
            status_code=201,
            authorizer=authorizer,
            method_response_parameters=method_response_parameters,
            integration_response_parameters=integration_response_parameters,
        )

        # /get-url-counter
        get_url_counter_route = api_gateway.root.add_resource("get-url-counter")
        utils_cdk.add_apigw_lambda_route(
            route=get_url_counter_route,
            method="GET",
            handler_lambda=lb_get_url_counter,
            status_code=200,
            authorizer=authorizer,
            method_response_parameters=method_response_parameters,
            integration_response_parameters=integration_response_parameters,
        )
