require("survival")
require("survminer")
require("rms")

issues = read.csv("dataset/hbase_features_imputed.csv", header = TRUE, sep="\t")

# Apply right data types to columns.
issues$priority <- factor(issues$priority)
issues$issuetype <- factor(issues$issuetype)
issues$is_assigned <- factor(issues$is_assigned)

issues2 <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(30, 60, 90, 180, 270), episode="tgroup")
write.table(issues2, "./dataset/hbase_features_survsplit.csv", quote=FALSE, sep="\t")