from asyncore import read
import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_, aws_dynamodb as ddb, aws_iam as iam


def create_lambda(
    self, name, layers=None, environment=None, role=None, timeout=10, memory_size=128
):
    """Standard function to create a lambda"""

    # Note: AWS is not allowing underscore in lambda's ID & Name
    normalized_name = f"{name.replace('_', '-')}-{self.suffix}"

    return lambda_.Function(
        self,
        id=f"lambda-{normalized_name}",
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
    name,
    partition_key,
    sort_key=None,
    read_capacity=None,
    write_capacity=None,
    ttl_attribute=None,
    kms_key=None,
    stream=None,
    on_demand=False,
):
    # PAY_PER_REQUEST mode require to manually set RCUs & WCUs.
    # Set default to 5 if none is provided
    if on_demand and not read_capacity:
        read_capacity = 5
    if on_demand and not write_capacity:
        write_capacity = 5

    return ddb.Table(
        self,
        id=f"table-{name}",
        table_name=name,
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
    return iam.Role(
        self,
        id=role_id,
        assumed_by=assumed_by,
        managed_policies=managed_policies,
        inline_policies=inline_policies,
    )
