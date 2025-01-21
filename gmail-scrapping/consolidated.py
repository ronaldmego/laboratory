import pandas as pd
import glob

# Rutas relativas de los archivos CSV para Scotiabank y Bgeneral
scotia_path = "download/scotia_transacciones_*.csv"
bgeneral_path = "download/transacciones_*.csv"
category_file = "auxiliar/category.csv"

# Cargar todos los archivos CSV de Scotiabank en un dataframe
scotia_files = glob.glob(scotia_path)
scotia_data_list = []

for file in scotia_files:
    data = pd.read_csv(file)
    data['banco'] = 'Scotiabank'  # Agregar columna para identificar el banco
    scotia_data_list.append(data)

# Concatenar todos los dataframes de Scotiabank
scotia_data = pd.concat(scotia_data_list, ignore_index=True)

# Cargar todos los archivos CSV de Bgeneral en un dataframe
bgeneral_files = glob.glob(bgeneral_path)
bgeneral_data_list = []

for file in bgeneral_files:
    data = pd.read_csv(file)
    data['banco'] = 'Bgeneral'  # Agregar columna para identificar el banco
    bgeneral_data_list.append(data)

# Concatenar todos los dataframes de Bgeneral
bgeneral_data = pd.concat(bgeneral_data_list, ignore_index=True)

# Consolidar los datos de ambos bancos
consolidated_data = pd.concat([scotia_data, bgeneral_data], ignore_index=True)

# Cargar el archivo de categorías y limpiar espacios
category_data = pd.read_csv(category_file)
category_data['Store'] = category_data['Store'].str.strip()  # Limpiar espacios al inicio y final

# Crear un diccionario para las categorías
category_dict = dict(zip(category_data['Store'], category_data['Cat']))

# Limpiar espacios en el dataframe consolidado
consolidated_data['store'] = consolidated_data['store'].str.strip()  # Limpiar espacios

# Asignar categorías al archivo consolidado
consolidated_data['category'] = consolidated_data['store'].map(category_dict).fillna('desconocido')

# Guardar el archivo consolidado con categorías
output_file = "auxiliar/consolidated_transacciones_con_categoria.csv"
consolidated_data.to_csv(output_file, index=False)

print(f"Datos consolidados con categorías guardados en: {output_file}")