#!/bin/bash
i=0
while true; do
  ((i=i+1))
  if curl --fail $1; then
    echo "Elasticsearch has started"
    break
  fi;
  sleep 5
  echo "waiting for Elasticsearch to start, try #$i..."
done
