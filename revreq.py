import requests
import click
import json

@click.command()
@click.option("--query", prompt="query template", help="query template file")
@click.option("--data", prompt="data file to use in query", help="data file to use in query")
@click.option("--len", type=int, prompt="length of data to extract", help="length of data to extract")
@click.option("--offset", type=int, prompt="offset of data to extract", help="offset of data to extract")
@click.option("--index", prompt="target index", help="target index")
@click.option("--linemod", prompt="python line processing", help="python line processing")
@click.option("--splitmod", prompt="python line splitting", help="python line splitting")
@click.option("--listmod", prompt="list mods joined back into line", help="list mods joined back into line")

def doquery(query, data, len, offset, index, linemod, splitmod, listmod):
    def comp(val):
        if val == 'A':
            return 'T'
        elif val == 'C':
            return 'G'
        elif val == 'G':
            return 'C'
        else:
            return 'A'

    def revcomp(s):
        l = [comp(v) for v in s]
        return "".join(l)

    with open(query) as fh:
        with open(data, "r") as dataFile:
            dataFile.seek(offset)
            line = dataFile.read(len)
            line = revcomp(line)
            line = eval(linemod)
            data = eval(splitmod)
            queryData = " ".join(eval(listmod))
        query = fh.read().replace("DATA", queryData)
        response = requests.get(f"http://localhost:9200/{index}/_search",
                                data=query,
                                headers={'content-type':'application/json'}
                                )
        obj = json.loads(response.text)
        count = 0
        for x in obj['hits']['hits']:
            location = x['_source']['location']
            score = x['_score']
            print(f"{location}, {score}")
            count += 1
            if count >= 2:
                break

if __name__ == "__main__":
    doquery()
