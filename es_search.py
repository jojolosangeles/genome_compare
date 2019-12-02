from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, connections
from botocore.vendored import requests

def search(s):
    response = requests.get("http://885d447e.ngrok.io/")
    return response.json()
    # prepare to search
    # client = Elasticsearch(
    #     ['885d447e.ngrok.io'],#:443'],
    #     # turn on SSL
    #     #use_ssl=True
    # )
    # searcher = Search(index='human_index')[0:2].using(client).query("match", raw_data=s)
    # searcher.source(excludes=["raw_data"])
    # sresponse = searcher.execute()
    # print(f"search for  {s}")
    # response = []
    # for hit in searcher:
    #     response.append({ 'species': hit.species, 'chromosome': hit.chromosome, 'score': hit.meta.score })
    # return response
