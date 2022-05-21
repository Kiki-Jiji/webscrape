#' The application User-Interface
#' 
#' @param request Internal parameter for `{shiny}`. 
#'     DO NOT REMOVE.
#' @import shiny
#' @noRd
app_ui <- function(request) {
  tagList(
    # Leave this function for adding external resources
    golem_add_external_resources(),
    # Your application UI logic 
    
    dashboardPage(skin = "purple",
      dashboardHeader(title = "Top books"),
      dashboardSidebar(
        sidebarMenu(
          menuItem("Books", tabName = "dashboard", icon = icon("dashboard")),
          menuItem("Price", tabName = "price", icon = icon("pound-sign")),
          menuItem("Words", tabName = "words", icon = icon("envelope-open-text")),
          menuItem("Authors", tabName = "authors", icon = icon("envelope-open-text"))
        )
      ),
      dashboardBody(
        tabItems(
          # First tab content
          tabItem(tabName = "dashboard",
                  fluidRow(
                    DT::DTOutput('tbl')
                  )
          ),
          
          tabItem(tabName = "price",
                  h2("Price"),
                  h4("Average Price per category in pound sterling"),
                  plotlyOutput("price", height = "600px")
          ),
          tabItem(tabName = "words",
                  h2("Words"),
                  numericInput('size', 'Number of top words', 20),
                  selectInput("shape", label = "Choose Shape", 
                              choices = c("circle", "star", "cardioid", "diamond", "triangle-forward", "triangle", "pentagon")),
                  selectInput("cat", label = "Choose Category", 
                              choices = "None"),
                  
                  wordcloud2::wordcloud2Output('wordcloud'),
                  hr(),
                  DT::DTOutput('top_words')
          ),
          tabItem(tabName = "authors",
                  h2("Authors"),
                  selectInput("author_cat", label = "Choose Category", 
                              choices = "None", multiple = TRUE),
                  dateRangeInput(inputId = "author_dr", label = "Date Range"),
                  plotlyOutput("author_pop", height = "600px")
          )
        )
    )
  )
  )
}

#' Add external Resources to the Application
#' 
#' This function is internally used to add external 
#' resources inside the Shiny application. 
#' 
#' @import shiny
#' @importFrom golem add_resource_path activate_js favicon bundle_resources
#' @noRd
golem_add_external_resources <- function(){
  
  add_resource_path(
    'www', app_sys('app/www')
  )
 
  tags$head(
    favicon(),
    bundle_resources(
      path = app_sys('app/www'),
      app_title = 'bookApp'
    )
    # Add here other external resources
    # for example, you can add shinyalert::useShinyalert() 
  )
}

