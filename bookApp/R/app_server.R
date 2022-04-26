#' The application server-side
#' 
#' @param input,output,session Internal parameters for {shiny}. 
#'     DO NOT REMOVE.
#' @import shiny
#' @noRd
app_server <- function( input, output, session ) {
  # Your application server logic 
  df = readr::read_csv("book_data.csv")

  output$tbl = DT::renderDT(
    df, filter = "top", rownames = FALSE, options = list(pageLength = 5)
  )
    
}

