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
units(start) <- "Day"
units(end) <- "Day"

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
}


print(f, latex = TRUE, coefs = TRUE)

z <- predict(f, type="terms")
f.short <- coxph(Surv(start, end, is_dead) ~ z, x=TRUE, y=TRUE, data=issues)
zph <- cox.zph(f.short, transform="identity")
zph

path = here("artifacts", args[1], "proportional_hazards.pdf")
pdf(path)
for ( i in 1:(length(zph)*2)){
    plot(zph[i], log="x", col="red")
}
dev.off()

# zph <- as.data.frame(print(zph))

# path = here("artifacts", args[1], "proportional_hazards.csv")
# write.table(zph, path, quote = FALSE, sep="\t", row.names=FALSE)