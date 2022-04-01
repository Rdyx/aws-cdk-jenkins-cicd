""" Front End Stack """

from aws_cdk import Duration, Stack, aws_sqs as sqs, aws_ec2 as ec2, aws_s3 as s3
from constructs import Construct

from utils_files import utils_cdk


class FrontStack(Stack):
    """Front Stack"""

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

        # ### S3 BUCKET ### #
        utils_cdk.create_s3_bucket(
            self,
            bucket_name=f"front-{self.suffix}",
            public_read_access=True,
            website_index_document="index.html",
            website_error_document="index.html",
        )
