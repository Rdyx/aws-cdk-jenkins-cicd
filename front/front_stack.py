""" Front End Stack """

from constructs import Construct

from utils_files import utils_cdk


class FrontStack(utils_cdk.CommonStacksVars):
    """Front Stack"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ### GET VPC ### #
        self.vpc = utils_cdk.get_vpc(self)

        # ### S3 BUCKET ### #
        utils_cdk.create_s3_bucket(
            self,
            bucket_name=f"front-{self.suffix}",
            public_read_access=True,
            website_index_document="index.html",
            # Little hack to be able to use react-router routes with s3 hosting
            website_error_document="index.html",
        )
