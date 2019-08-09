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


if (args[1] == "hbase"){
  f <- cph(Surv(start, end, is_dead) ~ 
          priority + 
          issuetype + 
          is_assigned + 
          rcs(comment_count,4) + 
          rcs(link_count, 4) +
          rcs(affect_count, 4) + 
          rcs(fix_count,4) + 
          has_priority_change + 
          has_desc_change + 
          rcs(has_fix_change,4) + 
          rcs(reporter_rep,4) + 
          rcs(assignee_workload,4),
          x=TRUE, y=TRUE, data=issues)
} else if (args[1] == "hadoop"){
  f <- cph(Surv(start, end, is_dead) ~ 
      priority + 
      issuetype + 
      is_assigned + 
      rcs(comment_count,4) + 
      rcs(link_count, 4) +
      rcs(affect_count, 4) + 
      fix_count + 
      has_priority_change + 
      has_desc_change + 
      has_fix_change + 
      rcs(reporter_rep,4) + 
      rcs(assignee_workload,4),
      x=TRUE, y=TRUE, data=issues)     
} else if (args[1] == "hive"){
  f <- cph(Surv(start, end, is_dead) ~ 
      priority + 
      issuetype + 
      is_assigned + 
      rcs(comment_count,4) + 
      rcs(link_count, 4) +
      rcs(affect_count, 4) + 
      fix_count + 
      has_priority_change + 
      has_desc_change + 
      has_fix_change + 
      rcs(reporter_rep,4) + 
      rcs(assignee_workload,4),
      x=TRUE, y=TRUE, data=issues)     
} else if (args[1] == "ignite"){
  f <- cph(Surv(start, end, is_dead) ~ 
      priority + 
      issuetype + 
      is_assigned + 
      rcs(comment_count,4) + 
      rcs(link_count, 4) +
      affect_count + 
      fix_count + 
      rcs(has_priority_change, 4) + 
      has_desc_change + 
      rcs(has_fix_change, 4) + 
      rcs(reporter_rep,4) + 
      rcs(assignee_workload,4),
      x=TRUE, y=TRUE, data=issues)     
}

w <- which.influence(f, cutoff=.035)
inf <- show.influence(w, issues)

path = here("artifacts", args[1], "outliers.csv")
write.csv(inf,path, quote=FALSE)
