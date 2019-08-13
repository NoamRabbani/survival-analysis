require("survival")
require("survminer")
require("rms")

issues = read.csv("dataset/hbase_features_survsplit.csv", header = TRUE, sep="\t")

# Apply right data types to columns.
issues$priority <- factor(issues$priority)
issues$issuetype <- factor(issues$issuetype)
issues$is_assigned <- factor(issues$is_assigned)

dd <- datadist(issues); options(datadist = "dd")
units(start) <- "Day"
units(end) <- "Day"

f <- cph(Surv(start, end, is_dead) ~ 
        priority + 
        issuetype + 
        is_assigned + 
        rcs(comment_count,4)*strat(tgroup) +
        rcs(link_count, 4)*strat(tgroup) + 
        rcs(affect_count, 4)*strat(tgroup),
        # rcs(fix_count,4)*strat(tgroup) + 
        # has_priority_change*strat(tgroup) + 
        # has_desc_change*strat(tgroup) + 
        # rcs(has_fix_change,4)*strat(tgroup) + 
        # rcs(reporter_rep,4)*strat(tgroup) + 
        # rcs(assignee_workload,4)*strat(tgroup)
        ,
        x=TRUE, y=TRUE, surv=TRUE, data=issues)

print(f, latex = TRUE, coefs = TRUE)

nom <- nomogram(f, 
    interact = list(tgroup = 1, comment_count = 5, link_count = 5, affect_count = 0)
    )

pdf("./scripts/analysis/nomogram.pdf")
plot ( nom , xfrac = .65 , lmgp = .35 )
dev.off()