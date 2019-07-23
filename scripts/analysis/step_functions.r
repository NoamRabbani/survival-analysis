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


issues2 <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(90, 180, 270), episode="tgroup")
# issues2 <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(60, 120, 180, 240, 300), episode="tgroup")

# issues2$interaction_is_assigned <- interaction(issues2$is_assigned, strat(issues2$tgroup))
# issues2$int_comment_count <- interaction(issues2$comment_count,issues2$tgroup)
# issues2$int_link_count <- interaction(issues2$link_count, strat(issues2$tgroup))
# issues2 <- with((issues2), data.frame(issues2, interaction(comment_count,tgroup)))
# colnames(issues2)[20] <- "int_comment_count"
summary(issues2)

# write.csv(issues2, "./dataset/hbase_features_interactions.csv", quote=FALSE)


dd <- datadist(issues2); options(datadist = "dd")
units(start) <- "Day"
units(end) <- "Day"

# f <- coxph(Surv(start, end, is_dead) ~ 
#         priority + 
#         issuetype + 
#         is_assigned + 
#         rcs(comment_count,4):strata(tgroup) + 
#         rcs(link_count, 4):strata(tgroup) +
#         rcs(affect_count, 4) + 
#         rcs(fix_count,4):strata(tgroup) + 
#         has_priority_change:strata(tgroup) + 
#         has_desc_change:strata(tgroup) + 
#         rcs(has_fix_change,4):strata(tgroup) + 
#         rcs(reporter_rep,4):strata(tgroup) + 
#         rcs(assignee_workload,4):strata(tgroup),
#         x=TRUE, y=TRUE, data=issues2)

f <- cph(Surv(start, end, is_dead) ~ 
        priority + 
        # issuetype + 
        is_assigned + 
        rcs(comment_count,4)*strat(tgroup) + 
        rcs(link_count, 4)*strat(tgroup) +
        rcs(affect_count, 4) + 
        rcs(fix_count,4)*strat(tgroup) + 
        has_priority_change*strat(tgroup) + 
        has_desc_change*strat(tgroup) + 
        rcs(has_fix_change,4)*strat(tgroup) + 
        rcs(reporter_rep,4)*strat(tgroup) + 
        rcs(assignee_workload,4)*strat(tgroup),
        x=TRUE, y=TRUE, data=issues2)

print(f, latex = TRUE, coefs = TRUE)


z <- predict(f, type="terms")
f.short <- coxph(Surv(start, end, is_dead) ~ z, x=TRUE, y=TRUE, data=issues2)
zph <- cox.zph(f.short, transform="identity")
zph

