import os
import json
import click


@click.command()
@click.option("--target-folder", help="folder with json search results")

def gen_data(target_folder):
    files = [x for x in filter(lambda x: x.endswith('.json'), os.listdir(target_folder))]
    MIN_SCORE = 250

    print("sp,chr,loc,score,msp,mchr,mloc,orientation")

    def show_hit(species, chromosome, location, score, match_species, match_chromosome,
                 match_location, reversed):
        score = int(float(score))
        if score > MIN_SCORE and (species != match_species or chromosome != match_chromosome):
            orientation = "inversed" if reversed else "same orientation"
            print(f"{species},{chromosome},{location},{score},{match_species},{match_chromosome},{match_location},{orientation}")

    for file in files:
        data = file.split(".")
        species, chromosome, location = data[:3]
        search_data = json.loads(open(f"{target_folder}/{file}", "r").read())
        reversed = file.find("revcomp") != -1
        if 'hits' in search_data:
            hits = search_data['hits']['hits']
            for hit in hits:
                show_hit(species, chromosome, location, hit['_score'],
                         hit['_source']['sp'], hit['_source']['chr'], hit['_source']['loc'],
                         reversed)


if __name__ == "__main__":
    gen_data()