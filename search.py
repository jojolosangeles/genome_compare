from botocore.vendored import requests

def search(s):
    result = requests.get("http://885d447e.ngrok.io/human_index/_search?q=raw_data:ACGT&_source_excludes=raw_data")
    return result.json()
