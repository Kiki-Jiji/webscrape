

files_to_ignore <- c( "books_data.csv", "dev", "dev.R", "dev2.R", "dev3.R")

SECRET =  Sys.getenv("SHINY_SECRET")
TOKEN = Sys.getenv("SHINY_TOKEN")
if(SECRET == "" | TOKEN == "") stop("SHINY_SECRET or SHINY_TOKEN env var not found")

rsconnect::setAccountInfo(name = 'kiki-jiji',
                          token = TOKEN,
                          secret = SECRET)


files_to_upload <- setdiff(dir(), files_to_ignore)
files_to_upload = c(files_to_upload, ".Renviron")

rsconnect::deployApp(appFiles = files_to_upload)
