require(rms)

issues = read.csv("dataset/hbase_features_filtered.csv", header = TRUE, sep="\t")

# Apply right data types to columns.
issues$start <- as.numeric(issues$start)
issues$end <- as.numeric(issues$end)
issues$priority <- factor(issues$priority)
issues$issuetype <- factor(issues$issuetype)
issues$is_assigned <- factor(issues$is_assigned)
issues$comment_count <- as.numeric(issues$comment_count)
issues$link_count <- as.numeric(issues$link_count)
issues$affect_count <- as.numeric(issues$affect_count)
issues$fix_count <- as.numeric(issues$fix_count)
issues$has_priority_change <- as.numeric(issues$has_priority_change)
issues$has_desc_change <- as.numeric(issues$has_desc_change)
issues$has_fix_change <- as.numeric(issues$has_fix_change)
issues$reporter_rep <- as.numeric(issues$reporter_rep)
issues$assignee_workload <- as.numeric(issues$assignee_workload)

w <- transcan (~ priority + issuetype + is_assigned + comment_count + link_count + 
                affect_count + fix_count + has_priority_change + 
                has_fix_change + reporter_rep + assignee_workload,
                 imputed=TRUE ,data = issues , pl = FALSE , pr = FALSE )

attach(issues)
issues$assignee_workload <- impute(w, assignee_workload, data=issues)
issues$assignee_workload <- round(issues$assignee_workload)
summary(issues)

write.table(issues, "./dataset/hbase_features_imputed.csv", quote = FALSE, sep="\t", row.names=FALSE)

