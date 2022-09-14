#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By: David Aurelia Ayala Usma
# Created Date: 2022-09-13
# Version = 0.0.1
# ---------------------------------------------------------------------------

## Description
"""Module to calculate the Polygenic Risk Score for a single individual"""

# ---------------------------------------------------------------------------
## Required libraries
import os
import sys
import ray
import numpy as np
import requests as rq
import flatten_json as fj
from pandas import read_csv as rcsv #Avoid dtype conflict in modin

## Parallelized pandas
#ray.init(_plasma_directory = '/tmp')
os.environ["MODIN_ENGINE"] = "ray"
import modin.pandas as pd

# ---------------------------------------------------------------------------
## Constants
BASE_DIR = os.path.dirname(os.getcwd())
REFSNP_API = 'https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{snp_id}/frequency'
OPENSNP_API = 'https://opensnp.org/data/{user_id}'

# ---------------------------------------------------------------------------
## Module functions

## Safe URL API requests
#  adapted from: https://github.com/ncbi/dbsnp/blob/master/tutorials/Variation%20Services/Jupyter_Notebook/spdi_batch.ipynb
def api_request(url):
    try:
        r = rq.get(url)
    except rq.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        print("ERROR: Timeout")
    except rq.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        print("ERROR: bad url =" + url)
    except rq.exceptions.RequestException as e:
        # catastrophic error. bail.
        print(e)
        sys.exit(1)
    if (r.status_code == 200):
        return r
    else:
        print("ERROR: status code = " + str(r.status_code))
        return None

## Recovering the major (non-effect) allele of the genotyped variant
def get_major_allele_api(snp_id):
    var_dict = api_request(REFSNP_API.format(snp_id=snp_id)).json()
    allele_freqs = {}

    var_dict_flatten = fj.flatten(var_dict)
    for key, value in var_dict_flatten.items():
        if('allele_counts' in key):
            allele = key[-1]
            if(allele in allele_freqs.keys()):
                allele_freqs[allele] = allele_freqs[allele] + value
            else:
                allele_freqs[allele] = value

    major_allele = sorted(allele_freqs.items(), key=lambda item: item[1])[-1][0]
    #print("SNP: {snp_id} has a major allele of {major_allele}".format(snp_id=snp_id, major_allele=major_allele))
    return major_allele

## Recovering the genotype dataset from a given individual
def get_genotype_individual(user_id):
    if(user_id != None):
        print("Retrieval of genotype of user: {user_id} started!".format(user_id=user_id))
        if('ancestry' in user_id):
            genotype = rcsv(OPENSNP_API.format(user_id=user_id), comment='#', sep='\t', low_memory=False)
            genotype['genotype'] = genotype['allele1'].astype(str) + genotype['allele2'].astype(str)
        else:
            genotype = rcsv(OPENSNP_API.format(user_id=user_id), comment='#', sep='\t', header=None, low_memory=False)
            genotype.columns = ['rsid', 'chromosome', 'position', 'genotype']
        
        print("Retrieval of genotype of user: {user_id} finished!".format(user_id=user_id))
        genotype = pd.DataFrame(genotype)
    return genotype

## Extracting the genotyped alleles from each individual for the PRS
def get_genotyped_alleles_individual(user_genotype, model_table):
    merged_df = user_genotype.merge(model_table,left_on='rsid', right_on='snp_id', how='inner')
    return merged_df

## Takes a model table and extracts the major (non-effect) allele of a given SNP
def assign_major_allele(snp_entry):
    snp_id = snp_entry['snp_id'].replace(r'rs', '')
    major_allele = get_major_allele_api(snp_id)
    print("Major (non-effect) allele for variant {snp} successfully retrieved".format(snp=snp_entry['snp_id']))
    return major_allele

## Get minor allele dosage
def get_minor_allele_dosage(snp_entry):
    major_allele = snp_entry['major_allele']
    genotype = snp_entry['genotype']
    dosage = len(genotype) - genotype.count(major_allele)
    return dosage

## Obtaining the major (no-effect) allele
def get_major_alleles_model(model_table):
    model_table['major_allele'] = model_table.apply(lambda x: assign_major_allele(x), axis=1)
    return model_table

## Attaching the major (no-effect) allele and the dosage of the minor (effect) allele
def merge_allelic_data(user_genotype, model_table):
    if(type(user_genotype) != type(model_table)):
        user_genotype = pd.DataFrame(user_genotype)
        model_table = pd.DataFrame(model_table)
    final_genotype_individual = get_genotyped_alleles_individual(user_genotype, model_table)
    final_genotype_individual['minor_allele_dosage'] = final_genotype_individual.apply(lambda x: get_minor_allele_dosage(x), axis=1)
    return final_genotype_individual

## Calculating the PRS from the effect size and the minor (effect) allele dosage
def calculating_prs_individual(final_genotype_individual):
    prs = final_genotype_individual['effect_size'] * final_genotype_individual['minor_allele_dosage']
    return sum(prs)

# ---------------------------------------------------------------------------
## Main function for testing

def individual_prs(individual_code, model_table):
    print("Starting Individual PRS module")
    individual_data = get_genotype_individual(individual_code)
    print("SNPs of the individual retrieved!")
    model_data = pd.read_csv(model_table, sep='\t')
    print("PRS model coefficients retrieved!")
    model_data = get_major_alleles_model(model_data)
    print("Non-effect alleles retrieved!")
    geno_indiv_model = merge_allelic_data(individual_data, model_data)
    print("Relevant genotypes for the PRS extracted!")
    prs_model_indiv = calculating_prs_individual(geno_indiv_model)
    print("The PRS of the individual {individual} for the Model {model} is: {prs}".format(individual=individual_code, model=model_table, prs=prs_model_indiv))

# ---------------------------------------------------------------------------
## Boilerplate for command line execution of main function for testing
if __name__ == '__main__':
    ray.init()
    individual_prs('10787.ancestry.8931', '{base_dir}/datasets/model_a.tsv'.format(base_dir=BASE_DIR))
