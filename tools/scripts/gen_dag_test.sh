#!/bin/bash

# This script is for generating airflow dag test files
# Usage: from codebase root dir, run dataplatform/bash/gen_dag_tests.sh

# Note: build the docker or pull from gcr first
echo 'Docker build airflow_code image...'
docker build -f docker-airflow/Dockerfile.airflow_code -t airflow_code:running .

# Clean generated dag test
echo 'Cleaning generated dag test'
rm -rf pytest/airflow/dags/auto_generate_result/*

# Compose and wait for healthy webserver
echo 'Composing...'
#cd docker-airflow

docker-compose -f docker-airflow/docker-compose.yml -f docker-airflow/docker-compose-UnitTestGenerator.yml down -v
docker-compose -f docker-airflow/docker-compose.yml -f docker-airflow/docker-compose-UnitTestGenerator.yml up -d

until [[ "`docker inspect -f {{.State.Health.Status}} airflow_webserver`" == "healthy" ]]; do
    echo 'Waiting for webserver...'
    sleep 2;
done;

# Pass command to generate tests
echo 'Generating tests...'

docker exec -it airflow_webserver bash -c '$RUN_TEST'

if [[ -n "$1" ]]; then
    docker-compose -f docker-airflow/docker-compose.yml -f docker-airflow/docker-compose-UnitTestGenerator.yml down -v
fi