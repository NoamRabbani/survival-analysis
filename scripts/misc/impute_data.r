require("survival")
require("survminer")
require("rms")

issues = read.csv("dataset/hbase_features_filtered.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$issuetype <- factor(issues$issuetype, levels=c(1,2,3,4,5,6,7))
issues$is_assigned <- factor(issues$is_assigned)
issues$has_priority_change <- factor(issues$has_priority_change)
issues$has_desc_change <- factor(issues$has_desc_change)
issues$has_fix_change <- factor(issues$has_fix_change)

# Impute missing data
w <- transcan(~ priority + issuetype + is_assigned + comment_count + link_count + affect_count 
                + fix_count + has_priority_change + has_desc_change + has_fix_change + reporter_rep +
                assignee_workload, imputed=TRUE ,data=issues, pl=FALSE, pr=FALSE)
attach(issues)
assignee_workload <- impute(w, assignee_workload, data=issues)

write.csv(issues,"dataset/hbase_features_imputed.csv")
print("test")
