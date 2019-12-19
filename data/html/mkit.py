import os
import json
import click

@click.command()
@click.option("--left", help="left column label")
@click.option("--middle", help="middle column label")
@click.option("--right", help="right column label")
@click.option("--datafile", help="path to data file")
@click.option("--outfile", help="output html file")

def gen_data(left, middle, right, datafile, outfile):
    lines = open(datafile, "r").readlines()

    templateLines = open("plotly.template.html", "r").readlines()
    with open(outfile, "w") as outFile:
        for line in templateLines:
            line = line.replace("LEFT", left).replace("MIDDLE", middle).replace("RIGHT", right)
            outFile.write(line)

if __name__ == "__main__":
    gen_data()
