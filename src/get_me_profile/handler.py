import json
import os

import boto3


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def _claims_from(event):
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
    )


def main(event, context):
    claims = _claims_from(event)
    user_id = claims.get("sub")

    if not user_id:
        return _response(
            401,
            {
                "message": "Authenticated user claims were not found.",
            },
        )

    player_key = f"p#{user_id}"
    response = table.get_item(
        Key={
            "pk": player_key,
            "sk": "profile",
        },
    )

    item = response.get("Item")
    profile = None
    if item:
        profile = {
            "handle": item.get("handle"),
            "displayName": item.get("displayName"),
            "createdAt": item.get("createdAt"),
            "updatedAt": item.get("updatedAt"),
        }

    return _response(
        200,
        {
            "userId": user_id,
            "playerKey": player_key,
            "email": claims.get("email"),
            "emailVerified": claims.get("email_verified") == "true",
            "profile": profile,
        },
    )
