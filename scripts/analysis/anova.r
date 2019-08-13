require("survival")
require("survminer")
require("rms")
require("here")
require("broom")

args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)!=1) {
  stop("At least one argument must be supplied", call.=FALSE)
}

path = here("artifacts", args[1], "cph_model.Rdata")
load(path)

a <- anova(f, test='Chisq')
a

path = here("artifacts", args[1], "anova.csv")
write.table(tidy(a), path, quote = FALSE, sep=";", row.names=FALSE)