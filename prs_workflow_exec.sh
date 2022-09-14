#!/usr/bin/env bash

## Path of the source datasets
BASE_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
USERS=$BASE_DIR/datasets/user_ids.tsv
MODEL_A=$BASE_DIR/datasets/model_a.tsv
MODEL_B=$BASE_DIR/datasets/model_b.tsv

## Output files and directory
OUTDIR=$BASE_DIR/workflow_results
mkdir -p $OUTDIR
RESULTS=$OUTDIR/prs_analysis_data.csv

## Running the entire cohort PRS workflow
echo $(date -u) "PRS workflow started! ----- Please check the docker_logs directory for progress details."
python3 $BASE_DIR/src/cohort_prs.py --out $RESULTS $USERS $MODEL_A $MODEL_B
echo $(date -u) "PRS workflow finished successfully!"