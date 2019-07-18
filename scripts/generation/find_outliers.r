require("survival")
require("survminer")
require("rms")

issues = read.csv("dataset/hbase_features_imputed.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$issuetype <- factor(issues$issuetype, levels=c(1,2,3,4,5,6,7))
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

attach(issues)

dd <- datadist(issues); options(datadist = 'dd')
units(start) <- 'Day'
units(end) <- 'Day'

S <- Surv(start, end, is_dead)


f <- cph(S ~ priority + issuetype + is_assigned + rcs(comment_count, 4) + rcs(link_count, 4) +
        rcs(affect_count, 4) + fix_count + has_priority_change + 
        has_desc_change + has_fix_change + rcs(reporter_rep,4) + rcs(assignee_workload,4),
        x=TRUE, y=TRUE)

w <- which.influence(f, cutoff=.035)
inf <- show.influence(w, issues)
inf

write.csv(inf, "which_influence.csv", quote=FALSE)
