import json
from es_search import search

def lambda_handler(event, context):
    MIN_SEQ_LEN = 10
    seq = event['path'].split("/")[-1]
    print(event['path'])
    n = len(seq)
    print(f"n is {n}")
    if n < MIN_SEQ_LEN:
        message = f"search sequence must have at least {MIN_SEQ_LEN} values, this one has {n} values"
    else:
        result = search(seq)
        message = seq
    result = {
        "message": message
    }
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(result)
    }
