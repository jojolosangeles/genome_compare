lines = open("files2.txt", "r").readlines()
for line in lines:
    species, chromosome, filePath = line.strip().split()
    print(f"python processing.py {species} {chromosome} {filePath} 200000 8 > cgh_200000/{species}.{chromosome}.processed")
