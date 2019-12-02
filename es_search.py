from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, connections
import os

def es_search(s):
    #prepare to search
    connections.create_connection(hosts=[os.environ['ELASTICSEARCH_HOST']], timeout=20)
    client = Elasticsearch()
    searcher = Search(index='human_index')[0:2].using(client).query("match", raw_data=s)
    searcher.source(excludes=["raw_data"])
    sresponse = searcher.execute()
    print(f"search for  {s}")
    response = []
    for hit in searcher:
        response.append({ 'species': hit.species, 'chromosome': hit.chromosome, 'score': hit.meta.score })
    return response
