#!/usr/bin/env Rscript
# Fetch public MIT-licensed epldata R tables and derive actual PL appearances.
# The repository's README warns that some historical data may contain errors.
dir.create("output/epldata", recursive=TRUE, showWarnings=FALSE)
base <- "https://raw.githubusercontent.com/pssguy/epldata/master/data/"
tables <- c("players","player_team","player_game","game_team","games")
for (tbl in tables) {
  dest <- tempfile(fileext=".rda")
  download.file(paste0(base,tbl,".rda"),dest,mode="wb",quiet=TRUE)
  e <- new.env(parent=emptyenv())
  load(dest,envir=e)
  stopifnot(exists(tbl,envir=e,inherits=FALSE))
  write.csv(get(tbl,envir=e),paste0("output/epldata/",tbl,".csv"),row.names=FALSE,na="")
}
