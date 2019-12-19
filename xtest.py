from search import search_index
import click

@click.command()
@click.option("--offset", type=int, help="sequence to search for")
@click.option("--length", type=int, help="length of sequence to extract")
@click.option("--index", default="human_index2", help="name of index to search")
@click.option("--file", help="path to file with lines to search")

def search_es(offset, length, index, file):
    with open(file, "r") as inFile:
        inFile.seek(offset)
        seq = inFile.read(length)
    seq = seq.replace("GC", "G C").replace("CG", "C G")
    data = [val for val in seq.split() if len(val) > 3]
    seq = " ".join(data)
    result = search_index(seq, index)
    print(result)

if __name__ == "__main__":
    search_es()