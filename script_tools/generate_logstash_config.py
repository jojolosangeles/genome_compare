import sys
import os

template="""input {
  file {
    path => "/processed/*.processed"
    start_position => "beginning"
  }
}

filter {
  grok {
    match => { "message" => "%{WORD:sp} %{WORD:chr} %{NONNEGINT:dSO} %{NONNEGINT:dEO} %{NONNEGINT:loc} %{NONNEGINT:sEO} %{GREEDYDATA:data}" }
  }
  mutate {
    remove_field => [ "message" ]
  }
}

output {
  elasticsearch {
    hosts => ["__ELASTICSEARCH_URL__"]
    index => "__ELASTICSEARCH_INDEX__"
  }
}
"""

target_folder = sys.argv[1]
es_url = sys.argv[2]
es_index = sys.argv[3]

logstash_config = template.replace("__TARGET_FOLDER__", target_folder)
logstash_config = logstash_config.replace("__ELASTICSEARCH_URL__", es_url)
logstash_config = logstash_config.replace("__ELASTICSEARCH_INDEX__", es_index)

pipeline_path = f"{target_folder}/pipeline"
if not os.path.exists(pipeline_path):
    os.mkdir(pipeline_path)

with open(f"{target_folder}/pipeline/logstash.yml", 'w') as lsyml:
    lsyml.write('http.host: "0.0.0.0"\n')
    # xpack.monitoring.elasticsearch.hosts: ["http://elasticsearch:9200"]
    # lsyml.write("node.name=test_node\n")

with open(f"{target_folder}/pipeline/logstash.conf", "w") as lsconf:
    lsconf.write(logstash_config)
