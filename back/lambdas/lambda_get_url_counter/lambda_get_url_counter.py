""" Lambda returning URL counter status from DDB """
import os
import boto3
from boto3.dynamodb.conditions import Key


DDB = boto3.resource("dynamodb")
TABLE_URL_REQUEST_COUNT = DDB.Table(os.environ.get("TABLE_URL_REQUEST_COUNT_NAME"))


def get_table_data(url):
    """Query data from DynamoDB"""
    if url:
        return TABLE_URL_REQUEST_COUNT.query(
            KeyConditionExpression=Key("url").eq(url),
        )["Items"]
    return TABLE_URL_REQUEST_COUNT.scan()["Items"]


def lambda_handler(event, _):
    """Lambda Handler"""
    print(f"Lambda handler: {event}")

    url = None

    if "params" in event:
        if "querystring" in event["params"]:
            if "url" in event["params"]["querystring"]:
                url = event["params"]["querystring"]["url"]

    try:
        return get_table_data(url)

    # pylint: disable=broad-except
    except Exception as err:
        print(err)
        return err
