import json
import os
from datetime import datetime, timezone

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


def _parse_body(event):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return None, "Request body must be valid JSON."

    if not isinstance(body, dict):
        return None, "Request body must be a JSON object."

    return body, None


def _clean_optional_string(value, field_name, max_length):
    if value is None:
        return None, None

    if not isinstance(value, str):
        return None, f"{field_name} must be a string."

    cleaned = value.strip()
    if not cleaned:
        return None, f"{field_name} cannot be empty."

    if len(cleaned) > max_length:
        return None, f"{field_name} must be {max_length} characters or fewer."

    return cleaned, None


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

    body, error = _parse_body(event)
    if error:
        return _response(400, {"message": error})

    handle, error = _clean_optional_string(body.get("handle"), "handle", 32)
    if error:
        return _response(400, {"message": error})

    display_name, error = _clean_optional_string(
        body.get("displayName"),
        "displayName",
        80,
    )
    if error:
        return _response(400, {"message": error})

    if handle is None and display_name is None:
        return _response(
            400,
            {
                "message": "Request body must include handle or displayName.",
            },
        )

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    player_key = f"p#{user_id}"

    update_expression_parts = [
        "updatedAt = :updatedAt",
        "createdAt = if_not_exists(createdAt, :createdAt)",
        "userId = :userId",
        "playerKey = :playerKey",
    ]
    expression_values = {
        ":updatedAt": now,
        ":createdAt": now,
        ":userId": user_id,
        ":playerKey": player_key,
    }

    if handle is not None:
        update_expression_parts.append("handle = :handle")
        expression_values[":handle"] = handle

    if display_name is not None:
        update_expression_parts.append("displayName = :displayName")
        expression_values[":displayName"] = display_name

    response = table.update_item(
        Key={
            "pk": player_key,
            "sk": "profile",
        },
        UpdateExpression=f"SET {', '.join(update_expression_parts)}",
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW",
    )

    item = response["Attributes"]
    return _response(
        200,
        {
            "userId": user_id,
            "playerKey": player_key,
            "email": claims.get("email"),
            "emailVerified": claims.get("email_verified") == "true",
            "profile": {
                "handle": item.get("handle"),
                "displayName": item.get("displayName"),
                "createdAt": item.get("createdAt"),
                "updatedAt": item.get("updatedAt"),
            },
        },
    )
