library("survival")
library("survminer")

issues = read.csv("dataset/hbase_features_raw.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$assignee <- factor(issues$assignee)
issues$issuetype <- factor(issues$issuetype)

res.cox <- coxph(Surv(start, end, death) ~ priority + assignee + issuetype, data = issues)
fit <- survfit(res.cox, data = issues)

test = cox.zph(res.cox, transform = "identity")
print(test)

pdf("residuals.pdf")
for (i in 1:(length(test)-2)){
    plot(test[i])
}
dev.off()