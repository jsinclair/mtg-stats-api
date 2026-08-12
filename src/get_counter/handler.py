import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def main(event, context):
    response = table.get_item(
        Key={
            "pk": "counter",
            "sk": "global",
        }
    )
    item = response.get("Item", {})

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "count": int(item.get("count", 0)),
        }),
    }
