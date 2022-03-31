import os
import requests

import boto3

from boto3.dynamodb.conditions import Key


DDB = boto3.resource("dynamodb")
table_request_count = DDB.Table(os.environ.get("TABLE_REQUEST_COUNT"))


def increment_status_code_counter(status_code):
    ddb_status_code_data = table_request_count.query(
        KeyConditionExpression=Key("status_code").eq(status_code)
    )["Items"]

    if ddb_status_code_data[0]:
        ddb_status_code_data[0]["counter"] += 1
    else:
        ddb_status_code_data[0] = {"status_code": status_code, "counter": 1}

    table_request_count.put_item(ddb_status_code_data[0])

    return ddb_status_code_data[0]


def lambda_handler(event, context):
    try:
        res = requests.get("https://google.com")
        return increment_status_code_counter(res.status_code)
    except:
        return "Error"
