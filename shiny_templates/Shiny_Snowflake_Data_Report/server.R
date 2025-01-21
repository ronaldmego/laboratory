library(shiny)
library(reticulate)

# Specify the correct path to the Python executable
use_python("D:/Apps/gpt-pilot/workspace/Shiny_Snowflake_Data_Report/new_virtual_environment/Scripts/python.exe", required = TRUE)

source_python("python-script-IFRS9.py")

server <- function(input, output) {
  observeEvent(input$runQuery, {
    req(input$dateStart, input$dateEnd)
    
    start_date <- format(input$dateStart, "%Y-%m-%d")
    end_date <- format(input$dateEnd, "%Y-%m-%d")
    
    cat("Querying Snowflake for sample data between", start_date, "and", end_date, "\n")
    
    tryCatch({
      # Fetch only a sample of the data for UI display
      df_py_sample <- py$query_snowflake_sample(start_date, end_date)
      
      # Convert the Python dictionary to an R data frame
      df_r_sample <- as.data.frame(df_py_sample, stringsAsFactors = FALSE)
      
      # Ensure all columns are correctly formatted
      df_r_sample[] <- lapply(df_r_sample, function(x) ifelse(is.character(x), as.character(x), x))
      
      output$queryResults <- renderTable({
        cat("Successfully retrieved sample data from Snowflake.\n")
        df_r_sample
      })
    }, error = function(e) {
      cat("Failed to query Snowflake for sample data: ", e$message, "\n")
      cat("Error trace: ", deparse(e$call), "\n")
      stop("Error in querying Snowflake for sample data: ", e$message)
    })
  })
  
  output$downloadData <- downloadHandler(
    filename = function() { paste("data-", Sys.Date(), ".csv", sep="") },
    content = function(file) {
      start_date <- format(input$dateStart, "%Y-%m-%d")
      end_date <- format(input$dateEnd, "%Y-%m-%d")
      
      cat("Preparing full data for download between", start_date, "and", end_date, "\n")
      
      tryCatch({
        # Fetch the full dataset for download
        df_py_full <- py$query_snowflake(start_date, end_date)
        # Convert the Python dictionary to an R data frame before writing to CSV
        df_r_full <- as.data.frame(df_py_full, stringsAsFactors = FALSE)
        # Ensure all columns are correctly formatted
        df_r_full[] <- lapply(df_r_full, function(x) ifelse(is.character(x), as.character(x), x))
        write.csv(df_r_full, file, row.names = FALSE)
        cat("Full data successfully prepared for download.\n")
      }, error = function(e) {
        cat("Failed to prepare full data for download: ", e$message, "\n")
        cat("Error trace: ", deparse(e$call), "\n")
        stop("Error in preparing full data for download: ", e$message)
      })
    }
  )
}