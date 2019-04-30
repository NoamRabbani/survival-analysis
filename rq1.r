library("survival")
library("survminer")

issues = read.csv("dataset/apache_features_filtered.csv", header = TRUE, sep="\t")

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))

res.cox <- coxph(Surv(days, death) ~ priority, data = issues)
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, censor = FALSE, palette = "#2E9FDF", ggtheme = theme_minimal())

priority_df <- with(issues,
                    data.frame(priority = levels(priority)
                              )
                    )
fit <- survfit(res.cox, data = issues, newdata = priority_df)
ggsurvplot(fit, censor = FALSE, legend.labs=c(3,1,2,4,5))

summary(res.cox)

####################################
# Univariate cox regression analysis
####################################

# covariates <- c("issuetype", "fixversions", "issuelinks")
# univ_formulas <- sapply(covariates,
#                         function(x) as.formula(paste('Surv(days, death)~', x)))
                        
# univ_models <- lapply( univ_formulas, function(x){coxph(x, data = issues)})
# univ_results <- lapply(univ_models,
#                        function(x){ 
#                           x <- summary(x)
#                           p.value<-signif(x$wald["pvalue"], digits=2)
#                           wald.test<-signif(x$wald["test"], digits=2)
#                           beta<-signif(x$coef[1], digits=2);
#                           HR <-signif(x$coef[2], digits=2);
#                           HR.confint.lower <- signif(x$conf.int[,"lower .95"], 2)
#                           HR.confint.upper <- signif(x$conf.int[,"upper .95"],2)
#                           HR <- paste0(HR, " (", 
#                                        HR.confint.lower, "-", HR.confint.upper, ")")
#                           res<-c(beta, HR, wald.test, p.value)
#                           names(res)<-c("beta", "HR (95% CI for HR)", "wald.test", 
#                                         "p.value")
#                           return(res)
#                          })
# res <- t(as.data.frame(univ_results, check.names = FALSE))
# as.data.frame(res)
