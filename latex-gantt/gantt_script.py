import pandas as pd
from datetime import datetime
import jinja2

def read_gantt_data(csv_file):
    df = pd.read_csv(csv_file)
    
    # Encontrar fechas mínima y máxima para el rango del gantt
    min_date = pd.to_datetime(df['date-begin']).min()
    max_date = pd.to_datetime(df['date-end']).max()
    
    return df, min_date, max_date

def convert_progress(progress):
    if progress == 'today':
        return 'today'
    return int(float(progress) * 100)

def generate_latex(df, min_date, max_date):
    latex_template = '''\\documentclass[a4paper,landscape]{article}
\\usepackage{pgfgantt}
\\usepackage[landscape,margin=1cm]{geometry}

% Definimos colores personalizados
\\definecolor{barblue}{RGB}{52,152,219}
\\definecolor{groupblue}{RGB}{41,128,185}
\\definecolor{linkred}{RGB}{231,76,60}
\\definecolor{taskgreen}{RGB}{46,204,113}
\\definecolor{taskgray}{RGB}{149,165,166}

\\begin{document}

\\def\\pgfcalendarweekdayletter#1{%
\\ifcase#1M\\or T\\or W\\or T\\or F\\or S\\or S\\fi%
}

\\begin{ganttchart}[
    hgrid={*1{draw=gray!20}},
    vgrid={*1{draw=gray!20}},
    time slot format=isodate,
    expand chart=\\textwidth,
    x unit=0.4cm,
    link/.style={->, line width=1pt, draw=blue, rounded corners=2pt},
    today=2025-01-23,
    today rule/.style={draw=red!70, dashed, line width=1.5pt},
    today label font=\\small\\bfseries\\color{red!70},
    today label node/.style={anchor=north west, font=\\small\\bfseries},
    title label font=\\small\\bfseries,
    title label node/.append style={text=black},
    group label font=\\bfseries,
    milestone label font=\\itshape,
    bar/.style={draw=black, line width=0.5pt, fill=gray!40, rounded corners=2pt},
    bar incomplete/.style={draw=black, line width=0.5pt, fill=gray!10},
    group/.style={draw=black, line width=0.7pt, fill=groupblue!40}
]{{{ min_date }}}{{{ max_date }}}
    \\gantttitlecalendar{year, month=name, week} \\\\
    {% for _, row in data.iterrows() %}
    \\{{ row.type }}[name={{ row.id }}, progress={{ row.progress }}]{{ "{" }}{{ row.activity }}{{ "}" }}{{ "{" }}{{ row.date_begin }}{{ "}" }}{{ "{" }}{{ row.date_end }}{{ "}" }} \\\\
    {% endfor %}
\\end{ganttchart}

\\end{document}'''

    template = jinja2.Template(latex_template)
    latex_content = template.render(
        min_date=min_date.strftime('%Y-%m-%d'),
        max_date=max_date.strftime('%Y-%m-%d'),
        data=df
    )
    
    return latex_content

def main(csv_file, output_file):
    df, min_date, max_date = read_gantt_data(csv_file)
    df['progress'] = df['progress'].apply(convert_progress)
    
    latex_content = generate_latex(df, min_date, max_date)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

if __name__ == "__main__":
    main('gantt_data.csv', 'gantt_output.tex')