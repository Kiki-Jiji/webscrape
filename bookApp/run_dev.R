# Set options here
options(golem.app.prod = FALSE) # TRUE = production mode, FALSE = development mode

# Detach all loaded packages and clean your environment
golem::detach_all_attached()

# Document and reload your package2
library(shinydashboard)
library(dplyr)
library(ggplot2)
library(plotly)
library(shiny)
golem::document_and_reload()

# Run the application
run_app()