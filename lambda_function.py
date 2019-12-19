from search import search
    
def lambda_handler(event, context):
    seq = event['seq']
    result = search(seq)
    return {
        'statusCode': 200,
        'body': result
    }

