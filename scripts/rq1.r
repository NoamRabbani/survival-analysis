library("survival")
library("survminer")

issues = read.csv("dataset/hbase_features_raw.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$assignee <- factor(issues$assignee)
issues$issuetype <- factor(issues$issuetype)
issues$priority_change_count <- factor(issues$priority_change_count)

# Univariate regression for priority
res.cox <- coxph(Surv(start, end, death) ~ priority, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(priority = levels(priority)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(3,1,2,4,5))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for assignee
res.cox <- coxph(Surv(start, end, death) ~ assignee, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())
new_df <- with(issues,
                    data.frame(assignee = levels(assignee)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(0,1))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for issuetype
res.cox <- coxph(Surv(start, end, death) ~ issuetype, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(issuetype = levels(issuetype)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(1,2,3,4,5,6,7,13,14))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for priority_change_count
res.cox <- coxph(Surv(start, end, death) ~ priority_change_count, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(priority_change_count = levels(priority_change_count)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(0,1))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

