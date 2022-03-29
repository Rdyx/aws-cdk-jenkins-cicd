""" Quick script to delete env from Jenkins """

import os
import sys
import boto3

AWS_REGION = os.environ.get("AWS_ACCOUNT")


def delete_env(branch_number):
    """Delete Environment on target branch"""

    print(f"Branch number: {branch_number}")

    s3_client = boto3.client("s3")
    cloudformation = boto3.resource("cloudformation", region_name=AWS_REGION)

    buckets_list = [
        bucket
        for bucket in s3_client.buckets.all()
        if bucket.name.endsWith(branch_number)
    ]
    stacks_list = [
        stack
        for stack in cloudformation.stacks.all()
        if stack.name.endsWith(branch_number)
    ]

    if len(buckets_list):
        # Empty each bucket related to the branch
        for bucket in buckets_list:
            bucket.objects.all().delete()

    if len(stacks_list):
        for stack in stacks:
            stack.delete()


if __name__ == "__main__":
    delete_env(sys.argv[1])
