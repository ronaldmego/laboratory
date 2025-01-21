# sections/compare_records_by_date.py

import streamlit as st
import pandas as pd
import datetime
from scripts.snowflake_connection import get_record_count_by_date_snowflake
from scripts.redshift_connection import get_record_count_by_date_redshift
from utils.helpers import display_dataframe, handle_error, format_date


def compare_records_by_date(full_table_name, date_column, sample_date):
    days = 5  # Número de días a comparar
    st.write(f"## Comparando registros por fecha para los últimos {days} días a partir de {sample_date.strftime('%Y-%m-%d')}")
    
    # Obtener el conteo de registros agrupados por fecha en Snowflake
    st.subheader("Registros por Fecha en Snowflake")
    try:
        df_snowflake_dates, error_snowflake_dates = get_record_count_by_date_snowflake(
            table_name=full_table_name,
            date_column=date_column,
            sample_date=sample_date,
            days=days
        )
        if error_snowflake_dates:
            handle_error(error_snowflake_dates, "Snowflake")
            df_snowflake_dates = pd.DataFrame(columns=['extraction_date', 'count'])
        else:
            # Asegurarse de que 'extraction_date' es de tipo fecha
            df_snowflake_dates['extraction_date'] = pd.to_datetime(df_snowflake_dates['extraction_date']).dt.date
            display_dataframe(df_snowflake_dates, "Registros por Fecha en Snowflake")
    except Exception as e:
        st.error(f"Error inesperado al consultar Snowflake: {e}")
        df_snowflake_dates = pd.DataFrame(columns=['extraction_date', 'count'])
    
    # Obtener el conteo de registros agrupados por fecha en Redshift
    st.subheader("Registros por Fecha en Redshift")
    try:
        df_redshift_dates, error_redshift_dates = get_record_count_by_date_redshift(
            table_name=full_table_name,
            date_column=date_column,
            sample_date=sample_date,
            days=days
        )
        if error_redshift_dates:
            handle_error(error_redshift_dates, "Redshift")
            df_redshift_dates = pd.DataFrame(columns=['extraction_date', 'count'])
        else:
            # Asegurarse de que 'extraction_date' es de tipo fecha
            df_redshift_dates['extraction_date'] = pd.to_datetime(df_redshift_dates['extraction_date']).dt.date
            display_dataframe(df_redshift_dates, "Registros por Fecha en Redshift")
    except Exception as e:
        st.error(f"Error inesperado al consultar Redshift: {e}")
        df_redshift_dates = pd.DataFrame(columns=['extraction_date', 'count'])
    
    # Comparar los registros por fecha
    st.markdown("---")
    st.header("Resultado de la Comparación por Fecha")
    
    # Crear un DataFrame con el rango de fechas
    date_list = [sample_date - datetime.timedelta(days=x) for x in range(days)]
    date_list = sorted(date_list)
    date_df = pd.DataFrame({'extraction_date': date_list})
    
    # Unir los conteos de Snowflake al DataFrame de fechas
    df_snowflake_full = pd.merge(
        date_df,
        df_snowflake_dates,
        on='extraction_date',
        how='left'
    )
    df_snowflake_full['count'] = df_snowflake_full['count'].fillna(0).astype(int)
    df_snowflake_full = df_snowflake_full.rename(columns={'count': 'count_snowflake'})
    
    # Unir los conteos de Redshift al DataFrame de fechas
    df_redshift_full = pd.merge(
        date_df,
        df_redshift_dates,
        on='extraction_date',
        how='left'
    )
    df_redshift_full['count'] = df_redshift_full['count'].fillna(0).astype(int)
    df_redshift_full = df_redshift_full.rename(columns={'count': 'count_redshift'})
    
    # Combinar ambos DataFrames en uno solo
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
    
    # Mostrar la comparación
    st.write("## Comparación de Registros por Fecha")
    st.dataframe(comparison_df)
    
    # Verificar si los conteos coinciden por fecha
    if comparison_df['match'].all():
        st.success("Los conteos de registros por fecha coinciden en ambas bases de datos.")
    else:
        st.warning("Existen discrepancias en los conteos de registros por fecha entre Snowflake y Redshift.")