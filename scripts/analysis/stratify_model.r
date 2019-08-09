require("survival")
require("survminer")
require("rms")
require("here")

args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)==0) {
  stop("At least one argument must be supplied", call.=FALSE)
}

path = here("datasets", args[1], "imputed.csv")
path
issues = read.csv(path, header = TRUE, sep="\t")

# Apply right data types to columns.
issues$priority <- factor(issues$priority)
issues$issuetype <- factor(issues$issuetype)
issues$is_assigned <- factor(issues$is_assigned)

dd <- datadist(issues); options(datadist = "dd")

if (args[1] == "hbase"){
issues <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(15, 75, 200), episode="tgroup")
dd <- datadist(issues); options(datadist = "dd")
f <- cph(Surv(start, end, is_dead) ~ 
  priority + 
  issuetype + 
  is_assigned + 
  rcs(comment_count,4)*strat(tgroup) + 
  rcs(link_count, 4)*strat(tgroup) +
  rcs(affect_count, 4) + 
  rcs(fix_count,4)*strat(tgroup) + 
  has_priority_change*strat(tgroup) + 
  has_desc_change + 
  rcs(has_fix_change,4)*strat(tgroup) + 
  rcs(reporter_rep,4) + 
  rcs(assignee_workload,4)*strat(tgroup),
  x=TRUE, y=TRUE, surv=TRUE, data=issues)
} else if (args[1] == "hadoop"){
issues <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(10, 20, 100, 150, 200), episode="tgroup")
dd <- datadist(issues); options(datadist = "dd")
f <- cph(Surv(start, end, is_dead) ~ 
  priority*strat(tgroup) + 
  issuetype*strat(tgroup) + 
  is_assigned*strat(tgroup) + 
  rcs(comment_count,4)*strat(tgroup) + 
  rcs(link_count, 4)*strat(tgroup) +
  rcs(affect_count, 4) + 
  fix_count*strat(tgroup) + 
  has_priority_change + 
  has_desc_change + 
  has_fix_change*strat(tgroup) + 
  rcs(reporter_rep,4) + 
  rcs(assignee_workload,4),
  x=TRUE, y=TRUE, surv=TRUE, data=issues)        
} else if (args[1] == "hive"){
issues <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(7, 15, 75, 200), episode="tgroup")
dd <- datadist(issues); options(datadist = "dd")
f <- cph(Surv(start, end, is_dead) ~ 
  priority+ 
  issuetype + 
  is_assigned + 
  rcs(comment_count,4) + 
  rcs(link_count, 4)*strat(tgroup) +
  rcs(affect_count, 4)*strat(tgroup) + 
  fix_count*strat(tgroup) + 
  has_priority_change + 
  has_desc_change + 
  has_fix_change*strat(tgroup) + 
  rcs(reporter_rep,4) + 
  rcs(assignee_workload,4),
  x=TRUE, y=TRUE, surv=TRUE, data=issues)        
}


print(f, latex = TRUE, coefs = TRUE)
path = here("artifacts", args[1], "cph_model.Rdata")
save(f, file=path)


# z <- predict(f, type="terms")
# f.short <- coxph(Surv(start, end, is_dead) ~ z, x=TRUE, y=TRUE, data=issues)
zph <- cox.zph(f, transform="identity")
zph

path = here("artifacts", args[1], "stratified_proportional_hazards.pdf")
pdf(path)
for ( i in 1:(length(zph)*2)){
    plot(zph[i], col="red")
    grid(20, 20, lwd = 2)
}
dev.off()



# zph <- as.data.frame(print(zph))
# path = here("artifacts", args[1], "proportional_hazards.csv")
# write.table(zph, path, quote = FALSE, sep="\t", row.names=FALSE)