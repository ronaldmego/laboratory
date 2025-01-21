library(shiny)
library(reticulate)

# Source UI and server logic
source("ui.R")
source("server.R")

# Define and run the Shiny application
shinyApp(ui = ui, server = server)