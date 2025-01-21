library(shiny)
library(shinyWidgets)
library(DT)

# Definir la interfaz de usuario de la aplicación
ui <- fluidPage(
  titlePanel("Status de Fuentes Lending en Redshift"),
  fluidRow(
    column(12, 
           pickerInput(
             inputId = "fuentes",
             label = "Selecciona las fuentes a mostrar:",
             choices = NULL,
             selected = NULL,
             multiple = TRUE,
             options = list(
               `actions-box` = TRUE,
               `selected-text-format` = "count > 3",
               `count-selected-text` = "{0} fuentes seleccionadas",
               `none-selected-text` = "Ninguna fuente seleccionada"
             )
           )
    )
  ),
  fluidRow(
    column(12, 
           DTOutput("dataTable")
    )
  )
)
