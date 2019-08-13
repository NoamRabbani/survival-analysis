require("survival")
require("survminer")
require("rms")
require("here")

args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)==0) {
  stop("At least one argument must be supplied", call.=FALSE)
}

path = here("datasets", args[1], "raw.csv")
issues = read.csv(path, header = TRUE, sep="\t")

# Apply right data types to columns.
issues$priority <- factor(issues$priority)
issues$issuetype <- factor(issues$issuetype)
issues$is_assigned <- factor(issues$is_assigned)

issues2 <- survSplit(Surv(start, end, is_dead) ~., data=issues, cut=c(365), episode="should_censor")
issues2$should_censor <- issues2$should_censor - 1

path = here("datasets", args[1], "survsplit.csv")
write.table(issues2, path, quote=FALSE, sep="\t", row.names=FALSE)