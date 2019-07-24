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
        rcs(affect_count, 4)*strat(tgroup) + 
        rcs(fix_count,4)*strat(tgroup) + 
        has_priority_change*strat(tgroup) + 
        has_desc_change*strat(tgroup) + 
        rcs(has_fix_change,4)*strat(tgroup) + 
        rcs(reporter_rep,4)*strat(tgroup) + 
        rcs(assignee_workload,4)*strat(tgroup),
        x=TRUE, y=TRUE, data=issues)

print(f, latex = TRUE, coefs = TRUE)

z <- predict(f, type="terms")
f.short <- coxph(Surv(start, end, is_dead) ~ z, x=TRUE, y=TRUE, data=issues)
zph <- cox.zph(f.short, transform="identity")
zph

pdf("./scripts/analysis/schoenfeld_residuals.pdf")
for ( i in 1:(length(zph)*2)){
    plot(zph[i])
    abline(0,0, col=2)
    abline(h=f$coef[i], col=i, lwd=2, lty=2)
}
dev.off()
