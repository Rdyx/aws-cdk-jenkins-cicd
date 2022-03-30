import requests


def lambda_handler(event, context):
    try:
        r = requests.get("https://google.com")
        r.status_code
        return "ok"

    except:
        return "Error"
