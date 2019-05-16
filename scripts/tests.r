library("survival")
library("survminer")

issues = read.csv("dataset/hbase_features_raw.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$death <- factor(issues$death)
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$assignee <- factor(issues$assignee)
issues$issuetype <- factor(issues$issuetype)

summary(issues)
