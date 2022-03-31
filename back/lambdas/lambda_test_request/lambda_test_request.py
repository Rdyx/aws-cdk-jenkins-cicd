import os
import requests

import boto3

from boto3.dynamodb.conditions import Key


DDB = boto3.resource("dynamodb")
table_url_request_count = DDB.Table(os.environ.get("TABLE_URL_REQUEST_COUNT"))


def increment_status_code_counter(url, status_code):
    queryresult = table_url_request_count.query(
        KeyConditionExpression=Key("status_code").eq(status_code) & Key("url").eq(url)
    )["Items"]

    if queryresult:
        queryresult[0]["counter"] += 1
    else:
        queryresult.append({"status_code": status_code, "counter": 1, "url": url})

    table_url_request_count.put_item(Item=queryresult[0])

    return queryresult[0]


def lambda_handler(event, context):
    url = event["url"] if "url" in event else "https://google.comz"

    try:
        res = requests.get(url)
        return increment_status_code_counter(url, res.status_code)
    except Exception as err:
        print(err)
        return increment_status_code_counter(url, 500)
