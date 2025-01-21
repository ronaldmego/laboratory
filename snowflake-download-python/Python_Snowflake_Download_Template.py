import snowflake.connector
import pandas as pd
import os
from tqdm import tqdm
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def query_snowflake():
    user = os.getenv('USER_SNOW')
    password = os.getenv('PASSWORD_SNOW')
    account = os.getenv('ACCOUNT_SNOW')
    warehouse = os.getenv('WAREHOUSE_SNOW')
    database = os.getenv('DATABASE_SNOW')
    schema = os.getenv('SCHEMA_SNOW')

    ctx = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema
    )

    cs = ctx.cursor()

    query = """
    SELECT * FROM TABLE
    """

    cs.execute(query)
    df = pd.DataFrame.from_records(iter(cs), columns=[x[0] for x in cs.description])

    # Usar tqdm para mostrar una barra de progreso mientras se cargan los datos
    for _ in tqdm(df.itertuples(), total=len(df), desc="Descargando datos"):
        pass  # La barra de progreso se actualiza aquí

    cs.close()
    ctx.close()

    return df

# Llamar a la función para obtener los datos
df = query_snowflake()

# Guardar el DataFrame en un archivo CSV
df.to_csv('datos_descargados.csv', index=False)
print("Datos guardados en 'datos_descargados.csv'")