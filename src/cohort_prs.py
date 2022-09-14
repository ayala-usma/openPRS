#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By: David Aurelia Ayala Usma
# Created Date: 2022-09-13
# Version = 0.0.1
# ---------------------------------------------------------------------------

## Description
"""Main module to calculate two Polygenic Risk Score models for several individuals"""

# ---------------------------------------------------------------------------
## Required libraries
import os
import sys
import argparse
import numpy as np
import requests as rq
from datetime import datetime
from timeit import default_timer as timer

## Parallelized pandas
os.environ["MODIN_ENGINE"] = "ray"
import ray
ray.init()
#ray.init(_plasma_directory = '/tmp')
import modin.pandas as pd

# ---------------------------------------------------------------------------
## Importing the individual PRS module
import individual_prs as prs

# ---------------------------------------------------------------------------
## Main function

def main():

    ## Parsing command line arguments
    parser = argparse.ArgumentParser(description='This package calculates the PRS scores for a condition in different individuals under different provided models. It also summarizes the data for analysis.')
    parser.add_argument('user_data', type=str, nargs=1,
                    help="""File containing a table with two columns. The first column describes presence or absence of the condition in an individual. 
                      The second one is an OpenSNP file id that references the genotype of an individual for download.""")
    parser.add_argument('prs_model', type=str, nargs='+',
                    help="""File containing a table with two columns describing the PRS model coefficients. The first column contains the variants identifiers (rsIDs) considered in the model. 
                    The second column contains the weights (beta coefficients) of each variant. Multiple models can be specified.""")
    
    args = parser.parse_args()
    
    ## Reading the PRS models data 
    t_start = timer()

    models = {}
    for model_path in args.prs_model:
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        models[model_name] = pd.read_csv(model_path, sep='\t')

    t_end = timer()
    print("[{timestamp}]: Data from the PRS models successfully loaded! ----- Time elapsed (s): {time}".format(timestamp=datetime.now(), time=(t_end - t_start)))

    ## Obtaining the major (non-effect) allele for the variants considered in each model
    t_step = timer()

    models_alleles = {k: prs.get_major_alleles_model(v) for k, v in models.items()}
    del models

    t_end = timer()
    print("[{timestamp}]: Major (non-effect) alleles successfully recovered! ----- Time elapsed (s): {time}".format(timestamp=datetime.now(), time=(t_end - t_step)))

    ## Reading the list of genotyped users and conditions to evaluate
    t_step = timer()

    indiv_data = pd.read_csv(args.user_data[0], sep='\t', comment='#')

    t_end = timer()
    print("[{timestamp}]: List of individuals' OpenSNP IDs and conditions successfully loaded! ----- Time elapsed (s): {time}".format(timestamp=datetime.now(), time=(t_end - t_step)))

    ## Obtaining the genotypes of all the individuals
    t_step = timer()

    def parallel_retrieval_genotypes(user_series):
        user_id = user_series['file_link']
        genotype_individual = prs.get_genotype_individual(user_id)
        return genotype_individual
        
    users_genotypes = indiv_data.apply(lambda x: parallel_retrieval_genotypes(x), axis=1)
    users_genotypes = users_genotypes.set_axis(indiv_data['file_link'])

    t_end = timer()
    print("[{timestamp}]: Genotype data of individuals successfully retrieved from OpenSNP! ----- Time elapsed (s): {time}".format(timestamp=datetime.now(), time=(t_end - t_step)))

    ## Merge genotypes with the models and store them in a dictionary and calculating the PRS by individual per model
    t_step = timer()

    prs_scores_dict = {}
    for name, model in models_alleles.items():
        prs_scores_dict[name] = users_genotypes.apply(lambda x: prs.calculating_prs_individual(prs.merge_allelic_data(x, model)), axis=1)
        t_end = timer()
        print("[{timestamp}]: Cohort PRS for {model_name} successfully calculated! ----- Time elapsed (s): {time}".format(timestamp=datetime.now(), model_name=name, time=(t_end - t_step)))

    ## Producing the final dataset with individuals, condition, and PRS scores per model
    t_step = timer()

    for model, prs_score in prs_scores_dict.items():
        column = prs_score.to_frame().reset_index()
        column.columns = ['file_link', 'PRS_{model}'.format(model=model)]
        indiv_data = indiv_data.merge(column, on='file_link', how='inner')
    
    t_end = timer()
    print("[{timestamp}]: PRSs of the cohort for all models successfully calculated! ----- Time elapsed (s): {time}".format(timestamp=datetime.now(), time=(t_end - t_step)))

    return indiv_data

# ---------------------------------------------------------------------------
## Boilerplate for command line execution of main function for testing
if __name__ == '__main__':
    t_prs_start = timer()
    print("[{timestamp}]: Cohort PRS calculator started!!!".format(timestamp=datetime.now()))
    main()
    t_prs_end = timer()
    print("[{timestamp}]: Workflow finished, bye! ----- Runtime of the workflow(s): {time}".format(timestamp=datetime.now(), time=(t_prs_end - t_prs_start)))