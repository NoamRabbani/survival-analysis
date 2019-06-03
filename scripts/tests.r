library("survival")
library("survminer")
library("rms")

issues = read.csv("dataset/hbase_features_filtered.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$is_assigned <- factor(issues$is_assigned)
issues$issuetype <- factor(issues$issuetype)
issues$has_priority_change <- factor(issues$has_priority_change)
issues$has_desc_change <- factor(issues$has_desc_change)
issues$comment_count <- log(issues$comment_count)

summary(issues)

# Look for link function
dd <- datadist(issues)
options(datadist = "dd")
link <- cph(Surv(start, end, is_dead) ~ rcs(comment_count, 4), x=TRUE, y=TRUE, data = issues)
p <- Predict(link)
plot(p$comment_count,p$yhat,type="l",xlab="comment_count",ylab="LogRelativeHazard")
lines(p$comment_count,p$lower,lty=2)
lines(p$comment_count,p$upper,lty=2)


fit <- coxph(Surv(start, end, is_dead) ~ comment_count, data = issues)
test = cox.zph(fit, transform = "identity")
print(test$table[1,3], digits = 3)

# issues$log_comment_count = log(issues$comment_count)
# coxph(Surv(start, end, is_dead) ~ log_comment_count, robust = TRUE, data = issues)