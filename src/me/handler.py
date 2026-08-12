import json


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def main(event, context):
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
    )

    user_id = claims.get("sub")
    if not user_id:
        return _response(
            401,
            {
                "message": "Authenticated user claims were not found.",
            },
        )

    return _response(
        200,
        {
            "userId": user_id,
            "playerKey": f"p#{user_id}",
            "email": claims.get("email"),
            "emailVerified": claims.get("email_verified") == "true",
            "username": claims.get("cognito:username"),
        },
    )
