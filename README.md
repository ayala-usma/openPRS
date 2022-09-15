# openPRS: An engine to calculate Polygenic Risk Scores from openSNP data

## Case study and source data

The current case study (proof-of-concept) for this Polygenic Risk Score (PRS) engine is Caffeine Addiction. The input datasets we will use for this problem are the following:

1. **datasets/user_ids.tsv**: Contains a subset of genotype filenames from openSNP. There are two columns:
   * `file_link`: the name of the reporter's openSNP id. 
   * `caffeine_addiction`: 0 if the reporter is not addicted to caffeine, 1 if yes.
2. **datasets/model_a.tsv**: Contains the output from a PRS model. There are two columns:
   * `snp_id`: The SNP id as it is recorded in openSNP.	
   * `effect_size`: The weights (or beta coefficients) of each variant according to a PRS linear model.
3. **datasets/model_b.tsv**: Contains the output from a second PRS model.

----
## Calculating the Polygenic Risk Scores


**A bit of theory on PRS first**
  * In healthcare research, a PRS is an measure of the genetic risk of an individual’s for a particular trait. In its most simple form, it is calculated as the weighted sum of the effect of genetic variants that previously have shown statistical association with the trait of interest. These variants are usually Single Nucleotide Polymorphisms (SNPs), which is a known single base pair change in someone's genome that is also shared by a population. 
  * The formula for the PRS is the following:
    * ![PRS or PGS](https://jmg.bmj.com/content/jmedgenet/57/11/725/F1.large.jpg?width=500&height=300)
  * The allele dosage means how many of the effect alleles are present in a single individual. The weights (beta coefficients) are typically estimated from a previous genetic association study for the specific effect allele.


   > *References*
   > * Babb de Villiers, C., Kroese, M., & Moorthie, S. (2020). Understanding polygenic models, their development and the potential application of polygenic scores in healthcare. *Journal of Medical Genetics*, 57(11), 725–732. https://doi.org/10.1136/jmedgenet-2019-106763
   > * Collister, J. A., Liu, X., & Clifton, L. (2022). Calculating Polygenic Risk Scores (PRS) in UK Biobank: A Practical Guide for Epidemiologists. *Frontiers in Genetics*, 13, 818574. https://doi.org/10.3389/fgene.2022.818574

**

**How does the engine work?**
  1. The engine takes the input datasets (**user_ids.tsv**, **model_a.tsv**, **model_b.tsv**) and delivers as an output a CSV file containing the following columns:
      * `file_link`: the name of the reporter's openSNP id. 
      * `caffeine_addiction`: 0 if the reporter is not addicted to caffeine, 1 if yes.
      * `PRS_model_a`: The PRS calculated under the model A.
      * `PRS_model_b`: The PRS calculated under the model B.

   1. The engine carries out the following steps to calculate the PRS values:
      1. For each SNP in each model table, the engine retrieves the known alleles to the dbSNP database via NCBI's [Variation Services API](https://api.ncbi.nlm.nih.gov/variation/v0/). 
         Then it calculates the major allele across population studies for that SNP. In absence of further data, the major allele is considered the non-effect allele.
      2. For each individual in the **user_ids** table, the engine retrieves the entire panel of genotyped SNPs via [openSNP](https://opensnp.org/) database and standardizes the format of the genotypes (*ancestry* to *23andMe* format) to allow seamless downstream analysis.
      3. Then, for each model and individual the engine calculates the effect allele dosage of the relevant SNPs for the particular model. Afterwards, the PRS for the individual is computed by multiplying the effect sizes and allele dosage of each SNP, and summing those products.
      4. The PRS values of the cohort for each model are attached to the **user_ids** table and stored in a CSV file.

**

**Results of the case study**
   * [Please access this Python Notebook for a data analysis of the Caffeine Addiction PRS models](PRS_analysis.ipynb)

----
## How to run the code: execution and dependencies

The engine is coded in Python 3 and packaged in a Docker container using the Ubuntu 18.04 base image. Thus, it can be run in any host operating system with Docker installed. 
The configuration of the Docker image can be consulted in the [Dockerfile](Dockerfile).

**Installation and execution**
   * Clone this repository to your machine.
   * Execute the `run.sh` script in your shell.
   * Let the openPRS engine run and see your results in the `workflow_results` folder!

**Dependencies and requirements**
   * Inside the Docker container the code is executed by python 3.8. The python packages used in the engine are the following:
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
   * The packages used in the data analysis notebook are listed in the [requirements_notebook](requirements_notebook.txt) file.

----
## Considerations on time complexity and optimization strategies

**High time complexity steps**
   * From line 95 to line 99 of the [cohort_prs.py](src/cohort_prs.py) script, the engine performs multiple merging operations between the model tables and the individual genotypes tables to calculate the PRS of each individual for each model. This typically indicates that it has an average complexity of O(m*n) where m = number of individuals and n = number of models. This complexity is particularly dangerous when multiple models are evaluated. Strategies to mitigate this issue include the usage of parallel operations with modin and ray libraries which can improve the execution time scalably by distributing the tasks among all available CPU threads.

**Bottlenecks**
   * Recovery of major (non-effect) alleles. This step is carried out via [Variation Services API](https://api.ncbi.nlm.nih.gov/variation/v0/) requests. Although this step has a worst-case time complexity of approximately O(n), it is a current bottleneck since the API response time is relatively slow and the number of SNPs can increase explosively with additional PRS models. For this, I used parallelized requests via modin DataFrames which reduced the execution time. A definitive solution to this problem would be providing the effect alleles as an input file. 
   * Recovery of individual genotypes from openSNP. The considerations are almost identical to the previous step. The only difference is that the API response time here is *worse*, and thus having an indexed local database with the openSNP data would be ideal to boost the performance here.

----
## Known issues


* The openSNP id `10424.ancestry.8695` was excluded from this analysis because the API response contains a corrupted file.
* The `--platform=linux/amd64 ubuntu:18.04` flag used in the Dockerfile forces the use of a base image compiled for amd64 architectures. While this suits well to many modern Intel and AMD processors, it slows down the execution speed in machines using ARM chips such as the most recent Mac laptops, Raspberry Pi, and other portable devices.

----
## Use License


This project is covered by the [GPL v3](LICENSE) license.