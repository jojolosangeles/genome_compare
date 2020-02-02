import json
import requests

class ES_Search:
    MUST_NOT = '"must_not": { "match": { "FIELD": "VALUE" }}'
    MUST = '"must": { "match": { "FIELD": "VALUE" }}'
    RANGE = '"filter": { "range": { "FIELD": { OPVAL_LIST }}}'
    QUERY = '{ "_source": { "excludes": ["data", "message"] }, "query": { "bool": { BOOL_QUERY }}}'

    def __init__(self, index):
        self.index = index

    def qline(self, line):
        line = line.strip()
        _isnot = line.find(" is not ") > 0
        _is = line.find(" is ") > 0
        _gte = line.find(" >= ") > 0
        _lte = line.find(" <= ") > 0
        _gt = line.find(" > ") > 0
        _lt = line.find(" < ") > 0
        if _isnot:
            data = line.split()
            return ES_Search.MUST_NOT.replace("FIELD", data[0]).replace("VALUE", data[3])
        elif _is:
            data = line.split()
            return ES_Search.MUST.replace("FIELD", data[0]).replace("VALUE", " ".join(data[2:]))
        elif _gte or _lte or _gt or _lt:
            data = line.split()
            opvals = []
            offset = 1
            while offset < len(data):
                if data[offset] == ">=":
                    opvals.append(f"\"gte\": {data[offset + 1]}")
                elif data[offset] == "<=":
                    opvals.append(f"\"lte\": {data[offset + 1]}")
                elif data[offset] == ">":
                    opvals.append(f"\"gt\": {data[offset + 1]}")
                elif data[offset] == "<":
                    opvals.append(f"\"lt\": {data[offset + 1]}")
                offset += 2
            return ES_Search.RANGE.replace("FIELD", data[0]).replace("OPVAL_LIST", ",".join(opvals))

    def query(self, lines):
        qlines = [ self.qline(line) for line in lines if line[0] != '#']
        if len(qlines) > 0:
            esquery = ES_Search.QUERY.replace("BOOL_QUERY", ",".join(qlines))
            #print(esquery)
            response = requests.get(f"http://localhost:9200/{self.index}/_search",
                                    data=esquery,
                                    headers={'content-type':'application/json'}
                                    )
            print(response.text)
