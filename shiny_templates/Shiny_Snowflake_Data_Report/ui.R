library(shiny)

ui <- fluidPage(
  titlePanel("IFRS9 Data Report"),
  sidebarLayout(
    sidebarPanel(
      dateInput("dateStart", "Start Date"),
      dateInput("dateEnd", "End Date"),
      actionButton("runQuery", "Run Query")
    ),
    mainPanel(
      tableOutput("queryResults"),
      downloadButton("downloadData", "Download CSV")
    )
  )
)