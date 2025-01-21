# Documentación Directory Tree Generator

Este script de Python permite generar una representación visual de la estructura de directorios de tu proyecto.

## Instalación

Simplemente descarga el archivo `directory_tree.py` y asegúrate de tener Python instalado en tu sistema.

## Uso Básico

La sintaxis básica del comando es:

```bash
python directory_tree.py "ruta/a/tu/proyecto" [opciones]
```

**Importante**: La ruta del directorio debe ir ANTES de las opciones como `--exclude-dirs` o `--max-depth`.

Ejemplo de uso completo:
```bash
python directory_tree.py "C:\Users\ronal\OneDrive\Documentos\APPs\AWS\video-games-sales-assistant-with-amazon-bedrock-agents-main" --exclude-dirs docs > estructura.txt
```

```bash
python directory_tree.py "C:\Users\ronal\OneDrive\Documentos\APPs\langchain_sql" --exclude-dirs ref > estructura.txt
```

```bash
python directory_tree.py "C:\Users\ronal\OneDrive\Documentos\APPs\telco_analytics" --exclude-dirs ref logs > estructura.txt
```

# New `project_analyzer.py`
```bash
(base) PS C:\Users\ronal\OneDrive\Documentos\APPs\laboratory\directory_tree> python project_analyzer.py "C:\Users\ronal\OneDrive\Documentos\APPs\telco_analytics" --exclude-dirs ref logs

Análisis completado con éxito!
Reporte guardado en: C:\Users\ronal\OneDrive\Documentos\APPs\laboratory\directory_tree\project_analysis_20250106_105446.md
(base) PS C:\Users\ronal\OneDrive\Documentos\APPs\laboratory\directory_tree> 
```


### Ejemplos de uso en diferentes sistemas operativos

#### En Linux/Mac
```bash
python directory_tree.py "/home/usuario/proyectos/mi-proyecto"
```

#### En Windows

Hay varias formas de especificar la ruta:

1. Usando comillas dobles (recomendado):
```bash
python directory_tree.py "C:\Users\usuario\Documentos\mi-proyecto"
```

2. Usando forward slashes:
```bash
python directory_tree.py "C:/Users/usuario/Documentos/mi-proyecto"
```

3. Usando doble backslash:
```bash
python directory_tree.py "C:\\Users\\usuario\\Documentos\\mi-proyecto"
```

## Opciones Avanzadas

### Limitar la profundidad
Para ver solo ciertos niveles de profundidad en la estructura:

```bash
python directory_tree.py "ruta/a/tu/proyecto" --max-depth 2
```

Ejemplo en Windows:
```bash
python directory_tree.py "C:\Users\usuario\mi-proyecto" --max-depth 2
```

### Excluir directorios adicionales
Para ignorar directorios adicionales a los excluidos por defecto:

```bash
python directory_tree.py "ruta/a/tu/proyecto" --exclude-dirs carpeta1 carpeta2
```

Ejemplo en Windows:
```bash
python directory_tree.py "C:\Users\usuario\mi-proyecto" --exclude-dirs carpeta1 carpeta2
```

Ejemplo excluyendo directorio y generando archivo txt:
```bash
python directory_tree.py "C:\Users\usuario\proyecto" --exclude-dirs env_ai > estructura.txt
```

### Guardar la salida en un archivo
Para guardar la estructura en un archivo de texto:

```bash
python directory_tree.py "ruta/a/tu/proyecto" > estructura.txt
```

Ejemplo en Windows:
```bash
python directory_tree.py "C:\Users\usuario\mi-proyecto" > estructura.txt
```

## Directorios excluidos por defecto
El script automáticamente excluye los siguientes directorios:
- `.git`
- `__pycache__`
- `node_modules`
- `venv`
- `.venv`
- `env`
- `.env`
- `.idea`
- `.vscode`
- `dist`
- `build`
- `coverage`
- `tmp`
- `.next`
- `.nuxt`

## Archivos excluidos por defecto
El script automáticamente excluye los siguientes tipos de archivos:
- `.pyc`
- `.pyo`
- `.pyd`
- `.DS_Store`

## Ejemplo de salida

```
mi-proyecto/
├── src
│   ├── components
│   │   ├── Header.js
│   │   └── Footer.js
│   └── utils
│       └── helpers.js
├── tests
│   └── test_main.py
├── README.md
└── package.json
```

## Notas adicionales

### Orden de los argumentos
Es importante mantener el siguiente orden en los comandos:
1. Primero el script: `directory_tree.py`
2. Luego la ruta del directorio (entre comillas si contiene espacios)
3. Finalmente las opciones como `--exclude-dirs` o `--max-depth`

### Uso del directorio actual
Si estás en el directorio que quieres analizar, puedes usar `.`:
```bash
python directory_tree.py "." --exclude-dirs env_ai
```

Guardar en archivo:
```bash
python directory_tree.py "." > estructura.txt
```

## Solución de problemas

### Problemas de codificación en Windows
El script está configurado para manejar caracteres especiales y codificación UTF-8 en Windows. Si experimentas problemas de codificación, puedes intentar estas alternativas:

1. Usando PowerShell con codificación específica:
```bash
python directory_tree.py "tu/ruta" | Out-File -Encoding utf8 estructura.txt
```

2. Usando PowerShell con codificación alternativa:
```bash
python directory_tree.py "tu/ruta" | Out-File estructura.txt -Encoding UTF8
```

### Errores comunes
1. Si recibes un error "arguments are required: directory", asegúrate de que la ruta del directorio va ANTES de las opciones:
   - ❌ Incorrecto: `python directory_tree.py --exclude-dirs env_ai "ruta/al/directorio"`
   - ✅ Correcto: `python directory_tree.py "ruta/al/directorio" --exclude-dirs env_ai`

### Permisos de acceso
- El script maneja automáticamente los errores de permisos para directorios a los que no tenga acceso
- Si encuentras errores de permisos, asegúrate de ejecutar el script con los permisos adecuados