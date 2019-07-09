require("survival")
require("survminer")
require("rms")

issues = read.csv("dataset/hbase_features_filtered.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$issuetype <- factor(issues$issuetype, levels=c(1,2,3,4,5,6,7))
issues$has_priority_change <- factor(issues$has_priority_change)
issues$has_desc_change <- factor(issues$has_desc_change)
issues$has_fix_change <- factor(issues$has_fix_change)
issues$log_comment_count <- log(issues$comment_count + 1)
issues$log_fix_count <- log(issues$fix_count + 1)
issues$log_reporter_rep <- log(issues$reporter_rep + 1)

attach(issues)
dd <- datadist(issues); options(datadist = 'dd')
units(start) <- 'Day'
units(end) <- 'Day'

S <- Surv(start, end, is_dead)
# f <- cph(S ~ priority + rcs(link_count, 4) +
#          rcs(affect_count, 4) + has_priority_change + 
#          has_desc_change,
#          x=TRUE, y=TRUE, surv=TRUE)

f <- cph(S ~ priority + issuetype + rcs(comment_count, 4) + rcs(link_count, 4) +
         rcs(affect_count, 4) + rcs(log1p(fix_count), 4) + has_priority_change + 
         has_desc_change + has_fix_change + rcs(log1p(reporter_rep),4),
         x=TRUE, y=TRUE)

# show.influence(which.influence(f), issues)

# p <- Predict(f)
# plot(p$fix_count,p$yhat,type="l",xlab="fix_count",ylab="LogRelativeHazard")
# lines(p$fix_count,p$lower,lty=2)
# lines(p$fix_count,p$upper,lty=2)


print(f, latex = TRUE, coefs = FALSE)

z <- predict(f, type='terms')
f.short <- cph(S ~ z, x=TRUE, y=TRUE)
phtest <- cox.zph(f.short, transform='identity')
phtest
ggcoxzph(phtest)