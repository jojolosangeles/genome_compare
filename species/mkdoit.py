import click

from collections import defaultdict

@click.command()
@click.option("--files",
              help="text file with list of files to processes, each line with <species> <chromosome> <filePath>")
@click.option("--segsize", help="segment size", type=int)
@click.option("--wordlen", help="minimum word length", type=int)
@click.option("--targetfolder", help="path to results folder")
@click.option("--targetindex", help="elasticsearch index to store results")
@click.option("--samplesizepercent", help="percent of segment to use as a sample")
@click.option("--numbersamples",
              help="number of samples to generate, doubled because reverse complement samples also generated")

def gen_script(files, segsize, wordlen, targetfolder, targetindex, samplesizepercent, numbersamples):
    lines = open(files, "r").readlines()
    print("set -x")
    print(f"echo 'creating logstash config file: logstash_{targetindex}.conf'")
    s = f"{targetfolder}".replace("/", "\\/")
    mkLogstash = f"sed -e \"s/__TARGET_FOLDER__/{s}/\" ../data/config/logstash_to_es.conf.template"
    conf_file = f"{targetfolder}/logstash_{targetindex}.conf"
    print(f"{mkLogstash} > {conf_file}x")
    mkLogstash = f"sed -e \"s/__ELASTICSEARCH_INDEX__/{targetindex}/\" {targetfolder}/logstash_{targetindex}.confx"
    print(f"{mkLogstash} > {conf_file}")
    # TODO: this is specific to my installation!  need this for repeated tests
    logstash_start_script = f"{targetfolder}/start_logstash_{targetindex}"
    print(f"mkdir -p {targetfolder}")
    print(
        f"echo 'rm /usr/local/Cellar/logstash/7.4.2/libexec/data/plugins/inputs/file/.sincedb*' > {logstash_start_script}")
    print(f"echo 'logstash -f {conf_file} &' > {logstash_start_script}")
    print(f"chmod +x {logstash_start_script}")
    print(f"read -p 'STOP LOGSTASH NOW!  then press ENTER'")
    print(f"{logstash_start_script}")

    speciesSet = set()

    for line in lines:
        species, chromosome, filePath = line.strip().split()
        speciesSet.add(species)
        print(
            f"python processing.py {species} {chromosome} {filePath} {segsize} {wordlen} {targetfolder} {samplesizepercent} {numbersamples}")

    # these are check against elasticsearch record counts (once logstash has loaded those -- how can we tell it is done?)
    for species in speciesSet:
        print(f"cat {targetfolder}/{species}.*.processed | wc > {targetfolder}/{species}.line_count")
    #
    # TODO: verify count against elasticsearch before sampling
    # maybe at this point, we query elasticsearch, waiting for now records to be inserted, then
    # counting
    #count = defaultdict(int)
    #elasticsearch = ElasticSearcher(index)
    #for species in speciesSet:
    #    count[species] = elasticsearch.count({'sp': species})
    print("sleep 60")

    # sample queries go out to a CSV
    for line in lines:
        species, chromosome, filePath = line.strip().split()
        sampleFilePath = f"{targetfolder}/{species}.{chromosome}.{segsize}.{wordlen}.samples"
        # print(f"echo 'sp,chr,loc,score,msp,mchr,mloc,orientation' > {sampleFilePath}.csv")
        print(f"python sample_query.py --query {sampleFilePath} --index {targetindex} >> {sampleFilePath}.csv")

    # put all result in single CSV
    resultsFile = f"{targetfolder}/data.csv"
    print(f"echo 'sp,chr,sloc,score,msp,mchr,mloc,orientation,segsize,dsSO,dsEO' > {resultsFile}")
    print(f"cat {targetfolder}/*.samples.csv >> {resultsFile}")

#
#  Cases tested:
#
#    python mkdoit.py --files ~/genomes/graph_data/cgh_files.txt --segsize 1000000 --wordlen 10 --targetfolder ~/genomes/graph_data/1m --targetindex cgh_1m --samplesizepercent 10 --numbersamples 3 > doit
#    python mkdoit.py --files ~/genomes/graph_data/cgh_files.txt --segsize 100000 --wordlen 12 --targetfolder ~/genomes/graph_data/1h --targetindex cgh_1h --samplesizepercent 10 --numbersamples 2 > doit
#    python mkdoit.py --files ~/genomes/graph_data/cgh_files.txt --segsize 500000 --wordlen 19 --targetfolder ~/genomes/graph_data/5h --targetindex cgh_5h --samplesizepercent 10 --numbersamples 2 > doit
#
if __name__ == "__main__":
    gen_script()
