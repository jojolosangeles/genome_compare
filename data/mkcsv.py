import os
import json
import click

@click.command()
@click.option("--graph", type=bool, prompt="generate graph data?", help="generate graph data?")
@click.option("--species", prompt="species", help="species")
@click.option("--chromosome", prompt="chromosome", help="chromosome")
@click.option("--chromosome2", default="same")
@click.option("--count", type=bool, default=False)

def gen_data(graph, species, chromosome, chromosome2, count):
    files = [x for x in filter(lambda x: x.endswith('.json'), os.listdir('esdata'))]
    MIN_SCORE = 250

    if graph:
        print("x,y,x2,y2,color")
    else:
        print("sp,chr,loc,score,msp,mchr,mloc")

    def x2(s):
        if s == "2A" or s == "2B":
            return "2"
        else:
            return s

    def include_hit(chromosome, chromosome2, match_chromosome):
        if chromosome2 == "same":
            return x2(chromosome) == x2(match_chromosome)
        else:
            return match_chromosome == chromosome2
            
    def show_hit(chromosome2, species_y, species, chromosome, location, score, match_species, match_chromosome, match_location, reversed):
        score = int(float(score))
        location = int(int(location)/1000000)
        match_location = int(int(match_location)/1000000)
        color = "inversed" if reversed else "same orientation"
        if species != match_species and include_hit(chromosome, chromosome2, match_chromosome) and score > MIN_SCORE:
            if graph:
                print(f"{location},{species_y[species]},{match_location},{species_y[match_species]},{color}")
            else:
                print(f"{species},{chromosome},{location},{score},{match_species},{match_chromosome},{match_location},{color}")
        # if species != match_species and x2(chromosome) != x2(match_chromosome) and score > MIN_SCORE:
        #     if graph:
        #         print(f"species {match_species}, chromosome {match_chromosome}")
        #         print(f"{location},{species_y[species]},{match_location},100,{color}")

    def above(species):
        if species == "human":
            return "gorilla"
        elif species == "chimp":
            return "human"
        else:
            return "chimp"

    def below(species):
        if species == "human":
            return "chimp"
        elif species == "chimp":
            return "gorilla"
        else:
            return "human"

    check_species = species
    check_chromosome = chromosome
    species_y = {}
    species_y[check_species] = 200
    species_y[above(check_species)] = 400
    species_y[below(check_species)] = 0

    def chk_chromo(check_chromosome, chromosome):
        if check_chromosome == "ALL":
            return True
        else:
            return check_chromosome == chromosome

    counts = {}
    for file in files:
        data = file.split(".")[0].split("_")
        species,chromosome,location = data[-3:]
        reversed = len(data) == 4
        if species == check_species and chk_chromo(check_chromosome, chromosome):
            data = json.loads(open(f"esdata/{file}", "r").read())
            if 'hits' in data:
                hits = data['hits']['hits']
                for hit in hits:
                    if count:
                        if int(float(hit['_score'])) > MIN_SCORE:
                            match_key = f"{hit['_source']['species']}_{hit['_source']['chromosome']}"
                            counts[match_key] = counts.get(match_key, 0) + 1
                    else:
                        show_hit(chromosome2, species_y, species,chromosome,location,hit['_score'], hit['_source']['species'], hit['_source']['chromosome'], hit['_source']['location'], reversed)
    if count:
        for x in counts:
            print(f"{check_species},{check_chromosome},{x},{counts[x]}")

if __name__ == "__main__":
    gen_data()