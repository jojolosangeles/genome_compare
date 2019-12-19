#922  python xq.py --species chimp --chromosome 6 --offset 51000000 --length 10000 > x1.txt
#  923  python ../jjquery.py --query x1.txt --index cgh_genomes | jq . | grep -E 'species|chromosome|location'

print("set -x")
target_index = "cgh_genomes"

with open("dataSizes.txt", "r") as inFile:
    lines = inFile.readlines()
    for line in lines:
        line = line.strip()
        number_checks =  int(int(line.split()[4])/1000000) + 1
        data = line.split()
        filePath = data[-1]
        filename = filePath.split("/")[-1]
        species_chromosome = filename.split(".")[0]
        species = species_chromosome.split("_")[0]
        chromosome = species_chromosome.split("_")[1]
        for x in range(number_checks):
            location = x * 1000000
            print(f"python xq.py --species {species} --chromosome {chromosome} --offset {location} --length 10000 > x1.txt")
            print(f"python ../jjquery.py --query x1.txt --index {target_index} > esdata/{species}_{chromosome}_{location}.json")
            print(f"python xqr.py --species {species} --chromosome {chromosome} --offset {location} --length 10000 > x1.txt")
            print(f"python ../jjquery.py --query x1.txt --index {target_index} > esdata/r_{species}_{chromosome}_{location}.json")