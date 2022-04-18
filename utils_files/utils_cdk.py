""" Module to centralize common cdk function and avoid verbose things in stacks """

import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_ec2 as ec2,
)
from constructs import Construct


class CommonStacksVars(cdk.Stack):
    """Standard function to init common "self" vars between stacks"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.project_name = self.node.try_get_context("PROJECT_NAME")
        self.stage = self.node.try_get_context("STAGE")
        self.suffix = f"{self.project_name}-{self.stage}"


def create_authorizer(
    self, auth_id=None, header_token=None, validation_regex=None, authorizer=None
):
    """Standard function to create an authorizer"""
    return apigw.TokenAuthorizer(
        self,
        id=f"AUTHORIZER-{auth_id}",
        identity_source=apigw.IdentitySource.header(header_token),
        validation_regex=validation_regex,
        handler=authorizer,
        authorizer_name=f"{auth_id}-{self.suffix}",
        results_cache_ttl=cdk.Duration.minutes(0),
    )


def create_api_gateway(
    self, apigw_id, authorizer=None, default_cors_preflight_options=None
):
    """Standard function to create an API Gateway"""
    api_policy = iam.PolicyDocument(
        statements=[
            iam.PolicyStatement(
                actions=["execute-api:Invoke"],
                effect=iam.Effect.ALLOW,
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
        default_method_options=apigw.MethodOptions(authorizer=authorizer)
        if authorizer
        else None,
        default_cors_preflight_options=default_cors_preflight_options,
    )


# pylint: disable=too-many-arguments
def add_apigw_lambda_route(
    route,
    method,
    handler_lambda,
    status_code,
    authorizer=None,
    integration_response_parameters=None,
    method_response_parameters=None,
):
    """Standard function to add a route to APIGW with lambda usage"""
    # pylint: disable=line-too-long
    # See http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
    # This template will pass through all parameters including path, querystring, header,
    # stage variables, and context through to the integration endpoint via the body/payload
    default_request_template = {
        "application/json": """
        #set($allParams = $input.params())
        {
            "body-json" : $input.json('$'),
            "params" : {
                #foreach($type in $allParams.keySet())
                #set($params = $allParams.get($type))
                "$type" : {
                    #foreach($paramName in $params.keySet())
                    "$paramName" : "$util.escapeJavaScript($params.get($paramName))"
                    #if($foreach.hasNext),#end
                    #end
                }
                #if($foreach.hasNext),#end
                #end
            },
            "stage-variables" : {
                #foreach($key in $stageVariables.keySet())
                "$key" : "$util.escapeJavaScript($stageVariables.get($key))"
                #if($foreach.hasNext),#end
                #end
            },
            "context" : {
                "account-id" : "$context.identity.accountId",
                "api-id" : "$context.apiId",
                "api-key" : "$context.identity.apiKey",
                "authorizer-principal-id" : "$context.authorizer.principalId",
                "caller" : "$context.identity.caller",
                "cognito-authentication-provider" : "$context.identity.cognitoAuthenticationProvider",
                "cognito-authentication-type" : "$context.identity.cognitoAuthenticationType",
                "cognito-identity-id" : "$context.identity.cognitoIdentityId",
                "cognito-identity-pool-id" : "$context.identity.cognitoIdentityPoolId",
                "http-method" : "$context.httpMethod",
                "stage" : "$context.stage",
                "source-ip" : "$context.identity.sourceIp",
                "user" : "$context.identity.user",
                "user-agent" : "$context.identity.userAgent",
                "user-arn" : "$context.identity.userArn",
                "request-id" : "$context.requestId",
                "resource-id" : "$context.resourceId",
                "resource-path" : "$context.resourcePath"
            }
        }
        """
    }

    route.add_method(
        method,
        integration=apigw.LambdaIntegration(
            handler=handler_lambda,
            passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
            request_templates=default_request_template,
            proxy=False,
            # request_parameters={"Access-Control-Allow-Origin": "*"},
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code=str(status_code),
                    response_parameters=integration_response_parameters,
                    # response_parameters=["Access-Control-Allow-Origin"],
                )
            ],
        ),
        authorization_type=apigw.AuthorizationType.CUSTOM if authorizer else None,
        authorizer=authorizer,
        # request_parameters={"AccessControlAllowOrigin": True},
        method_responses=[
            apigw.MethodResponse(
                status_code=str(status_code),
                response_parameters=method_response_parameters,
            )
        ],
    )


# pylint: disable=too-many-arguments
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


# pylint: disable=too-many-arguments
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
    managed_policies=None,
    inline_policies=None,
):
    """Standard function to create an IAM role"""
    # Avoid dangerous default value as [] for managed policies
    # https://stackoverflow.com/questions/26320899/why-is-the-empty-dictionary-a-dangerous-default-value-in-python
    if not managed_policies:
        managed_policies = [
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole"
            )
        ]

    return iam.Role(
        self,
        id=f"IAM-ROLE-{role_id}",
        assumed_by=assumed_by,
        managed_policies=managed_policies,
        inline_policies=inline_policies,
    )


# pylint: disable=too-many-arguments
def create_s3_bucket(
    self,
    bucket_name,
    kms_key=None,
    block_public_access=None,
    enforce_ssl=None,
    public_read_access=None,
    foreign_accounts_list=None,
    website_index_document=None,
    website_error_document=None,
):
    """Standard function to create S3 Bucket"""
    s3_cors_rule = s3.CorsRule(
        allowed_methods=[s3.HttpMethods.GET],
        allowed_headers=["*"],
        allowed_origins=["*"],
    )

    s3_bucket = s3.Bucket(
        self,
        id=f"S3-{bucket_name}",
        bucket_name=bucket_name,
        encryption_key=kms_key,
        encryption=s3.BucketEncryption.KMS if kms_key else None,
        block_public_access=block_public_access,
        cors=[s3_cors_rule],
        removal_policy=cdk.RemovalPolicy.DESTROY,
        enforce_ssl=enforce_ssl,
        public_read_access=public_read_access,
        website_index_document=website_index_document,
        website_error_document=website_error_document,
    )

    # If you want to allow another AWS account(s) to access your bucket
    if foreign_accounts_list:
        for account in foreign_accounts_list:
            bucket_policy = iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AccountPrincipal(account)],
                resources=[s3_bucket.bucket_arn, f"{s3_bucket.bucket_arn}/*"],
                actions=["s3:*"],
            )
            s3_bucket.add_to_resource_policy(bucket_policy)

    return s3_bucket


def get_vpc(self):
    """Standard function to get VPC"""
    return ec2.Vpc.from_lookup(
        self,
        id="VPC",
        vpc_id=self.node.try_get_context("VPC_ID"),
        is_default=True,
    )
