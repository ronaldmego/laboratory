"""
Este script renombra files con caraceres estandart, eliminando mayusculas, tildes, y cualquier caracter que pueda crear problemas de lectura.
"""

import os
import re
import unicodedata

def normalize_filename(filename):
    # Separar nombre y extensión
    name, ext = os.path.splitext(filename)
    
    # Eliminar caracteres entre paréntesis y los paréntesis
    name = re.sub(r'\s*\([^)]*\)', '', name)
    
    # Convertir a minúsculas
    name = name.lower()
    
    # Normalizar caracteres Unicode
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    
    # Reemplazar espacios por guiones y eliminar caracteres no alfanuméricos
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'\s+', '-', name.strip())
    
    return f"{name}{ext}"

def rename_pdfs(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            old_path = os.path.join(directory, filename)
            new_filename = normalize_filename(filename)
            new_path = os.path.join(directory, new_filename)
            
            try:
                os.rename(old_path, new_path)
                print(f"Renombrado: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error al renombrar {filename}: {e}")

# Ejecutar el script
directory = r"C:\Users\ronal\APPs\personal\assets\books"
rename_pdfs(directory)