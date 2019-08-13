require("survival")
require("survminer")
require("rms")
require("here")

# Parse arguments.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("At least one argument must be supplied", call.=FALSE)
}

# Load dataset.
filename <- paste(args[1], ".csv", sep="")
path <- here("reesjones2017cornell", "data", filename)
data <- read.csv(path, header = TRUE)
data$event <- 1
dd <- datadist(data); options(datadist = "dd")

f <- cph(Surv(timeOpen, event) ~ 
    issueCleanedBodyLen + 
    meanCommentSizeT + 
    log1p(nActorsT) + 
    log1p(nCommentsT) + 
    nCommitsByActorsT + 
    nCommitsByCreator + 
    nCommitsByUniqueActorsT +
    nCommitsInProject + 
    nCommitsProjectT + 
    nIssuesByCreator + 
    nIssuesByCreatorClosed + 
    nIssuesCreatedInProject + 
    nIssuesCreatedInProjectClosed + 
    nIssuesCreatedProjectClosedT + 
    nIssuesCreatedProjectT + 
    nLabelsT + 
    nSubscribedByT,
    x=TRUE, y=TRUE, data=data)

print(f, latex = TRUE, coefs = TRUE)

z <- predict(f, type="terms")
f.short <- coxph(Surv(timeOpen, event) ~ z, x=TRUE, y=TRUE, data=data)
zph <- cox.zph(f.short, transform="identity")
zph



