#' The application server-side
#' 
#' @param input,output,session Internal parameters for {shiny}. 
#'     DO NOT REMOVE.
#' @import shiny
#' @noRd
app_server <- function( input, output, session ) {
  
  
  # Your application server logic 
  dollar_pound_rate =  0.81
  df = load_data()
  df = clean_data(df)
  
  # incorrect category labels deal with later
  df = df %>%
    dplyr::filter(date != "2022-05-07")
  
  available_categories <- unique(df$category)
  updateSelectInput(inputId = "cat", choices = c("all", available_categories), selected = "all")
  updateSelectInput(inputId = "author_cat", choices = c("all", available_categories), selected = "all")

  
  dates = unique(df$date)
  updateDateRangeInput(inputId = "author_dr", start = min(dates), end = max(dates))
  
  output$tbl = DT::renderDT(
    df, filter = "top", rownames = FALSE, options = list(pageLength = 5)
  )
  
  
  output$price = plotly::renderPlotly({
    
    plot_data = df %>%
      mutate(category = gsub("_", " ", category)) %>%
      group_by(category) %>%
      summarise(avg_price_pounds = mean(price, na.rm=TRUE)) %>%
      mutate(country = case_when(
        grepl("UK", category) ~ "UK",
        grepl("US", category) ~ "US"
      ),
      avg_price_pounds = ifelse(country == "US", avg_price_pounds* dollar_pound_rate, avg_price_pounds),
      avg_price_pounds = round(avg_price_pounds, 2))
    
    
    plotly::plot_ly(x = plot_data$category, y = plot_data$avg_price_pounds, color = plot_data$country, colors = c("Red", "Purple")) |> 
      plotly::add_bars() |> layout(plot_bgcolor='transparent') |>
      layout(paper_bgcolor='transparent', yaxis = list(title = "Average price in Pound Sterling")) 
    
    
    
  })
  
  output$author_pop = plotly::renderPlotly({
    
    
    plot_data = top_authors(df, input$author_cat, min_date = input$author_dr[1], max_date = input$author_dr[2])
    
    xform <- list(categoryorder = "array",
                  categoryarray = plot_data$author)
    
    plot_ly(
      x = plot_data$author,
      y = plot_data$n,
      name = "SF Zoo",
      type = "bar"
    ) %>% 
      layout(xaxis = xform)
    
  })
  
  
  top_words <- reactiveVal()   
  
  observeEvent(input$cat, {
    
    tw =  calculate_top_words(df, select_category = input$cat) 
    
    top_words(tw)
    
  })
  
  output$wordcloud = wordcloud2::renderWordcloud2({
    
    top_words() |>
    slice_head(n = input$size) |>
    wordcloud2::wordcloud2(shape = input$shape, size = 0.8)
    
  })
  
  
  
  output$top_words = DT::renderDT(
    top_words(), filter = "top", rownames = FALSE, options = list(pageLength = 5)
  )


    
}

