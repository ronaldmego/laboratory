# Shiny_Snowflake_Data_Report

This project facilitates querying Snowflake databases and visualizing the results through a Shiny application. It leverages Python for executing queries and securely handling Snowflake credentials, and R/Shiny for the user interface and server logic.

## Overview

The architecture of this project combines Python and R technologies to offer a seamless data querying and visualization experience. Key components include:
- **Python Script (`python-script.py`)**: Handles querying Snowflake, utilizing `python-dotenv` for secure credential management.
- **.env File**: Stores Snowflake connection credentials securely.
- **R Shiny App Components (`UI.R`, `Server.R`, `App.R`)**: Define the user interface and server logic for the application.

## Features

- Securely query Snowflake databases using credentials stored in an `.env` file.
- Interactive user interface to specify query parameters.
- Visualization of query results within the Shiny app.
- Ability to download query results as CSV files.

## Getting started

### Requirements

- Python environment with `pandas`, `snowflake-connector-python`, and `python-dotenv` installed.
- R environment with `shiny` and `reticulate` packages installed.

### Quickstart

1. Ensure all required Python and R packages are installed.
2. Create an `.env` file in the project root with your Snowflake credentials.
3. Run the Shiny app by executing `shiny::runApp()` in the R console from the project directory.

### License

Copyright (c) 2024.