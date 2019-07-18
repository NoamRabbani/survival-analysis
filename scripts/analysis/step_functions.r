require("survival")
require("survminer")
require("rms")

issues = read.csv("dataset/hbase_features_imputed.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
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

dd <- datadist(issues); options(datadist = "dd")
units(start) <- "Day"
units(end) <- "Day"



f <- cph(Surv(start, end, is_dead) ~ priority + issuetype + is_assigned + rcs(comment_count,4) + rcs(link_count, 4) +
        rcs(affect_count, 4) + rcs(fix_count,4) + has_priority_change + 
        has_desc_change + rcs(has_fix_change,4) + rcs(reporter_rep,4) + rcs(assignee_workload,4),
        x=TRUE, y=TRUE, data=issues)
print(f, latex = TRUE, coefs = FALSE)

z <- predict(f, type="terms")
f.short <- cph(Surv(start, end, is_dead) ~ z, x=TRUE, y=TRUE, data=issues)
zph <- cox.zph(f.short, transform="identity")
zph

issues_tgroup = survSplit(Surv(start, end, is_dead) ~ priority + issuetype + is_assigned + rcs(comment_count,4) + rcs(link_count, 4) +
        rcs(affect_count, 4) + rcs(fix_count,4) + has_priority_change + 
        has_desc_change + rcs(has_fix_change,4) + rcs(reporter_rep,4) + rcs(assignee_workload,4),
        data=issues, cut=c(1000), episode="tgroup", id="issuekey")

summary(issues_tgroup)

# f <- cph(Surv(start, end, is_dead) ~ priority + issuetype + is_assigned:strata(tgroup) + rcs(comment_count,4) + rcs(link_count, 4) +
#                     rcs(affect_count, 4) + rcs(fix_count,4) + has_priority_change + 
#                     has_desc_change + rcs(has_fix_change,4) + rcs(reporter_rep,4) + rcs(assignee_workload,4),
#         x=TRUE, y=TRUE, data=issues_tgroup)

# z <- predict(f, type="terms")
# f.short <- cph(Surv(start, end, is_dead) ~ z, x=TRUE, y=TRUE, data=issues_tgroup)
# zph <- cox.zph(f.short, transform="identity")
# zph
