import click

@click.command()
@click.option("--species", prompt="species", help="species")
@click.option("--chromosome", prompt="chromosome", help="chromosome")
@click.option("--datasource", prompt="Source data file", help="Source data file")
@click.option("--index", prompt="target index", help="target index")
@click.option("--linemod", prompt="python line processing", help="python line processing")
@click.option("--splitmod", prompt="python line splitting", help="python line splitting")
@click.option("--listmod", prompt="list mods joined back into line", help="list mods joined back into line")
@click.option("--idprefix", prompt="id prefix", help="id prefix")
@click.option("--outfile", prompt="output file", help="output file")


def esgen(datasource, index, linemod, splitmod, listmod, idprefix, outfile, species, chromosome):
    CREATE_LINE = '{ "create": { "_index": "__INDEX__", "_id": "__ID__" }}'
    DATA_LINE = '{ "id": "__ID__", "data": "__DATA__", "chromosome": "__CHROMOSOME__", "species": "__SPECIES__", "location": __LOCATION__}'
    n = 0
    location = 0
    with open(datasource, "r") as inFile:
        with open(outfile, "w") as outFile:
            for line in inFile:
                line = line.strip()
                line_location = str(location)
                location += len(line)
                n += 1
                id = idprefix + "_" + str(n)
                outFile.write(CREATE_LINE.replace("__INDEX__", index).replace("__ID__", id))
                outFile.write('\r\n')

                line = eval(linemod)
                data = eval(splitmod)
                line = " ".join(eval(listmod))
                outFile.write(DATA_LINE.replace("__ID__", id).
                              replace("__DATA__", line).
                              replace("__LOCATION__", line_location).
                              replace("__CHROMOSOME__", chromosome).replace("__SPECIES__", species))
                outFile.write('\r\n')

if __name__ == '__main__':
    esgen()
