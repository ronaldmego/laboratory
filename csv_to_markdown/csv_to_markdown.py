def csv_to_markdown(csv_file, output_file=None):
    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Limpiar líneas
    lines = [line.strip().split(',') for line in lines]
    
    # Crear tabla markdown
    markdown = []
    # Headers
    markdown.append('| ' + ' | '.join(lines[0]) + ' |')
    # Separador
    markdown.append('| ' + ' | '.join(['---'] * len(lines[0])) + ' |')
    # Datos
    for line in lines[1:]:
        markdown.append('| ' + ' | '.join(line) + ' |')
    
    result = '\n'.join(markdown)
    
    # Guardar o retornar
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        return f"Guardado en {output_file}"
    return result

# Uso
csv_file='C:\\Users\\ronal\\APPs\\project_analyzer_for_llm\\ref\\result.csv'
tabla = csv_to_markdown(csv_file, 'salida.md')