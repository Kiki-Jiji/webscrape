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
    
    dashboardPage(
      dashboardHeader(title = "Top books"),
      dashboardSidebar(
        sidebarMenu(
          menuItem("Books", tabName = "dashboard", icon = icon("dashboard")),
          menuItem("Widgets", tabName = "widgets", icon = icon("th")),
          menuItem("Price", tabName = "price", icon = icon("th")),
          menuItem("Words", tabName = "words", icon = icon("th"))
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
          
          # Second tab content
          tabItem(tabName = "widgets",
                  h2("Widgets tab content"),
                  plotlyOutput("stars")
                  
          ),
          tabItem(tabName = "price",
                  h2("Price"),
                  plotlyOutput("price")
          ),
          tabItem(tabName = "words",
                  h2("Words"),
                  numericInput('size', 'Minimum Occurences', 10),
                  selectInput("shape", label = "Choose Shape", 
                              choices = c("circle", "star", "cardioid", "diamond", "triangle-forward", "triangle", "pentagon")),
                  wordcloud2::wordcloud2Output('wordcloud'),
                  hr(),
                  DT::DTOutput('top_words')
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

