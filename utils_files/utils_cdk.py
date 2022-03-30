from aws_cdk import cdk, Duration, aws_lambda as lambda_


def create_lambda(
    self, name, layers=None, environment=None, role=None, timeout=None, memory_size=None
):
    """Standard function to create a lambda"""

    # Note: AWS is not allowing underscore in lambda's ID & Name
    normalized_name = f"{name.replace('_', '-')}-{self.suffix}"

    return lambda_.Function(
        self,
        id=f"lambda-{normalized_name}",
        function_name=f"{normalized_name}",
        code=lambda_.Code.asset(f"back/lambdas/lambda_{name}"),
        handler=f"lambda_{name}.lambda_handler",
        runtime=lambda_.Runtime.PYTHON_3_8,
        layers=layers,
        environment=environment,
        role=role,
        timeout=cdk.Duration.seconds(timeout) if timeout else cdk.Duration.seconds(10),
        memory_size=memory_size if memory_size else 128,
        security_group=self.lambda_security_group,
    )
