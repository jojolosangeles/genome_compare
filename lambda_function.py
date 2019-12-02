import json
from search import search
from es_search import es_search
    
def lambda_handler(event, context):
    seq = event['seq']
    result = search(seq)
    return {
        'statusCode': 200,
        'body': result
    }

