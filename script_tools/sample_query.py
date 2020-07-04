import click
import json
import requests


@click.command()
@click.option("--query", prompt="Input query file", help="Input query file")
@click.option("--index", prompt="target index", help="target index")
@click.option("--esurl", prompt="Elasticsearch URL", help="Elasticsearch URL")
def doquery(esurl, query, index):
    MUST_NOT = '"must_not": { "match": { "FIELD": "VALUE" }}'
    MUST = '"must": { "match": { "FIELD": "VALUE" }}'
    RANGE = '"filter": { "range": { "FIELD": { OPVAL_LIST }}}'
    QUERY = '{ "_source": { "excludes": ["data", "message"] }, "query": { "bool": { BOOL_QUERY }}}'

    def qline(line):
        line = line.strip()
        _isnot = line.find(" is not ") > 0
        _is = line.find(" is ") > 0
        _gte = line.find(" >= ") > 0
        _lte = line.find(" <= ") > 0
        _gt = line.find(" > ") > 0
        _lt = line.find(" < ") > 0
        if _isnot:
            data = line.split()
            return MUST_NOT.replace("FIELD", data[0]).replace("VALUE", data[3])
        elif _is:
            data = line.split()
            return MUST.replace("FIELD", data[0]).replace("VALUE", " ".join(data[2:]))
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
            return RANGE.replace("FIELD", data[0]).replace("OPVAL_LIST", ",".join(opvals))

    with open(query) as q:
        for line in q:
            if len(line) > 100:
                (species, chromosome, source_file_start_offset, source_file_end_offset, segment_start_offset,
                 segment_end_offset, orientation, data) = line.rstrip().split(' ', maxsplit=7)
                qline = MUST.replace("FIELD", "data").replace("VALUE", data)
                # human X 151 1014436 0 1000000 True TGGTGAAACCTC ACAG..
                # 0     1 2   3       4 5       6    7:
                esquery = QUERY.replace("BOOL_QUERY", qline)
                # print(esquery)
                response = requests.get(f"{esurl}/{index}/_search",
                                        data=esquery,
                                        headers={'content-type': 'application/json'}
                                        )
                es_response = json.loads(response.text)
                for x in es_response:
                    if x == 'hits':
                        for y in es_response['hits']['hits']:
                            score = int(y['_score'])
                            msp = y['_source']['sp']
                            mchr = y['_source']['chr']
                            mloc = int(y['_source']['segloc'])
                            seg_size = int(y['_source']['sEO']) - mloc
                            dsSO = y['_source']['dSO']
                            dsEO = y['_source']['dEO']
                            print(
                                f"{species},{chromosome},{segment_start_offset},{score},{msp},{mchr},{mloc},{orientation},{seg_size},{dsSO},{dsEO}")
                # print(response.text)


if __name__ == "__main__":
    doquery()
