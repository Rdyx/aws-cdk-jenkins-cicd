""" Quick script to delete env from Jenkins """

import os
import sys
import boto3

AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION")


def delete_env(branch_id):
    """Delete Environment on target branch"""

    print(f"Branch id: {branch_id}")

    s3_client = boto3.resource("s3")
    cloudformation = boto3.resource("cloudformation", region_name=AWS_DEFAULT_REGION)

    buckets_list = [
        bucket for bucket in s3_client.buckets.all() if bucket.name.endswith(branch_id)
    ]
    stacks_list = [
        stack for stack in cloudformation.stacks.all() if stack.name.endswith(branch_id)
    ]

    if len(buckets_list):
        # Empty each bucket related to the branch, this will allow stack deletion
        # To delete bucket with no error
        for bucket in buckets_list:
            bucket.objects.all().delete()

    if len(stacks_list):
        for stack in stacks_list:
            stack.delete()


if __name__ == "__main__":
    delete_env(sys.argv[1])
