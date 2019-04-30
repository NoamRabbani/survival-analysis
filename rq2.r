library("survival")
library("survminer")

issues = read.csv("dataset/apache_features_filtered.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))

res.cox <- coxph(Surv(days, death) ~ priority, data = issues)
fit <- survfit(res.cox, data = issues)

test = cox.zph(res.cox, transform = "identity")
print(test)
png('rplot.png')
plot(test[i])
dev.off()