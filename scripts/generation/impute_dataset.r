require(rms)

issues = read.csv("dataset/hbase_features_filtered.csv", header = TRUE, sep="\t")

# Apply right data types to columns.
issues$priority <- factor(issues$priority)
issues$issuetype <- factor(issues$issuetype)
issues$is_assigned <- factor(issues$is_assigned)

w <- transcan (~ 
    priority + 
    issuetype + 
    is_assigned + 
    comment_count + 
    link_count + 
    affect_count + 
    fix_count + 
    # has_priority_change + 
    has_fix_change + 
    reporter_rep + 
    assignee_workload,
    imputed=TRUE ,data = issues , pl = FALSE , pr = FALSE )

attach(issues)
issues$assignee_workload <- impute(w, assignee_workload, data=issues)
issues$assignee_workload <- round(issues$assignee_workload)
summary(issues)

write.table(issues, "./dataset/hbase_features_imputed.csv", quote = FALSE, sep="\t", row.names=FALSE)

