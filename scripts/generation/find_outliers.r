require("survival")
require("survminer")
require("rms")
require("here")

args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)==0) {
  stop("At least one argument must be supplied", call.=FALSE)
}

path = here("datasets", args[1], "survsplit.csv")
issues = read.csv(path, header = TRUE, sep="\t")
summary(issues)

# transform columns into factors with the modes as first value
issues$priority <- factor(issues$priority, levels=c(3,1,2,4,5))
issues$issuetype <- factor(issues$issuetype, levels=c(1,2,3,4,5,6,7))
issues$is_assigned <- factor(issues$is_assigned)

attach(issues)

dd <- datadist(issues); options(datadist = 'dd')
units(start) <- 'Day'
units(end) <- 'Day'

S <- Surv(start, end, is_dead)


f <- cph(S ~ priority + issuetype + is_assigned + rcs(comment_count, 4) + rcs(link_count, 4) +
        rcs(affect_count, 4) + fix_count + has_priority_change + 
        has_desc_change + has_fix_change + rcs(reporter_rep,4) + rcs(assignee_workload,4),
        x=TRUE, y=TRUE)

w <- which.influence(f, cutoff=.035)
inf <- show.influence(w, issues)

path = here("artifacts", args[1], "outliers.csv")
write.csv(inf,path, quote=FALSE)
