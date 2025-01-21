import os
import pickle
import csv
import re
import base64
from bs4 import BeautifulSoup
from dateutil import parser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Crear la carpeta "download" si no existe
if not os.path.exists('download'):
    os.makedirs('download')

# Alcances requeridos
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Definir los rangos de fechas para procesar
monthly_ranges = [
    ('2024/09/01', '2024/10/01')#,
    #('2024/08/01', '2024/09/01'),
    #('2024/07/01', '2024/08/01'),
    #('2024/06/01', '2024/07/01'),
    #('2024/05/01', '2024/06/01'),
    #('2024/04/01', '2024/05/01'),
    #('2024/03/01', '2024/04/01'),
    #('2024/02/01', '2024/03/01'),
    #('2024/01/01', '2024/02/01'),
    #('2023/12/01', '2024/01/01'),
    #('2023/11/01', '2023/12/01'),
    #('2023/10/01', '2023/11/01'),
    #('2023/09/01', '2023/10/01'),
    #('2023/08/01', '2023/09/01'),
    #('2023/07/01', '2023/08/01'),
    #('2023/06/01', '2023/07/01'),
    #('2023/05/01', '2023/06/01'),
    #('2023/04/01', '2023/05/01'),
    #('2023/03/01', '2023/04/01'),
    #('2023/02/01', '2023/03/01'),
    #('2023/01/01', '2023/02/01'),
    #('2022/12/01', '2023/01/01'),
    #('2022/11/01', '2022/12/01'),
    #('2022/10/01', '2022/11/01'),
    #('2022/09/01', '2022/10/01'),
    #('2022/08/01', '2022/09/01'),
    #('2022/07/01', '2022/08/01'),
    #('2022/06/01', '2022/07/01'),
    #('2022/05/01', '2022/06/01'),
    #('2022/04/01', '2022/05/01'),
    #('2022/03/01', '2022/04/01'),
    #('2022/02/01', '2022/03/01'),
    #('2022/01/01', '2022/02/01')
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
        # Utilizamos dateutil.parser para manejar múltiples formatos de fecha automáticamente
        date_obj = parser.parse(date_str)
        # Formatear la fecha como yyyy/mm/dd
        return date_obj.strftime("%Y/%m/%d")
    except Exception as e:
        print(f"Error al convertir la fecha: {e}")
        return None

# Función para procesar un correo individual
def process_single_email(message, service):
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    headers = msg['payload']['headers']
    
    # Intentar obtener el asunto
    try:
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    except StopIteration:
        subject = "Asunto desconocido"
        print("Advertencia: No se encontró el asunto en el correo")

    sender = next(header['value'] for header in headers if header['name'] == 'From')
    
    # Intentar obtener la fecha, si no existe, asignar un valor por defecto
    try:
        date = next(header['value'] for header in headers if header['name'] == 'Date')
        simple_date = extract_simple_date(date)
    except StopIteration:
        date = "Fecha desconocida"
        simple_date = "Fecha desconocida"
        print("Advertencia: No se encontró la fecha en el correo")

    # Limpieza del asunto
    subject_clean = " ".join(subject.split())
    
    # Procesar correos tanto de tarjeta principal como adicional
    if ("Autorización de Débito en Tarjeta Principal".lower() in subject_clean.lower() or 
        "Autorización de Débito en Tarjeta Adicional".lower() in subject_clean.lower()) and \
        "notificaciones@pa.scotiabank.com".lower() in sender.lower():
        
        print(f"Correo encontrado: Asunto: {subject_clean}, De: {sender}, Fecha: {date}")
        
        # Obtener el cuerpo completo del correo
        body = get_email_body(msg)
        if body:
            print(f"Contenido del correo completo (texto plano): {body}")

            # Detectar si la transacción es exitosa
            status = "exitosa"

            # Regex para capturar el monto y el comercio
            pattern = r'tarjeta de crédito (?:titular|adicional) de Scotiabank terminada en \d{4} por USD ([0-9]+(?:,[0-9]{3})*\.[0-9]+) en (.*?) el día'
            match = re.search(pattern, body, re.IGNORECASE)

            if match:
                amount = match.group(1).replace(",", "")
                store = match.group(2)
                print(f"Transacción encontrada: {amount} en {store} - {status}")
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
        
        # Verificar si hay una página siguiente y seguir procesando
        if not next_page_token:
            break

    return data

# Función principal
def main():
    """Procesa correos agrupados por días específicos de abril 2024 para Scotiabank"""
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

    # Procesar correos por cada día en el rango
    for start_date, end_date in monthly_ranges:
        print(f"Procesando correos del {start_date} al {end_date}")
        transactions = process_emails_by_month(service, start_date, end_date)
        
        # Especificar la ruta del archivo CSV dentro de la carpeta "download" con nombre "scotia_transacciones_YYYY-MM.csv"
        csv_filename = f'download/scotia_transacciones_{start_date[:4]}-{start_date[5:7]}.csv'

        # Guardar los resultados en un archivo CSV dentro de la carpeta "download"
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['amount', 'store', 'status', 'date', 'fecha_simplificada'])
            writer.writeheader()
            writer.writerows(transactions)

        print(f"Se ha completado el procesamiento del lote: {start_date[:7]}")

if __name__ == '__main__':
    main()