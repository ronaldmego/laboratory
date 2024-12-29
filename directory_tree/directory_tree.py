import os
import argparse
import sys
import locale
from datetime import datetime

def generate_tree(root_path, additional_exclude_dirs=None, exclude_files=None, max_depth=None):
    """
    Generate a directory tree structure in text format.
    """
    # Directorios que siempre se excluirán por defecto
    DEFAULT_EXCLUDE_DIRS = {
        '.git',
        '__pycache__', 
        'node_modules',
        'venv',
        '.venv',
        'env',
        '.env',
        '.idea',
        '.vscode',
        'dist',
        'build',
        'coverage',
        'tmp',
        '.next',
        '.nuxt'
    }
    
    # Combinar los directorios excluidos por defecto con los adicionales
    exclude_dirs = DEFAULT_EXCLUDE_DIRS | set(additional_exclude_dirs or [])
    exclude_files = set(exclude_files or ['.pyc', '.pyo', '.pyd', '.DS_Store'])
    
    # Lista para almacenar las líneas de salida
    lines = []
    
    def add_to_tree(path, prefix='', current_depth=0):
        # Verificar la profundidad máxima
        if max_depth is not None and current_depth > max_depth:
            return
            
        try:
            # Convertir la ruta para soportar rutas largas en Windows
            if sys.platform.startswith('win'):
                path_to_list = os.path.abspath(path)
                if not path_to_list.startswith('\\\\?\\'):
                    path_to_list = '\\\\?\\' + path_to_list
            else:
                path_to_list = path
                
            # Obtener y ordenar el contenido del directorio
            contents = sorted(os.listdir(path_to_list))
        except (PermissionError, FileNotFoundError, OSError):
            return
        
        # Filtrar elementos excluidos
        contents = [item for item in contents 
                   if not (item in exclude_dirs or 
                          any(item.endswith(ext) for ext in exclude_files))]
        
        # Procesar cada elemento
        for i, item in enumerate(contents):
            is_last = i == len(contents) - 1
            current_prefix = '└── ' if is_last else '├── '
            full_path = os.path.join(path, item)
            
            # Añadir el elemento actual
            lines.append(f'{prefix}{current_prefix}{item}')
            
            # Si es un directorio, procesar su contenido
            if os.path.isdir(full_path):
                next_prefix = prefix + ('    ' if is_last else '│   ')
                add_to_tree(full_path, next_prefix, current_depth + 1)

    # Añadir el directorio raíz
    root_name = os.path.basename(root_path.rstrip(os.sep))
    lines.append(f'{root_name}/')
    
    # Generar el árbol
    add_to_tree(root_path)
    
    return '\n'.join(lines)

def save_tree_output(tree_output, save_path, filename):
    """
    Guarda la salida del árbol en un archivo en la ruta especificada.
    Si el archivo existe, genera un nombre único añadiendo un número.
    """
    try:
        # Asegurarse de que el directorio existe
        os.makedirs(save_path, exist_ok=True)
        
        # Separar el nombre base y la extensión
        name, ext = os.path.splitext(filename)
        
        # Crear la ruta completa del archivo
        file_path = os.path.join(save_path, filename)
        
        # Si el archivo existe, añadir un número al final
        counter = 1
        while os.path.exists(file_path):
            new_filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(save_path, new_filename)
            counter += 1
        
        # Guardar el contenido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(tree_output)
            
        print(f"Árbol guardado en: {file_path}")
    except Exception as e:
        print(f"Error al guardar el archivo en {save_path}: {str(e)}")

if __name__ == '__main__':
    # Configurar codificación para Windows
    if sys.platform.startswith('win'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(
        description='Generate a directory tree structure',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('directory', type=str, help='Root directory path')
    parser.add_argument('--max-depth', type=int, help='Maximum depth to traverse')
    parser.add_argument(
        '--exclude-dirs', 
        nargs='+', 
        default=[], 
        help='Additional directories to exclude\n'
             'Note: Some directories are excluded by default\n'
             '(.git, __pycache__, node_modules, venv, etc.)'
    )
    parser.add_argument(
        '--exclude-files', 
        nargs='+', 
        default=[], 
        help='File patterns to exclude\n'
             'Default: .pyc, .pyo, .pyd, .DS_Store'
    )
    
    args = parser.parse_args()
    
    # Obtener la ruta absoluta y verificar que existe
    target_path = os.path.abspath(args.directory)
    if not os.path.exists(target_path):
        print(f"Error: La ruta {target_path} no existe")
        sys.exit(1)
    
    # Generar el árbol
    tree_output = generate_tree(
        target_path,
        additional_exclude_dirs=args.exclude_dirs,
        exclude_files=args.exclude_files,
        max_depth=args.max_depth
    )
    
    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tree_{timestamp}.txt"
    
    # Guardar en el directorio actual
    current_dir = os.getcwd()
    save_tree_output(tree_output, current_dir, filename)
    
    # Guardar en el directorio analizado
    save_tree_output(tree_output, target_path, filename)
    
    # Imprimir el resultado en consola
    try:
        print("\nÁrbol de directorios:")
        print(tree_output)
    except UnicodeEncodeError:
        print(tree_output.encode(locale.getpreferredencoding(), errors='replace').decode())