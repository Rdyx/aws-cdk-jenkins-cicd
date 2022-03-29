""" Back End Stack """

from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
)
from constructs import Construct


class BackStack(Stack):
    """Back Stack"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        sqs.Queue(
            self,
            id="back-SQS"
            queue_name="back-SQS-name",
            visibility_timeout=Duration.seconds(300),
        )
