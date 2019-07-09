library("survival")
library("survminer")
library("rms")

issues = read.csv("dataset/hbase_features_filtered.csv", header = TRUE, sep="\t")
s = subset(issues, end>1000)
length(unique(s$issuekey))
length(unique(issues$issuekey))

# transform columns into factors with the modes as first value
issues$log_comment_count <- log(issues$comment_count + 1)

# summary(issues)

# Look for link function
dd <- datadist(issues)
options(datadist = "dd")
# link <- cph(Surv(start, end, is_dead) ~ rcs(comment_count, 4), x=TRUE, y=TRUE, data = issues)
link <- cph(Surv(start, end, is_dead) ~ log_comment_count, x=TRUE, y=TRUE, data = issues)
p <- Predict(link)
plot(p$log_comment_count,p$yhat,type="l",xlab="commentlog_comment_count_count",ylab="LogRelativeHazard")
lines(p$log_comment_count,p$lower,lty=2)
lines(p$log_comment_count,p$upper,lty=2)


fit <- coxph(Surv(start, end, is_dead) ~ log1p(comment_count), x=TRUE, y=TRUE, data = issues)
test = cox.zph(fit, transform = "identity")
test

# issues$log_comment_count = log(issues$comment_count)
# coxph(Surv(start, end, is_dead) ~ log_comment_count, robust = TRUE, data = issues)