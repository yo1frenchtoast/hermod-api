#!/bin/bash

echo "****************** BUILD ******************"

docker-compose build

echo "****************** PUSH *******************"

docker-compose push

echo "****************** DEPLOY *****************"

docker stack deploy --compose-file docker-compose.yml hermod-api

echo "****************** END ********************"
