#!/usr/bin/env bash

## Path of the basedir of the app
BASE_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DOCKER_LOGS=$BASE_DIR/docker_logs

## Execution of the entire workflow inside a docker container and exporting results
mkdir -p $DOCKER_LOGS

echo $(date -u) "Building the application container image! ----- Please check the progress in the file ${DOCKER_LOGS}/docker_build.log"
docker build -t gl_env . >& ${DOCKER_LOGS}/docker_build_$(date +%F_%T).log

echo $(date -u) "Executing the application workflow inside the container! ----- Please check the progress in the file ${DOCKER_LOGS}/docker_run.log"
docker run --name=gl_prs_workflow gl_env >& ${DOCKER_LOGS}/docker_run_$(date +%F_%T).log

echo $(date -u) "Exporting the results from inside the container to the analysis directory! ----- Please check the results here: ${BASE_DIR}/workflow_results"
docker cp gl_prs_workflow:/home/gl_test/workflow_results ${BASE_DIR} >& ${DOCKER_LOGS}/docker_cp_$(date +%F_%T).log

echo $(date -u) "Cleaning up the house!!!"
docker rm gl_prs_workflow
docker rmi -f gl_env

echo $(date -u) "Yay! Enjoy your results. :D"