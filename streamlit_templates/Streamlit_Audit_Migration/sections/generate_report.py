# sections/generate_report.py

import streamlit as st
import os
import datetime
import pandas as pd
from scripts.report_generation import generate_audit_report
from scripts.snowflake_connection import (
    check_table_exists_snowflake,
    get_total_record_count_snowflake,
    get_record_count_by_date_snowflake,
    get_columns_snowflake
)
from scripts.redshift_connection import (
    check_table_exists_redshift,
    get_total_record_count_redshift,
    get_record_count_by_date_redshift,
    get_columns_redshift
)
from sections.top_frequent_data import get_frequent_data_for_report
from utils.helpers import format_date, handle_error, run_parallel_queries

def generate_report(full_table_name, date_column, sample_date):
    st.sidebar.write(f"## Generando informe para la tabla **{full_table_name}**...")

    # Verificar existencia de la tabla en Snowflake
    try:
        snowflake_exists, snowflake_error = check_table_exists_snowflake(full_table_name)
        if snowflake_error:
            handle_error(snowflake_error, "Snowflake")
    except Exception as e:
        snowflake_exists, snowflake_error = False, str(e)
        handle_error(snowflake_error, "Snowflake")

    # Verificar existencia de la tabla en Redshift
    try:
        redshift_exists, redshift_error = check_table_exists_redshift(full_table_name)
        if redshift_error:
            handle_error(redshift_error, "Redshift")
    except Exception as e:
        redshift_exists, redshift_error = False, str(e)
        handle_error(redshift_error, "Redshift")

    # Obtener conteo total de registros en Snowflake
    try:
        snowflake_total, error_snowflake_total = get_total_record_count_snowflake(full_table_name)
        if error_snowflake_total:
            handle_error(error_snowflake_total, "Snowflake")
    except Exception as e:
        snowflake_total, error_snowflake_total = None, str(e)
        handle_error(error_snowflake_total, "Snowflake")

    # Obtener conteo total de registros en Redshift
    try:
        redshift_total, error_redshift_total = get_total_record_count_redshift(full_table_name)
        if error_redshift_total:
            handle_error(error_redshift_total, "Redshift")
    except Exception as e:
        redshift_total, error_redshift_total = None, str(e)
        handle_error(error_redshift_total, "Redshift")

    # Obtener conteo de registros por fecha (últimos 5 días)
    days = 5
    try:
        snowflake_dates_df, error_snowflake_dates = get_record_count_by_date_snowflake(
            table_name=full_table_name,
            date_column=date_column,
            sample_date=sample_date,
            days=days
        )
        if error_snowflake_dates:
            handle_error(error_snowflake_dates, "Snowflake")
            snowflake_dates_df = pd.DataFrame(columns=['extraction_date', 'count'])
        else:
            snowflake_dates_df['extraction_date'] = pd.to_datetime(snowflake_dates_df['extraction_date']).dt.date
    except Exception as e:
        snowflake_dates_df = pd.DataFrame(columns=['extraction_date', 'count'])
        handle_error(str(e), "Snowflake")

    try:
        redshift_dates_df, error_redshift_dates = get_record_count_by_date_redshift(
            table_name=full_table_name,
            date_column=date_column,
            sample_date=sample_date,
            days=days
        )
        if error_redshift_dates:
            handle_error(error_redshift_dates, "Redshift")
            redshift_dates_df = pd.DataFrame(columns=['extraction_date', 'count'])
        else:
            redshift_dates_df['extraction_date'] = pd.to_datetime(redshift_dates_df['extraction_date']).dt.date
    except Exception as e:
        redshift_dates_df = pd.DataFrame(columns=['extraction_date', 'count'])
        handle_error(str(e), "Redshift")

    # Crear el rango de fechas
    date_list = [sample_date - datetime.timedelta(days=x) for x in range(days)]
    date_list = sorted(date_list)
    date_df = pd.DataFrame({'extraction_date': date_list})

    # Procesar los DataFrames de Snowflake y Redshift
    def process_dates_df(df, source_name):
        if df is not None and not df.empty:
            df = pd.merge(date_df, df, on='extraction_date', how='left')
            df['count'] = df['count'].fillna(0).astype(int)
        else:
            df = date_df.copy()
            df['count'] = 0
        df = df.rename(columns={'count': f'count_{source_name}'})
        return df

    df_snowflake_full = process_dates_df(snowflake_dates_df, 'snowflake')
    df_redshift_full = process_dates_df(redshift_dates_df, 'redshift')

    # Combinar los DataFrames
    comparison_df = pd.merge(
        df_snowflake_full,
        df_redshift_full,
        on='extraction_date',
        how='outer'
    ).fillna(0)

    # Asegurarse de que los conteos son enteros
    comparison_df['count_snowflake'] = comparison_df['count_snowflake'].astype(int)
    comparison_df['count_redshift'] = comparison_df['count_redshift'].astype(int)

    # Añadir columna de comparación
    comparison_df['match'] = comparison_df['count_snowflake'] == comparison_df['count_redshift']

    # Obtener estructura de columnas en Snowflake
    try:
        columns_snowflake_df, error_snowflake_columns = get_columns_snowflake(full_table_name)
        if error_snowflake_columns:
            handle_error(error_snowflake_columns, "Snowflake")
    except Exception as e:
        columns_snowflake_df, error_snowflake_columns = None, str(e)
        handle_error(error_snowflake_columns, "Snowflake")

    # Obtener estructura de columnas en Redshift
    try:
        columns_redshift_df, error_redshift_columns = get_columns_redshift(full_table_name)
        if error_redshift_columns:
            handle_error(error_redshift_columns, "Redshift")
    except Exception as e:
        columns_redshift_df, error_redshift_columns = None, str(e)
        handle_error(error_redshift_columns, "Redshift")

    # Obtener los datos más frecuentes (top 3 por columna)
    try:
        frequent_data = get_frequent_data_for_report(
            full_table_name,
            date_column,
            sample_date,
            top_n=3
        )
    except Exception as e:
        frequent_data = None
        st.sidebar.error(f"Error al obtener los datos más frecuentes: {e}")

    # Generar el informe PDF
    try:
        report_path = generate_audit_report(
            table_name=full_table_name,
            analysis_date=format_date(sample_date),
            snowflake_exists=snowflake_exists,
            redshift_exists=redshift_exists,
            snowflake_total=snowflake_total,
            redshift_total=redshift_total,
            comparison_df=comparison_df,  # Pasar el DataFrame de comparación
            columns_snowflake_df=columns_snowflake_df,
            columns_redshift_df=columns_redshift_df,
            frequent_data=frequent_data  # Pasar los datos frecuentes
        )
        st.sidebar.success("El informe se ha generado exitosamente.")

        # Proporcionar enlace de descarga
        with open(report_path, "rb") as file:
            btn = st.sidebar.download_button(
                label="Descargar Informe PDF",
                data=file,
                file_name=os.path.basename(report_path),
                mime="application/pdf"
            )
    except Exception as e:
        st.sidebar.error(f"Error al generar el informe: {e}")