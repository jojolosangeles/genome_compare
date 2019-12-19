lines = open("files.txt", "r").readlines()

def extractSpecies(line):
  ptr = line.find("ptr") > 0
  gor = line.find("orilla") > 0
  hum = line.find("huref") > 0
  if hum:
    return "human"
  elif gor:
    return "gorilla"
  else:
    return "chimp"

for line in lines:
  line = line.strip()
  species = extractSpecies(line)
  chromo = line.split(".")[-2].split("_chr")[1]
  print(species, chromo, line)
