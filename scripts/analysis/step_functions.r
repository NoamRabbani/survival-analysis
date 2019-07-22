require("survival")
require("survminer")
require("rms")

issues = read.csv("dataset/hbase_features_imputed.csv", header = TRUE, sep="\t")

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


issues2 <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(365,730,1095), episode="tgroup")
write.csv(issues2, "./dataset/hbase_features_tgroup.csv", quote=FALSE)

# issues2$interaction_is_assigned <- issues2$is_assigned * strata(issues2$tgroup)
issues2$interaction_comment_count <- interaction(issues2$comment_count, strata(issues2$tgroup))

dd <- datadist(issues); options(datadist = "dd")
units(start) <- "Day"
units(end) <- "Day"

# f <- cph(Surv(start, end, is_dead) ~ priority + comment_count * strat(issues2$tgroup),
#         x=TRUE, y=TRUE, singular.ok=TRUE, data=issues2)
# f


f <- cph(Surv(start, end, is_dead) ~ priority + issuetype + is_assigned + rcs(comment_count,4)*strat(tgroup) + rcs(link_count, 4) +
        rcs(affect_count, 4)*strat(tgroup) + rcs(fix_count,4)*strat(tgroup) + rcs(has_priority_change,4)*strat(tgroup) + 
        has_desc_change + rcs(has_fix_change,4)*strat(tgroup) + rcs(reporter_rep,4)*strat(tgroup) + rcs(assignee_workload,4),
        x=TRUE, y=TRUE, data=issues2)
print(f, latex = TRUE, coefs = FALSE)


z <- predict(f, type="terms")
f.short <- cph(Surv(start, end, is_dead) ~ z, x=TRUE, y=TRUE, data=issues2)
zph <- cox.zph(f.short, transform="identity")
zph
# issues_tgroup = survSplit(Surv(start, end, is_dead) ~ priority + issuetype + is_assigned + rcs(comment_count,4) + rcs(link_count, 4) +
#         rcs(affect_count, 4) + rcs(fix_count,4) + has_priority_change + 
#         has_desc_change + rcs(has_fix_change,4) + rcs(reporter_rep,4) + rcs(assignee_workload,4),
#         data=issues, cut=c(1000), episode="tgroup", id="issuekey")

# summary(issues_tgroup)
