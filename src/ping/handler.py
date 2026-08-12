import json

def main(event, context):
    statusCode = 200
    res = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'pong'
        })
    }
    return res
