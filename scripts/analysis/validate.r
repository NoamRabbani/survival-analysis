require("survival")
require("survminer")
require("rms")
require("here")

args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)!=1) {
  stop("At least one argument must be supplied", call.=FALSE)
}


path = here("datasets", args[1], "imputed.csv")
issues = read.csv(path, header = TRUE, sep="\t")

path = here("artifacts", args[1], "cph_model.Rdata")
load(path)


# get median resolution time of issues
resolution_rows = subset(issues, is_dead == 1)
median_resolution_time = median(resolution_rows$end)

v <- validate(f, u=median_resolution_time, B=1)
v
path = here("artifacts", args[1], "validate.csv")
write.table(v, path, quote = FALSE, sep="\t", row.names=FALSE)