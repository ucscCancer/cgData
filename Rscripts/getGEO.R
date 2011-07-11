#!/usr/bin/env Rscript

library(GEOquery)
library(rjson)

args <- commandArgs(TRUE)

gsm <- getGEO(args[1])

write.table(Table(gsm), file = args[2], sep = "\t", row.names = FALSE, col.names = TRUE)

cat(toJSON(Meta(gsm)), file = paste(args[2], ".json", sep="") )
