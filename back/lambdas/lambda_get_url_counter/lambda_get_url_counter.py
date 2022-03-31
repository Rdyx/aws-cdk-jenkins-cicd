import boto3
import os
from boto3.dynamodb.conditions import Key


DDB = boto3.resource("dynamodb")
TABLE_URL_REQUEST_COUNT = DDB.Table(os.environ.get("TABLE_URL_REQUEST_COUNT_NAME"))


def get_table_data(url):
    """Query data from DynamoDB"""
    return TABLE_URL_REQUEST_COUNT.query(KeyConditionExpression=Key("url").eq(url))[
        "Items"
    ]


def lambda_handler(event, context):
    """Lambda Handler"""
    print(f"Lambda handler: {event}")

    url = event["url"] if "url" in event else "https://google.comz"

    try:
        return get_table_data(url)
    except Exception as err:
        print(err)
        return "No Data"
