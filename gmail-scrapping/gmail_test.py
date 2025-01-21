import os
import pickle
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

# Definir el rango de fechas para verificar (mismo formato que usamos antes)
date_range = ('2023/07/31', '2023/08/01')  # Puedes ajustar esta fecha

# Remitente a filtrar
sender_filter = 'transaccionesbg@bgeneral.com'  # Filtra por el sender deseado

# Función para extraer fecha en formato simplificado
def extract_simple_date(date_str):
    try:
        date_obj = parser.parse(date_str)
        return date_obj.strftime("%Y/%m/%d")
    except Exception as e:
        print(f"Error al convertir la fecha: {e}")
        return None

# Función para procesar y listar correos
def list_emails_by_date(service, start_date, end_date):
    query = f'after:{start_date} before:{end_date}'
    next_page_token = None

    while True:
        # Obtener correos en el rango de fechas especificado (sin filtrar por INBOX o etiquetas)
        results = service.users().messages().list(userId='me', q=query, maxResults=100, pageToken=next_page_token).execute()
        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken')

        if not messages:
            break

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            sender = next(header['value'] for header in headers if header['name'] == 'From')
            date = next(header['value'] for header in headers if header['name'] == 'Date')
            simple_date = extract_simple_date(date)

            # Filtrar solo correos del remitente especificado
            if sender_filter.lower() in sender.lower():
                # Imprimir en terminal los datos importantes
                print(f"Asunto: {subject}")
                print(f"Remitente: {sender}")
                print(f"Fecha: {date}")
                print(f"Fecha simplificada: {simple_date}")
                print("-" * 50)  # Separador entre correos

        if not next_page_token:
            break

# Función principal
def main():
    """Lista correos del día específico para verificación, filtrados por remitente"""
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

    # Llamar a la función para listar correos del rango definido y aplicando el filtro por sender
    list_emails_by_date(service, date_range[0], date_range[1])

if __name__ == '__main__':
    main()