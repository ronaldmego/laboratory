library(shiny)
library(reticulate)
library(DT)

# Configurar reticulate para usar el entorno virtual con la ruta completa
use_virtualenv("C:/Users/ronal/OneDrive/Documentos/APPs/Statuscargas_Rstudio/venvr", required = TRUE)

# Usar el paquete reticulate para importar funciones de Python
source_python("python_script.py")

# Definir la lógica del servidor
server <- function(input, output, session) {
  # Llamar a la función de Python para obtener los datos
  df <- get_data()
  df <- calculate_status(df)
  
  # Establecer las opciones por defecto excluyendo las fuentes especificadas
  default_fuentes <- setdiff(unique(df$fuente), c("LENDING_RISK_PY_SCORE_V2", "INFO_DYN_PY_PAYMENTOFFERS"))
  
  # Actualizar las opciones del pickerInput
  updatePickerInput(session, "fuentes", choices = unique(df$fuente), selected = default_fuentes)
  
  # Filtrar los datos basados en la selección del usuario
  filtered_data <- reactive({
    req(input$fuentes)
    df[df$fuente %in% input$fuentes, ]
  })
  
  # Renderizar el DataTable
  output$dataTable <- renderDT({
    datatable(filtered_data(), options = list(pageLength = 14)) %>%
      formatStyle(
        'status',
        target = 'row',
        backgroundColor = styleEqual(c(1, 0), c('lightgreen', 'lightcoral'))
      )
  })
}