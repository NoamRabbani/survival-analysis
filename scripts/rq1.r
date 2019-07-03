library("survival")
library("survminer")

issues = read.csv("dataset/hbase_features_filtered.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$is_assigned <- factor(issues$is_assigned)
issues$issuetype <- factor(issues$issuetype)
issues$has_priority_change <- factor(issues$has_priority_change)
issues$has_desc_change <- factor(issues$has_desc_change)
issues$has_fix_change <- factor(issues$has_fix_change)

summary(issues)

# Univariate regression for priority
res.cox <- coxph(Surv(start, end, is_dead) ~ priority, data = issues)
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

# Univariate regression for is_assigned
res.cox <- coxph(Surv(start, end, is_dead) ~ is_assigned, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())
new_df <- with(issues,
                    data.frame(is_assigned = levels(is_assigned)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(0,1))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for issuetype
res.cox <- coxph(Surv(start, end, is_dead) ~ issuetype, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(issuetype = levels(issuetype)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(1,2,3,4,5,6,7))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for priority_change_count
res.cox <- coxph(Surv(start, end, is_dead) ~ has_priority_change, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(has_priority_change = levels(has_priority_change)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(0,1))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for has_desc_change
res.cox <- coxph(Surv(start, end, is_dead) ~ has_desc_change, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(has_desc_change = levels(has_desc_change)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(0,1))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for comment_count
res.cox <- coxph(Surv(start, end, is_dead) ~ comment_count, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for link_count
res.cox <- coxph(Surv(start, end, is_dead) ~ link_count, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for affect_count
res.cox <- coxph(Surv(start, end, is_dead) ~ affect_count, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for fix_count
res.cox <- coxph(Surv(start, end, is_dead) ~ fix_count, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for has_fix_change
res.cox <- coxph(Surv(start, end, is_dead) ~ has_fix_change, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(has_fix_change = levels(has_fix_change)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(0,1))
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)

# Univariate regression for fix_count
res.cox <- coxph(Surv(start, end, is_dead) ~ reporter_rep, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())
summary(res.cox)
test = cox.zph(res.cox, transform = "identity")
print(test)
