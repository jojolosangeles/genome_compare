from botocore.vendored import requests
import os

def search(s):
    host = os.environ['ELASTICSEARCH_HOST']
    q2 = f"http://{host}/human_index/_search?q=raw_data:{s}&_source_excludes=raw_data"
    result = requests.get(q2)
    return result.json()
