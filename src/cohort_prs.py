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

## Parallelized pandas
os.environ["MODIN_ENGINE"] = "ray"
import ray
#ray.init(runtime_env={'env_vars': {'__MODIN_AUTOIMPORT_PANDAS__': '1'}})
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
    models = {}
    for model_path in args.prs_model:
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        models[model_name] = pd.read_csv(model_path, sep='\t')

    ## Obtaining the major (non-effect) allele for the variants considered in each model
    models_alleles = {k: prs.get_major_alleles_model(v) for k, v in models.items()}
    del models

    ## Reading the list of genotyped users and conditions to evaluate
    indiv_data = pd.read_csv(args.user_data[0], sep='\t', comment='#')

    ## Obtaining the genotypes of all the individuals
    def parallel_retrieval_genotypes(user_series):
        user_id = user_series['file_link']
        genotype_individual = prs.get_genotype_individual(user_id)
        return genotype_individual
        
    users_genotypes = indiv_data.apply(lambda x: parallel_retrieval_genotypes(x), axis=1)
    users_genotypes = users_genotypes.set_axis(indiv_data['file_link'])

    ## Merge genotypes with the models and store them in a dictionary and calculating the PRS by individual per model
        ## For each model, apply to users_genotypes lambda x: calculating_prs_individual(merge_allelic_data(x, model))
        ## Store them each in a Series

    ## Final dataset with individuals, condition, and PRS scores per model
        ## Final dataframe adding the Series as columns

    return

# ---------------------------------------------------------------------------
## Boilerplate for command line execution of main function for testing
if __name__ == '__main__':
    main()