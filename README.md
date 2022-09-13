# Polygenic Risk Score Problem

We are trying to build a PRS model for caffeine addiction. As a preliminary step, two simple models are built, and we would like to evaluate the model using some open test dataset from [openSNP](https://opensnp.org/). We would like you to retrieve a subset of genotype data and evaluate how the two models perform. 

Three files have been provided for you: 

1. user_ids.tsv contains a subset of genotype filenames from openSNP, there are two columns:
   * `file_link`: the name of the reporter's genotype file. 
   * `caffeine_addiction`: 0 if the reporter is not addicted to caffeine, 1 if yes.
2. model_a.tsv contains the output from a PRS model.
3. model_b.tsv contains the output from a separate PRS model.

Please create a git repository hosted on Github or similar that contains your code analyzing the results. The repo should contain some instructions (can be any format, e.g. Notebook, README, etc.) on how to run your code and reproduce the results in the correct environment with dependencies installed (you might use e.g. a virtual environment or a docker container). Please assume we'll be running the code on a default Ubuntu 16.04 instance.

Notes:
1. The genotype file can be downloaded using this link: https://opensnp.org/data/[file_link], for example, 12345.23andme.789 can be downloaded at https://opensnp.org/data/12345.23andme.789.
2. The predictive results of the model may not look good, however, it is beyond the scope of this assignment to improve the model. So, please just analyze the results as it is.
3. There are python packages such as `snps`, that you can use to read the user genotype file.

Describe:
1. Any pre-processing steps/analysis you have used, or you would like to use but do not implement due to time limit or computational time. 
2. Run the two models on the test set and provide the output to us.
3. The evaluation results of the two PRS models, including metrics you used to do the evaluation.
4. Any computational complexity of the code you have used to analyze the results, considering it may be applied to thousands or millions of user data in the future.
5. Provide a discussion of how the two model performed, how would you like to interpret the score to the reporters, as well as future improvements to provide better estimates of the PRS score.