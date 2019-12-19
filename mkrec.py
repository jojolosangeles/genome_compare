import click
import os

TEMPLATE_LINE="python req.py --query query_search.json --data FILE --offset OFFSET --len LEN  --index INDEX --linemod \"line.replace('CG', 'C G').replace('GC', 'G C')\" --splitmod \"line.split()\" --listmod \"[val for val in data if len(val) > 3]\""
ECHO_LINE="echo 'FILE OFFSET' >> outFile.txt"
@click.command()
@click.option("--file", prompt="data file", help="data file")
@click.option("--len", type=int, prompt="length of data to extract", help="length of data to extract")
@click.option("--index", prompt="target index", help="target index")

def mklines(file, len, index):
    fileLength = os.stat(file).st_size
    offset = 0
    print("rm outFile.txt")
    print("touch outFile.txt")
    while offset < fileLength:
        print(ECHO_LINE.replace("FILE", file).replace("OFFSET", str(offset)))
        print(TEMPLATE_LINE.replace("FILE", file).replace("OFFSET", str(offset)).replace("LEN", str(len)).replace("INDEX", index) + " >> outFile.txt")
        offset += len

if __name__ == "__main__":
    mklines()
