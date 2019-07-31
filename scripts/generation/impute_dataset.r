require(rms)
require("here")

args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)==0) {
  stop("At least one argument must be supplied", call.=FALSE)
}

path = here("datasets", args[1], "filtered.csv")
path
issues = read.csv(path, header = TRUE, sep="\t")

# Apply right data types to columns.
issues$priority <- factor(issues$priority)
issues$issuetype <- factor(issues$issuetype)
issues$is_assigned <- factor(issues$is_assigned)

if (args[1] == "hbase"){
  w <- transcan (~ 
      priority + 
      issuetype + 
      is_assigned + 
      comment_count + 
      link_count + 
      affect_count + 
      fix_count + 
      # has_priority_change + 
      # has_fix_change + 
      # has_desc_change + 
      reporter_rep + 
      assignee_workload,
      imputed=TRUE ,data = issues , pl = FALSE , pr = FALSE )  
} else if (args[1] == "hadoop"){
  w <- transcan (~ 
      priority + 
      issuetype + 
      is_assigned + 
      comment_count + 
      link_count + 
      affect_count + 
      # fix_count + 
      # has_priority_change + 
      # has_fix_change + 
      # has_desc_change + 
      reporter_rep + 
      assignee_workload,
      imputed=TRUE ,data = issues , pl = FALSE , pr = FALSE )
}

attach(issues)
issues$assignee_workload <- impute(w, assignee_workload, data=issues)
issues$assignee_workload <- round(issues$assignee_workload)
summary(issues)

path = here("datasets", args[1], "imputed.csv")
write.table(issues, path, quote = FALSE, sep="\t", row.names=FALSE)

