library(shiny)

# Fuente de los archivos de UI y servidor
source("ui.R")
source("server.R")

# Ejecutar la aplicación
shinyApp(ui = ui, server = server)