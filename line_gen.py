import click
import gzip

@click.command()
@click.option("--datasource", prompt="Source data file", help="Source data file")
@click.option("--linelen", prompt="Line length", type=int, help="Line length")
@click.option("--outfile", prompt="Output file", help="Output file")
@click.option("--filter", prompt="Code that filters line", help="Code that filters line")


def linegen(datasource, outfile, linelen, filter):
    def open_datasource(datasource):
        ext = datasource.split(".")[-1]
        if ext == "gz":
            return gzip.open(datasource, "rt")
        else:
            return open(datasource, "r")

    with open_datasource(datasource) as inFile:
        with open(outfile, "w") as outFile:
            buffer = ""
            for line in inFile:
                line = line.strip()
                if not eval(filter):
                    buffer += line
                    while len(buffer) > linelen:
                        outFile.write(buffer[:linelen])
                        outFile.write('\n')
                        buffer = buffer[linelen:]
            outFile.write(buffer)
            outFile.write('\n')

if __name__ == '__main__':
    linegen()