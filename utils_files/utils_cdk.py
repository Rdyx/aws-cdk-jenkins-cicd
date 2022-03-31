""" Module to centralize common cdk function and avoid verbose things in stacks """

import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_apigateway as apigw,
)


def create_api_gateway(
    self,
    apigw_id,
    auth_id="token_auth",
    header_token="AuthToken",
    validation_regex="MyAccessToken",
    lambda_auth=None,
):
    """Standard function to create an API Gateway"""
    # Example with authorizer authentication
    authorizer = apigw.TokenAuthorizer(
        self,
        id=f"AUTHORIZER-{auth_id}",
        identity_source=apigw.IdentitySource.header(header_token),
        validation_regex=validation_regex,
        handler=lambda_auth,
        authorizer_name="token_auth",
        results_cache_ttl=cdk.Duration.minutes(0),
    )

    api_policy = iam.PolicyDocument(
        statements=[
            iam.PolicyStatement(
                actions=["execute-api:Invoke"],
                effect=iam.Effect.ALLOW,
                principals=[iam.ArnPrincipal("*")],
                resources=["execute-api:/*"],
            ),
            iam.PolicyStatement(
                actions=["execute-api:Invoke"],
                effect=iam.Effect.DENY,
                conditions={"StringNotEquals": {"aws:sourceVpc": self.vpc.vpc_id}},
                principals=[iam.ArnPrincipal("*")],
                resources=["execute-api:/*"],
            ),
        ],
    )

    return apigw.RestApi(
        self,
        id=f"APIGW-{apigw_id}",
        rest_api_name=f"APIGW-{apigw_id}",
        endpoint_configuration=apigw.EndpointConfiguration(
            types=[apigw.EndpointType.EDGE]
        ),
        policy=api_policy,
        deploy_options=apigw.StageOptions(
            stage_name=self.node.try_get_context("STAGE"),
        ),
        # Uncomment if you want to enable a custom authorizer
        default_method_options=apigw.MethodOptions(authorizer=authorizer),
    )


def add_apigw_lambda_route(route, method, lambda_):
    route.add_method(
        method,
        apigw.LambdaIntegration(
            handler=lambda_,
            passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
            # request_templates=
            proxy=False,
            integration_responses=[apigw.IntegrationResponse(status_code="200")],
        ),
        method_responses=[apigw.MethodResponse(status_code="200")],
    )


def create_lambda(
    self, name, layers=None, environment=None, role=None, timeout=10, memory_size=128
):
    """Standard function to create a lambda"""

    # Note: AWS is not allowing underscore in lambda's ID & Name
    normalized_name = f"{name.replace('_', '-')}-{self.suffix}"

    return lambda_.Function(
        self,
        id=f"LAMBDA-{normalized_name}",
        function_name=f"{normalized_name}",
        code=lambda_.AssetCode(f"back/lambdas/lambda_{name}"),
        handler=f"lambda_{name}.lambda_handler",
        runtime=lambda_.Runtime.PYTHON_3_8,
        layers=layers,
        environment=environment,
        role=role,
        timeout=cdk.Duration.seconds(timeout),
        memory_size=memory_size,
        security_groups=[self.lambda_security_group],
    )


def create_dynamodb(
    self,
    table_id,
    partition_key,
    table_name=None,
    sort_key=None,
    read_capacity=None,
    write_capacity=None,
    ttl_attribute=None,
    kms_key=None,
    stream=None,
    on_demand=True,
):
    """Standard function to create a DynamoDB"""
    # PAY_PER_REQUEST mode require to manually set RCUs & WCUs.
    # Set default to 5 if none is provided
    if not on_demand and not read_capacity:
        read_capacity = 5
    if not on_demand and not write_capacity:
        write_capacity = 5

    return ddb.Table(
        self,
        id=f"TABLE-{table_id}",
        table_name=table_name,
        partition_key=partition_key,
        sort_key=sort_key,
        read_capacity=read_capacity,
        write_capacity=write_capacity,
        time_to_live_attribute=ttl_attribute,
        encryption_key=kms_key,
        encryption=ddb.TableEncryption.CUSTOMER_MANAGED if kms_key else None,
        removal_policy=cdk.RemovalPolicy.DESTROY,
        stream=stream,
        billing_mode=ddb.BillingMode.PAY_PER_REQUEST
        if on_demand
        else ddb.BillingMode.PROVISIONED,
    )


def create_role(
    self,
    role_id,
    assumed_by=iam.ServicePrincipal(service="lambda.amazonaws.com"),
    managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name(
            "service-role/AWSLambdaVPCAccessExecutionRole"
        )
    ],
    inline_policies=None,
):
    """Standard function to create an IAM role"""
    return iam.Role(
        self,
        id=f"IAM-ROLE-{role_id}",
        assumed_by=assumed_by,
        managed_policies=managed_policies,
        inline_policies=inline_policies,
    )
