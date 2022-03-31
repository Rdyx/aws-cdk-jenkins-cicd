import boto3
import os
from boto3.dynamodb.conditions import Key


DDB = boto3.resource("dynamodb")
TABLE_URL_REQUEST_COUNT = DDB.Table(os.environ.get("TABLE_URL_REQUEST_COUNT_NAME"))


def get_table_data(url):
    """Query data from DynamoDB"""
    if url:
        return TABLE_URL_REQUEST_COUNT.query(KeyConditionExpression=Key("url").eq(url))[
            "Items"
        ]
    else:
        return TABLE_URL_REQUEST_COUNT.scan()


def lambda_handler(event, context):
    """Lambda Handler"""
    print(f"Lambda handler: {event}")

    url = (
        event["params"]["querystring"]["url"]
        if "url" in event["params"]["querystring"]
        else None
    )

    try:
        return get_table_data(url)
    except Exception as err:
        print(err)
        return "Oops"
