library("survival")
library("survminer")

issues = read.csv("dataset/apache_features_filtered.csv", header = TRUE, sep="\t")

####################################
# Univariate cox regression analysis
####################################

covariates <- c("priority", "issuetype", "fixversions", "issuelinks")
univ_formulas <- sapply(covariates,
                        function(x) as.formula(paste('Surv(days, death)~', x)))
                        
univ_models <- lapply( univ_formulas, function(x){coxph(x, data = issues)})
univ_results <- lapply(univ_models,
                       function(x){ 
                          x <- summary(x)
                          p.value<-signif(x$wald["pvalue"], digits=2)
                          wald.test<-signif(x$wald["test"], digits=2)
                          beta<-signif(x$coef[1], digits=2);
                          HR <-signif(x$coef[2], digits=2);
                          HR.confint.lower <- signif(x$conf.int[,"lower .95"], 2)
                          HR.confint.upper <- signif(x$conf.int[,"upper .95"],2)
                          HR <- paste0(HR, " (", 
                                       HR.confint.lower, "-", HR.confint.upper, ")")
                          res<-c(beta, HR, wald.test, p.value)
                          names(res)<-c("beta", "HR (95% CI for HR)", "wald.test", 
                                        "p.value")
                          return(res)
                         })
res <- t(as.data.frame(univ_results, check.names = FALSE))
as.data.frame(res)

####################################
# Multivariate cox regression analysis
####################################

res.cox <- coxph(Surv(days, death) ~ priority + issuetype + fixversions, data = issues)
summary(res.cox)

# Plot the baseline survival function
fit <- survfit(res.cox, data = issues)
ggsurvplot(fit, palette = "#2E9FDF", ggtheme = theme_minimal())

# Plot survival depending on each covariate
new_df <- with(issues,
                    data.frame(priority = c(1,2,3,4,5),
                               issuetype = c(1,1,1,1,1),
                               fixversions = c(0,0,0,0,0)
                              )
                    )              
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, conf.int = TRUE, legend.labs=c("Priority=1", "Priority=2", "Priority=3", "Priority=4", "Priority=5"),
           ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(priority = c(1,1,1,1,1),
                               issuetype = c(1,2,3,4,5),
                               fixversions = c(0,0,0,0,0)
                              )
                    )              
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, conf.int = TRUE, legend.labs=c("Issuetype=1", "Issuetype=2", "Issuetype=3", "Issuetype=4", "Issuetype=5"),
           ggtheme = theme_minimal())

new_df <- with(issues,
                    data.frame(priority = c(1,1,1,1,1),
                               issuetype = c(1,1,1,1,1),
                               fixversions = c(0,1,2,3,4)
                              )
                    )              
fit <- survfit(res.cox, data = issues, newdata = new_df)
ggsurvplot(fit, conf.int = TRUE, legend.labs=c("Fixversions=0", "Fixversions=1", "Fixversions=2", "Fixversions=3", "Fixversions=4"),
           ggtheme = theme_minimal())


test = cox.zph(res.cox)
ggcoxzph(test)
print(test)

# Calculate and plot linearity two at a time
# par(mfrow=c(2, 2))
# res <- residuals(res.cox, type="martingale")
# X <- as.matrix(issues[, c("no_fixversion", "no_issuelink")]) # matrix of covariates
# par(mfrow=c(2, 2))

# for (j in 1:2) { # residual plots
# plot(X[, j], res, xlab=c("no_fixversion", "no_issuelink")[j], ylab="residuals")
# abline(h=0, lty=2)
# lines(lowess(X[, j], res, iter=0))
# }

# b <- coef(res.cox)[c(2,3)] # regression coefficients
# for (j in 1:2) { # component-plus-residual plots
# plot(X[, j], b[j]*X[, j] + res, xlab=c("no_fixversion", "no_issuelink")[j],
# ylab="component+residual")
# abline(lm(b[j]*X[, j] + res ~ X[, j]), lty=2)
# lines(lowess(X[, j], b[j]*X[, j] + res, iter=0))
# }

# new_df <- with(issues,
#                     data.frame(priority = c(1,1,1,1),
#                                reporterrep = c(1,2,3,4),
#                                no_fixversion = c(0,0,0,0),
#                                no_issuelink = c(0,0,0,0)
#                               )
#                     )              
# fit <- survfit(res.cox, data = issues, newdata = new_df)
# ggsurvplot(fit, conf.int = TRUE, legend.labs=c("ReporterRep=1", "ReporterRep=2", "ReporterRep=3", "ReporterRep=4"),
#            ggtheme = theme_minimal())

# new_df <- with(issues,
#                     data.frame(priority = c(1,1,1,1),
#                                reporterrep = c(1,1,1,1),
#                                no_fixversion = c(0,1,2,3),
#                                no_issuelink = c(0,0,0,0)
#                               )
#                     )              
# fit <- survfit(res.cox, data = issues, newdata = new_df)
# ggsurvplot(fit, conf.int = TRUE, legend.labs=c("no_fixversion=0", "no_fixversion=1", "no_fixversion=2", "no_fixversion=3"),
#            ggtheme = theme_minimal())




                    