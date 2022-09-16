# openPRS: An engine to calculate Polygenic Risk Scores from openSNP data

## Case study and source data

The current case study (proof-of-concept) for this Polygenic Risk Score (PRS) engine is Caffeine Addiction. The input datasets we will use for this problem are the following:

1. **datasets/user_ids.tsv**: Contains a list of ids from individuals that made their genotypes available in openSNP. There are two columns:
   * `file_link`: the reporter's openSNP id. 
   * `caffeine_addiction`: 0 if the reporter is not addicted to caffeine, 1 if yes.
2. **datasets/model_a.tsv**: Contains the output from a existing PRS model. There are two columns:
   * `snp_id`: The openSNP id of a variant of interest.	
   * `effect_size`: The weights (beta coefficients) of each variant according to a PRS linear model.
3. **datasets/model_b.tsv**: Contains the output from a second PRS model.

----
## Calculating the Polygenic Risk Scores


**A bit of theory on PRS first**
  * In healthcare research, a PRS is a measure of the genetic risk of an individual for a particular trait. In its most simple form, it is calculated as the weighted sum of the effect of genetic variants statistically associated with the trait of interest. These variants are usually Single Nucleotide Polymorphisms (SNPs), which are known single base pair changes in the genome of an individual that are also shared by a population. 
  * The formula for the PRS is the following:
    * ![PRS or PGS](https://jmg.bmj.com/content/jmedgenet/57/11/725/F1.large.jpg?width=500&height=300)
  * The allele dosage means how many copies of the effect alleles are present in a single individual. The weights (beta coefficients) are typically estimated from previous genetic association studies for the specific effect allele.


   > *References*
   > * Babb de Villiers, C., Kroese, M., & Moorthie, S. (2020). Understanding polygenic models, their development and the potential application of polygenic scores in healthcare. *Journal of Medical Genetics*, 57(11), 725–732. https://doi.org/10.1136/jmedgenet-2019-106763
   > * Collister, J. A., Liu, X., & Clifton, L. (2022). Calculating Polygenic Risk Scores (PRS) in UK Biobank: A Practical Guide for Epidemiologists. *Frontiers in Genetics*, 13, 818574. https://doi.org/10.3389/fgene.2022.818574

**

**How does the engine work?**
   1. The engine takes the input datasets (**user_ids.tsv**, **model_a.tsv**, **model_b.tsv**) and delivers a CSV file containing the following columns:
      * `file_link`: the reporter's openSNP id. 
      * `caffeine_addiction`: 0 if the reporter is not addicted to caffeine, 1 if yes.
      * `PRS_model_a`: The PRS calculated under the model A.
      * `PRS_model_b`: The PRS calculated under the model B.

   2. The engine carries out the following steps to calculate the PRS values:
      1. For each SNP in the model tables, the engine retrieves its known alleles via NCBI's [Variation Services API](https://api.ncbi.nlm.nih.gov/variation/v0/). 
         Then it calculates the major allele across population studies for that SNP. **Important note:** In absence of additional data, the major allele is considered the non-effect allele.
      2. For each individual in the **user_ids** table, the engine retrieves their entire panel of genotyped SNPs via [openSNP](https://opensnp.org/) database. Then, the output is standardized to account for the different genotype formats (*ancestry* to *23andMe* format) thus facilitating downstream processes.
      3. For each model and individual, the engine calculates the effect allele dosage of the SNPs considered in the model. Afterwards, the PRS for the individual is computed by summing the product between the allele dosage of each SNP and its effect size.
      4. The PRS values of all the individuals for each model are attached to the **user_ids** table and stored in a CSV file.

**

**Results of the case study**
   * Please access this [Python Notebook](PRS_analysis.ipynb) for a data analysis of the two caffeine addiction PRS models of this case study.

----
## How to run the code: execution and dependencies

The engine is coded in Python 3 and packaged in a Docker container. Thus, it can be run in any host operating system with Docker installed. 
The configuration of the Docker image can be consulted in the [Dockerfile](Dockerfile).

**Installation and execution**
   * Clone this repository into your machine.
   * Execute the `run.sh` script in your shell.
   * Let the openPRS engine run and see your results in the `workflow_results` folder!

**Dependencies and requirements**
   * The Docker image executes the code in python3.8. The required python packages are the following:
     > * `numpy`
     > * `pandas`
     > * `six`
     > * `botocore`
     > * `modin`
     > * `protobuf`
     > * `ray`
     > * `requests`
     > * `flatten_json`
     > * `argparse`
   * The specific versions and installation modes of the packages above can be checked in the [requirements](requirements.txt) file.
   * The packages used by the data analysis notebook are listed in the [requirements_notebook](requirements_notebook.txt) file.

----
## Considerations on time complexity and optimization strategies

**High time complexity steps**
   * From line 95 to line 99 of the [cohort_prs.py](src/cohort_prs.py) script, the engine performs multiple merging operations between the model tables and the individual genotypes tables. This indicates that it has an average complexity of O(m*n) where m = number of individuals and n = number of models. This complexity is particularly dangerous when multiple models are evaluated. The strategy used to mitigate this issue was the usage of parallel operations with [modin](https://modin.readthedocs.io/en/stable/) DataFrames and [ray](https://www.ray.io/) libraries. This improves the execution time by distributing the tasks among all available CPU threads, which makes this a viable solution when elastic IT infrastructures are available.

**Bottlenecks**
   * *Recovering major (non-effect) alleles.* This step is carried out via [Variation Services API](https://api.ncbi.nlm.nih.gov/variation/v0/) requests. Although this step has a time complexity of O(n), it is a current bottleneck since the API response time is relatively slow and the number of SNPs can increase explosively with additional PRS models. To mitigate this, I used parallelized requests via modin DataFrames which reduced the execution time. A definitive solution to this problem would be providing the effect alleles as an input file. 
   * *Recovering individual genotypes from openSNP.* The considerations and mitigation strategy are identical to the previous step, but the difference is that the API response time here is even worse. A better solution to this would be having a local copy of the openSNP database.

----
## Known issues


* The openSNP id `10424.ancestry.8695` was excluded from this analysis because the API response contains a corrupted file.
* The `--platform=linux/amd64 ubuntu:18.04` flag used in the Dockerfile forces the use of a base image compiled for amd64 architectures. While this suits well to many modern Intel and AMD processors, it slows down the execution speed in machines using ARM chips such as the most recent Mac laptops, Raspberry Pi, and other portable devices.

----
## Use License


This project is covered by the [GPL v3](LICENSE) license.