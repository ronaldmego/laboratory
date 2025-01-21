import os
import pdfplumber
import re
import pandas as pd

# Función para extraer texto de un PDF usando pdfplumber
def extract_text_with_pdfplumber(pdf_file_path):
    with pdfplumber.open(pdf_file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Función para extraer las transacciones, incluyendo pagos y referencia, desde el PDF usando pdfplumber
def extract_transactions_with_reference(pdf_file_path):
    with pdfplumber.open(pdf_file_path) as pdf:
        transactions = []
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            for line in lines:
                # Revisar si la línea parece una transacción con el patrón básico o un pago
                if re.match(r'\d{2}/\d{2}/\d{4}\s+\d{2}/\d{2}/\d{4}\s+\d+', line):
                    transactions.append(line)
    return transactions

# Función para convertir las líneas de transacciones en un DataFrame, capturando montos, referencia, comas y paréntesis
def parse_transaction_lines_with_reference(lines):
    # Patrón ajustado para capturar la referencia y los montos al final de la línea, incluyendo montos entre paréntesis
    transaction_pattern = r'(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+(.+?)\s+(\(?\d[\d,]*\.\d{2}\)?)$'
    transactions = [re.findall(transaction_pattern, line) for line in lines]
    transactions = [t[0] for t in transactions if t]  # Filtrar transacciones válidas
    
    df = pd.DataFrame(transactions, columns=['Fecha_Transaccion', 'Fecha_Registro', 'Referencia', 'Descripcion', 'Monto'])
    
    # Limpiar los montos, quitando paréntesis y convertir a número
    df['Monto'] = df['Monto'].str.replace(r'[\(\)]', '', regex=True)
    df['Monto'] = pd.to_numeric(df['Monto'].str.replace(',', ''), errors='coerce')
    
    df['Fecha_Transaccion'] = pd.to_datetime(df['Fecha_Transaccion'], format='%d/%m/%Y')
    df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'], format='%d/%m/%Y')
    
    return df

# Función para aplicar signo negativo a los montos de pagos
def apply_negative_sign_to_payments(df):
    # Considerar pagos que típicamente restan deuda
    df['Monto'] = df.apply(lambda row: -row['Monto'] if "Pago de tarjeta" in row['Descripcion'] or "ITP" in row['Descripcion'] else row['Monto'], axis=1)
    return df

# Función para agregar las columnas de Producto y Fecha de Emisión
def add_pdf_metadata(df, pdf_file_name):
    # Extraer producto y fecha de emisión del nombre del archivo
    product, date = pdf_file_name.split('_')
    date = pd.to_datetime(date, format='%d%m%Y')
    
    # Agregar columnas al DataFrame
    df['Producto'] = product
    df['Fecha_Emision'] = date
    return df

# Directorios de entrada y salida
input_directory = r"C:\Users\ronal\OneDrive\Documentos\FINANZAS PERSONALES\Estados de cuenta TC\Scotiabank"
output_directory = r"C:\Users\ronal\OneDrive\Documentos\FINANZAS PERSONALES\Estados de cuenta TC\Output"
output_csv_path = os.path.join(output_directory, "transacciones_consolidadas.csv")

# Listas para almacenar los resultados
successful_files = []
failed_files = []
all_transactions = []

# Recorrer todos los archivos PDF en el directorio de entrada uno por uno
for filename in os.listdir(input_directory):
    if filename.endswith(".pdf"):
        pdf_file_path = os.path.join(input_directory, filename)
        try:
            print(f"Procesando {filename}...")

            # Extraer las transacciones del PDF actual
            transaction_lines = extract_transactions_with_reference(pdf_file_path)
            
            # Crear el DataFrame a partir de las líneas de transacciones extraídas
            df_transactions = parse_transaction_lines_with_reference(transaction_lines)
            
            # Aplicar el ajuste para que los pagos tengan signo negativo
            df_transactions_adjusted = apply_negative_sign_to_payments(df_transactions)
            
            # Agregar las columnas Producto y Fecha de Emisión
            df_transactions_final = add_pdf_metadata(df_transactions_adjusted, filename.replace('.pdf', ''))

            successful_files.append(filename)
            all_transactions.append(df_transactions_final)
            print(f"{filename} procesado correctamente.")
            print(df_transactions_final.head())  # Muestra las primeras filas como referencia

        except Exception as e:
            failed_files.append((filename, str(e)))
            print(f"Error procesando {filename}: {e}")

# Concatenar todos los DataFrames exitosos en uno solo
if all_transactions:
    df_consolidated = pd.concat(all_transactions, ignore_index=True)

    # Guardar el DataFrame consolidado en un archivo CSV
    df_consolidated.to_csv(output_csv_path, index=False)
    print(f"\nTransacciones consolidadas y guardadas en {output_csv_path}")

# Generar el informe final
print("\n--- Resumen del procesamiento ---")
print(f"\nArchivos procesados correctamente ({len(successful_files)}):")
for file in successful_files:
    print(f"- {file}")

print(f"\nArchivos con errores ({len(failed_files)}):")
for file, error in failed_files:
    print(f"- {file}: {error}")