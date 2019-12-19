lines = open("files2.txt", "r").readlines()
LINE_GEN = "python ../line_gen.py --datasource FILEPATH --linelen 1000000 --outfile esdata/SPECIES_CHROMOSOME.1m --filter \"len(line) == 0 or line[0] == '>'\""
ES_GEN = "python ../esgen.py --datasource esdata/SPECIES_CHROMOSOME.1m --chromosome CHROMOSOME --species SPECIES --index cgh_genomes --linemod \"line.replace('CG', 'C G').replace('GC', 'G C').replace('AT', 'A T').replace('TA', 'T A').replace('N', '')\" --splitmod \"line.split()\" --listmod \"[val for val in data if len(val) > 5]\" --idprefix SPECIES_CHROMOSOME --outfile esdata/SPECIES_CHROMOSOME.1m.es_bulk"
MK50 = "python ../mk50.py esdata/SPECIES_CHROMOSOME.1m.es_bulk"

print("set -x")
for line in lines:
  line = line.strip()
  species,chromosome,filepath = line.split()
  print(LINE_GEN.replace("FILEPATH", filepath).replace("SPECIES", species).replace("CHROMOSOME", chromosome))
  print(ES_GEN.replace("SPECIES", species).replace("CHROMOSOME", chromosome))
  print(MK50.replace("SPECIES", species).replace("CHROMOSOME", chromosome))
