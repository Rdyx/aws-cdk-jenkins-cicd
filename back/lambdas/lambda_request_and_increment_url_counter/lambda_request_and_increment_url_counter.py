"""
    Example lambda which is pinging an url and stores the returned status_code in
    a DynamoDB table
"""

import os
import requests

import boto3

from boto3.dynamodb.conditions import Key


DDB = boto3.resource("dynamodb")
TABLE_URL_REQUEST_COUNT = DDB.Table(os.environ.get("TABLE_URL_REQUEST_COUNT_NAME"))


def get_table_data(url, status_code):
    """Query data from DynamoDB"""
    return TABLE_URL_REQUEST_COUNT.query(
        KeyConditionExpression=Key("url").eq(url) & Key("status_code").eq(status_code)
    )["Items"]


def write_table_data(item):
    """Write data in DynamoDB"""
    TABLE_URL_REQUEST_COUNT.put_item(Item=item)


def increment_status_code_counter(url, status_code):
    """Get data, increment counter in DynamoDB and return it"""
    status_table_data = get_table_data(url, status_code)

    if status_table_data:
        status_table_data[0]["counter"] += 1
    else:
        status_table_data.append({"url": url, "status_code": status_code, "counter": 1})

    write_table_data(status_table_data[0])

    return status_table_data[0]


def lambda_handler(event, _):
    """Lambda Handler, default lambda executed function"""
    print(f"Lambda handler: {event}")

    url = "https://google.comz"

    if "body-json" in event:
        if "url" in event["body-json"]:
            url = event["body-json"]["url"]

    try:
        res = requests.get(url)
        return increment_status_code_counter(url, res.status_code)

    # pylint: disable=broad-except
    except Exception as err:
        print(err)
        return increment_status_code_counter(url, 500)
