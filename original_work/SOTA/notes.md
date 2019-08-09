# Papers that propose a model

## habayeb2018tse
    * Proposes a hidden markov chain (HMM) model uses temporal features to achieve SOTA results in classifying bugs as slow resolution and fast resolution.
    * Replicates what they consider the SOTA (zhang2013icse) and achieves 33% higher F-measure.

## akbarinasaji2018jsas
    * Replicates zhang2013icse (KNN learner with custon distance metric) and determines that the model is generalizable and that it can be used for further research.

## rees-jones2017cornell
    * Uses a decision tree with seven creation-time features to achieve SOTA results in predicting issue resolution times.
    * Gets their data and features from the JIRA of apache projects.
    * Claims that training a learner on cross-project data improves the performance of the model.
    * Claims that the model by zhang2013icse is complicated and difficult to interpret.
    * Claims that kikas2016msr, which uses random forests, is the SOTA.

## asar2016ese
    * Replicates the work of an original paper in detail to obtain defect resolution time based on text clustering.
    * Extends the original paper by applying the model to a new context and obtains poor accuracy. Argues that this model does not achieve practically useful levels of accuracy.
    * Has a great summary of previous work on bug fix time.

## jiang2013msr
    * Measures how much time it takes for a patch to get accepted.
    * Uses decision trees with 35 features to determine wether a patch will be accepted in the linux project. Uses top node analysis to determine which features have the most influence.
    * Repeat the same approach to determine how long it will take for a patch to be merged in the linux project.

## zhang2013icse
    * Uses KNN to predict bug fix time based on simple features. However, the distance metrics for the KNN model are not trivial.
    * Compares the KNN model with other basic models such as Naive Bayes and Decision Tree.

## marks2011promise
    * Uses random forests with 23 features grouped in three dimensions (location, reporter, and description) to classify bug fix time into three classes (>3 months,  >1 year, and >3 years). The projects studied are Eclipse and Mozilla and the model accuracy is 65%.
    * All numeric features are binned into three categories (low, medium, and high) to improve explainability of the decision trees. They also perform top-node analysis.
    * No comparison with the SOTA. 

## panjer2007msr
    * Uses 17 features and 5 models to classify the time taken to fix a bug into 7 bins of time intervals. Data is collected from Eclipse's Bugzilla and the their best model (logistic regression) achieves a prediction accuracy of 34.9%.
    * Features are extracted at the bug's creation time.
    * Top node analysis shows that "comments", "severity", and "version" are the most important features.

## giger2010rsse
    * Uses decision trees and 17 features to classify bugs into slow fixes or fast fixes in relation to median fix time. Reports precision, recall and AUC ranging from 0.65 to 0.74.
    * Uses post-submission data of bug reports to increase the performance of the model. The more post-submission information you have, the better the model.

## weib2007msr
    * KNN model that uses issue title and description as a features. They compute distances between text samples using the lucene framework and then apply a KNN model.
    * They perform model validation, but it is specific to their approach.

# Papers that analyze features

## zhang2012wcre
    * Studies a specific stage in the lifecycle of bugs: the time from when a bug is reported to when it starts getting fixed. They refer to this stage as delays in bug fixing.
    * Uses logistic regression with nine features to determine their influence on bug fixing delays. Features are derived the from the issue reports.
    * No model performance measure.

## bhattacharya2011msr
    * Use multivariate regression and four features to show that predictive power is low when trying to predict bug fix time.
    * Use univariate regression and four features to show that predictive power is low when trying to predict bug fix time.
    * Find that "reporter reputation" has poor predictive power on bug fix time.

# Papers that use survival analysis

## syer2015tse
    * Uses survival analysis to predict when a defect will occur in a module based on the module's LOC.
    * Remove potential outliers in their data by deleting the smallest and larget 10 observations.
    * Modify the data to respect proportional hazards by applying link functions.
    * Use dfbeta residuals to find overly influential observations, but decide to keep them in the dataset because they are valid.

## canfora2011wcre
    * Uses survival analysis to determine which code constructs (loops, exception handling, function calls) affects the survival of a bug. They also analyze interacting features (but not time interactions).
    * They use AIC(?) to determine which distribution (Weibull, Cox, logistic) to use for survival analysis. They pick Cox.
    * Finds that one feature doesn't respect proportional hazards assumption and excludes it.

## selim2010wcre
    * Uses survival analysis with 17 features related to code clones to predict when a defect will occur.
    * To compare their results, they use another survival model with control features only.
    * To satisfy proportional hazards, they only use a subset of their data for modelling. They also use link functions.
    * They use spearman correlation for model validation.

# koru2008ese
    * Claims that cox model diagnostic has three compoments: checking proportional hazards, checking overly influential observations and checking Spearman correlation.

# Miscellaneous Papers

## abdelmoez2013taeece
    * Shows that removing outliers slighlty improves recall of a Naive Bayes model that predicts bug fix time using 16 features.

## kim2006msr
    * Bean counting on how long it takes to fix a bug after it was introduced in the codebase (as opposed to reported on the issue tracker).

---------------------------------------------------------------------------

# Thrusts of our paper

## We are able to make predictions without creating arbitrary classification bins
    * panjer2007msr uses 7 time bins for classification.
    * giger2010rsse classifies bugs into slow fixes or fast fixes as compared to the median fix time.

## The RMS package gives good insights on our model
    * selim2010wcre use coefficients and p values to determine which predictors have the most influence. This might not be a valid analysis.
