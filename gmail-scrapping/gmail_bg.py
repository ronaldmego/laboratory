import os
import pickle
import csv
import re
import base64
from bs4 import BeautifulSoup
from dateutil import parser  # Importación para manejo flexible de fechas
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Crear la carpeta "download" si no existe
if not os.path.exists('download'):
    os.makedirs('download')

# Alcances requeridos
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Definir los rangos de meses para procesar
monthly_ranges = [
    #('2024/04/01', '2024/05/01'),  # Incluye 30 de abril
    #('2024/03/01', '2024/04/01'),  # Incluye 31 de marzo
    #('2024/02/01', '2024/03/01'),  # Incluye 29 de febrero (bisiesto)
    #('2024/01/01', '2024/02/01'),  # Incluye 31 de enero
    #('2023/12/01', '2024/01/01'),  # Incluye 31 de diciembre
    #('2023/11/01', '2023/12/01'),  # Incluye 30 de noviembre
    #('2023/10/01', '2023/11/01'),  # Incluye 31 de octubre
    #('2023/09/01', '2023/10/01'),  # Incluye 30 de septiembre
    ('2023/08/01', '2023/09/01'),  # Incluye 31 de agosto
    ('2023/07/01', '2023/08/01')   # Incluye 31 de julio
]

# Función para decodificar el cuerpo del correo
def decode_base64url(encoded_str):
    """Decodifica una cadena base64url"""
    decoded_bytes = base64.urlsafe_b64decode(encoded_str + '==')
    return decoded_bytes.decode('utf-8', 'ignore')

# Función para extraer el cuerpo completo del correo y limpiarlo de etiquetas HTML
def get_email_body(msg):
    if 'payload' in msg:
        # Si el correo está en formato multipart
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    return decode_base64url(part['body']['data'])
                elif part['mimeType'] == 'text/html':
                    html_content = decode_base64url(part['body']['data'])
                    # Usar BeautifulSoup para extraer solo el texto del HTML
                    soup = BeautifulSoup(html_content, 'html.parser')
                    return soup.get_text(separator=" ", strip=True)  # Eliminar etiquetas HTML
        # Si el correo no es multipart, devolver el cuerpo directamente
        else:
            if msg['payload']['mimeType'] == 'text/plain':
                return decode_base64url(msg['payload']['body']['data'])
            elif msg['payload']['mimeType'] == 'text/html':
                html_content = decode_base64url(msg['payload']['body']['data'])
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup.get_text(separator=" ", strip=True)
    return None

# Función para extraer fecha en formato simplificado
def extract_simple_date(date_str):
    try:
        # Eliminar cualquier contenido entre paréntesis en la fecha, como "(GMT-05:00)"
        cleaned_date_str = re.sub(r'\(.*?\)', '', date_str).strip()
        # Utilizamos dateutil.parser para manejar múltiples formatos de fecha automáticamente
        date_obj = parser.parse(cleaned_date_str)
        # Formatear la fecha como yyyy/mm/dd
        return date_obj.strftime("%Y/%m/%d")
    except Exception as e:
        print(f"Error al convertir la fecha: {e}")
        return None

# Función para procesar un correo individual
def process_single_email(message, service):
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    headers = msg['payload']['headers']

    # Manejar excepciones cuando no se encuentra el encabezado 'Subject'
    try:
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    except StopIteration:
        print("Advertencia: No se encontró el encabezado 'Subject' en el correo.")
        subject = "Asunto desconocido"

    sender = next(header['value'] for header in headers if header['name'] == 'From')

    # Intentar obtener la fecha, si no existe, asignar un valor por defecto
    try:
        date = next(header['value'] for header in headers if header['name'] == 'Date')  # Extraer la fecha
        simple_date = extract_simple_date(date)  # Convertir a formato simple yyyy/mm/dd
    except StopIteration:
        date = "Fecha desconocida"
        simple_date = "Fecha desconocida"
        print("Advertencia: No se encontró la fecha en el correo")

    # Limpieza del asunto
    subject_clean = " ".join(subject.split())

    # Solo procesar correos relevantes
    if "Notificaciones de Tarjeta VISA CONNECTMILES PLATINUM".lower() in subject_clean.lower() and "bgeneral.com".lower() in sender.lower():
        print(f"Correo encontrado: Asunto: {subject_clean}, De: {sender}, Fecha: {date}")

        # Obtener el cuerpo completo del correo
        body = get_email_body(msg)
        if body:
            print(f"Contenido del correo completo (texto plano): {body}")  # Mostrar el cuerpo del correo sin HTML

            # Detectar si la transacción es rechazada o exitosa
            if "rechazada" in body.lower():
                status = "rechazada"
            else:
                status = "exitosa"

            # Regex para capturar el monto y el comercio tanto para transacciones exitosas como rechazadas
            pattern = r'pag[o|ó] \$([0-9]+\.[0-9]+) en (.*?)\.|compra por \$([0-9]+\.[0-9]+) en (.*?) con la tarjeta'

            match = re.search(pattern, body, re.IGNORECASE)

            if match:
                if match.group(1) and match.group(2):
                    amount, store = match.group(1), match.group(2)
                elif match.group(3) and match.group(4):
                    amount, store = match.group(3), match.group(4)

                print(f"Transacción encontrada: {amount} en {store} - {status}")  # Confirmar que el regex está capturando los datos
                # Almacenar los datos capturados en el CSV
                return {'amount': amount, 'store': store, 'status': status, 'date': date, 'fecha_simplificada': simple_date}
            else:
                print("No se encontró un patrón coincidente en el cuerpo del correo")
        else:
            print("No se pudo obtener el cuerpo completo del correo")
    return None  # No hay datos que procesar si no coincide

# Función para procesar correos por mes
def process_emails_by_month(service, start_date, end_date):
    query = f'after:{start_date} before:{end_date}'
    next_page_token = None
    data = []
    
    while True:
        # Obtener correos del mes específico
        results = service.users().messages().list(userId='me', q=query, maxResults=100, pageToken=next_page_token).execute()
        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken')

        if not messages:
            break

        # Procesar cada correo y extraer la información de las transacciones exitosas
        for message in messages:
            transaction_info = process_single_email(message, service)
            if transaction_info:
                data.append(transaction_info)
        
        if not next_page_token:
            break

    return data

# Función principal
def main():
    """Procesa correos agrupados por meses de diciembre 2023 a mayo 2024"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Procesar correos por cada mes en el rango
    for start_date, end_date in monthly_ranges:
        print(f"Procesando correos del {start_date} al {end_date}")
        transactions = process_emails_by_month(service, start_date, end_date)
        
        # Especificar la ruta del archivo CSV dentro de la carpeta "download"
        csv_filename = f'download/transacciones_{start_date[:4]}-{start_date[5:7]}.csv'

        # Guardar los resultados en un archivo CSV dentro de la carpeta "download"
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['amount', 'store', 'status', 'date', 'fecha_simplificada'])
            writer.writeheader()
            writer.writerows(transactions)

        print(f"Se ha completado el procesamiento del lote: {start_date[:7]}")

if __name__ == '__main__':
    main()