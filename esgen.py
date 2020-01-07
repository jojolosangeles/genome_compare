import click
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

#
#  Generate bulk load file format
#
@click.command()
@click.option("--species", prompt="species", help="species")
@click.option("--chromosome", prompt="chromosome", help="chromosome")
@click.option("--datasource", prompt="Source data file", help="Source data file")
@click.option("--index", prompt="target index", help="target index")
@click.option("--processing-config", help="python line, split, list processing configuration")
@click.option("--idprefix", prompt="id prefix", help="id prefix")
@click.option("--outfile", prompt="output file", help="output file")


def esgen(datasource, index, processing_config, idprefix, outfile, species, chromosome):
    CREATE_LINE = '{ "create": { "_index": "__INDEX__", "_id": "__ID__" }}'
    DATA_LINE = '{ "id": "__ID__", "data": "__DATA__", "chromosome": "__CHROMOSOME__", "species": "__SPECIES__", "location": __LOCATION__}'
    n = 0
    location = 0
    code = open(processing_config).readlines()

    def recode(codeline):
        data = codeline.split()
        code_segment = []
        while len(data) >= 2:
            if data[0] == "SPLIT":
                split_sections = data[1].split(",")
                for x in split_sections:
                    code_segment.append(f"replace('{x}', '{x[0]} {x[1]}')")
            elif data[0] == "REMOVE":
                remove_data = data[1].split(",")
                for x in remove_data:
                    code_segment.append(f"replace('{x}', '')")
            elif data[0] == "CODE":
                offset = int(data[1])
                code_segment.append(f"dcode({offset})")
            else:
                return codeline
            data = data[2:]

        return f"line.{'.'.join(code_segment)}"

    def token_recode(codeline):
        data = codeline.split()
        if data[0] == "TOKENS":
            return f"[val for val in data if len(val) {data[1]}]"
        else:
            return codeline


    class decodeable(str):
        def __init__(self, s):
            self.s = s

        def dcode(self, offset):
            coding_dna = Seq(self.s[offset:], generic_dna)
            s = coding_dna.translate()
            return ''.join(list(s))

    linemod = recode(code[0])
    splitmod = code[1]
    listmod = token_recode(code[2])
    with open(datasource, "r") as inFile:
        with open(outfile, "w") as processedLines:
            for line in inFile:
                line = line.strip()
                line_location = str(location)
                location += len(line)
                n += 1
                id = idprefix + "_" + str(n)

                line = decodeable(line)
                line = eval(linemod)
                data = eval(splitmod)
                line = f"{species} {chromosome} {location} " + " ".join(eval(listmod))
                processedLines.write(line)
                processedLines.write("\n")

if __name__ == '__main__':
    esgen()
