import json
from es_search import search
from botocore.vendored import requests

def lambda_handler(event, context):
    MIN_SEQ_LEN = 10
    print(json.dumps(event))
    result = requests.get("http://885d447e.ngrok.io/")
    # seq = event['seq']
    # n = len(seq)
    # print(f"n is {n}")
    # if n < MIN_SEQ_LEN:
    #     message = f"search sequence must have at least {MIN_SEQ_LEN} values, this one has {n} values"
    # else:
    #     result = search(seq)
    #     message = seq
    # result = {
    #     "message": message
    # }
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(result)
    }
