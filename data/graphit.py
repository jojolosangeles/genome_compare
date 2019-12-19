lines = open("data.csv", "r").readlines()

SCORE_THRESHOLD = 500

def pval(species, chromosome, location, score, target_species, target_chromosome, target_location):
    location = int(int(location)/1000000)
    score = int(float(score))
    target_location = int(int(target_location)/1000000)
    #print(f"pval {species},{chromosome}, {location}, {score}, {score > SCORE_THRESHOLD}")
    if species != target_species or chromosome != target_chromosome or location != target_location:
        if score > SCORE_THRESHOLD:
            print(f"{species}.{chromosome}.{location:03d},{target_species}.{target_chromosome}.{target_location:03d}")

for line in lines:
    line = line.strip()
    data = line.split(",")
    species,chromosome,location,sc1,sp1,chr1,loc1,sc2,sp2,chr2,loc2,sc3,sp3,chr3,loc3 = data

    pval(species, chromosome, location, sc1, sp1, chr1, loc1)
    pval(species, chromosome, location, sc2, sp2, chr2, loc2)
    pval(species, chromosome, location, sc3, sp3, chr3, loc3)

