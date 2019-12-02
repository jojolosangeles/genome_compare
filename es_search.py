from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, connections

def search(s):
    # set up connections
    connections.create_connection(alias='local_connection', hosts=['localhost'], timeout=60)
    connections.create_connection(alias='remote_connection', hosts=['885d447e.ngrok.io'], timeout=60)
    connectionName = 'remote_connection'

    # prepare to search
    client = Elasticsearch()
    searcher = Search(using=connectionName, index='human_index')[0:2].using(client).query("match", raw_data=s)
    sresponse = searcher.execute()
    print(f"search for  {s}")
    response = []
    for hit in searcher:
        response.append({ 'species': hit.species, 'chromosome': hit.chromosome, 'score': hit.meta.score })
    return response
