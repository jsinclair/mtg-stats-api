import json
import os
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def main(event, context):
    try:
        request_body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({
                "message": "Request body must be valid JSON.",
            }),
        }

    response = table.update_item(
        Key={
            "pk": "counter",
            "sk": "global",
        },
        UpdateExpression="ADD #count :increment",
        ExpressionAttributeNames={
            "#count": "count",
        },
        ExpressionAttributeValues={
            ":increment": Decimal(1),
        },
        ReturnValues="ALL_NEW",
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "count": int(response["Attributes"]["count"]),
            "message": f"Hello, {request_body['username']}"
            if request_body.get("username")
            else "Counter incremented.",
        }),
    }
