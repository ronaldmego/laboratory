import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load environment variables from .env file
load_dotenv()

# Configuración de la conexión
conn_params = {
    'host': os.getenv('HOST'),
    'port': os.getenv('PORT'),
    'dbname': os.getenv('DBNAME'),
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
}

# Print the connection parameters to debug
print(f"Host: {conn_params['host']}")
print(f"Port: {conn_params['port']}")
print(f"Database: {conn_params['dbname']}")
print(f"User: {conn_params['user']}")

# Conectar a Redshift y obtener datos
def get_data():
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        print("Conexión exitosa")

        # Crear un cursor
        cursor = conn.cursor()

        # Ejecutar la consulta (sin las columnas 'diferencia_dias' y 'status')
        query = "SELECT country, fuente, source, fecha FROM INFORMATION_DELIVERY_PROD.mfs_marketing.rm_lending_status;"
        cursor.execute(query)

        # Obtener los resultados y convertirlos a un DataFrame de Pandas
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        # Debug: print the number of rows fetched
        print(f"Number of rows fetched: {len(results)}")
        
        df = pd.DataFrame(results, columns=columns)

        # Debug: Mostrar el head del DataFrame obtenido
        print("Datos obtenidos de la base de datos:")
        print(df.head())

        return df

    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()  # Devolver un DataFrame vacío en caso de error

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Conexión cerrada")

# Calcular las columnas 'diferencia_dias' y 'status' localmente
def calculate_status(df):
    # Fecha actual en zona horaria GMT-5
    current_date = datetime.now(timezone(timedelta(hours=-5))).date()
    
    # Asegurarse de que la columna 'fecha' esté en formato de fecha
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    
    # Calcular diferencia en días
    df['diferencia_dias'] = (current_date - df['fecha']).apply(lambda x: x.days)
    
    # Calcular status según las reglas especificadas
    df['status'] = df.apply(lambda row: 1 if (row['source'] == 'MMB' and row['diferencia_dias'] == 0) or 
                                        (row['source'] != 'MMB' and row['diferencia_dias'] == 1) else 0, axis=1)
    
    # Debug: Mostrar el head del DataFrame después del cálculo
    print("Datos después de calcular 'diferencia_dias' y 'status':")
    print(df.head())

    return df

# Obtener y calcular los datos
df = get_data()
if not df.empty:
    df = calculate_status(df)
