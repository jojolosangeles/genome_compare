import json
from search import search
    
def lambda_handler(event, context):
    result = search("ha") #requests.get("http://885d447e.ngrok.io/")
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

