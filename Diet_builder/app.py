from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    # Leggi il file Excel
    xls = pd.ExcelFile(r"C:\Users\lbasile\PycharmProjects\TIM_dev\Preprocessing_pipeline\diet_plan_2300.xlsx")
    sheet_names = xls.sheet_names

    # Converti ogni foglio in una tabella HTML
    sheets = {}
    for sheet_name in sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        sheets[sheet_name] = df.to_html(classes='table table-striped', index=False)

    # Template HTML
    html = '''
    <html>
        <head>
            <title>Visualizzazione Dati</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
            <style>
                .sheet-table {
                    display: none;
                }
                .sheet-table.active {
                    display: table;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mt-5">Dati Tabellari</h1>
                <div class="mt-3">
                    <ul class="nav nav-tabs" id="sheet-tabs">
                        {% for sheet in sheet_names %}
                            <li class="nav-item">
                                <a class="nav-link {% if loop.index == 1 %}active{% endif %}" href="#" data-sheet="{{ sheet }}">{{ sheet }}</a>
                            </li>
                        {% endfor %}
                    </ul>
                    <div class="mt-3">
                        {% for sheet, table in sheets.items() %}
                            <div class="sheet-table {% if loop.index == 1 %}active{% endif %}" id="table-{{ sheet }}">
                                {{ table | safe }}
                            </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const tabs = document.querySelectorAll('#sheet-tabs a');
                    tabs.forEach(tab => {
                        tab.addEventListener('click', function(event) {
                            event.preventDefault();
                            // Rimuovi la classe 'active' da tutti i tab
                            tabs.forEach(t => t.classList.remove('active'));
                            // Aggiungi la classe 'active' al tab cliccato
                            this.classList.add('active');

                            // Nascondi tutte le tabelle
                            const tables = document.querySelectorAll('.sheet-table');
                            tables.forEach(table => table.classList.remove('active'));

                            // Mostra la tabella associata al tab cliccato
                            const sheet = this.getAttribute('data-sheet');
                            document.getElementById('table-' + sheet).classList.add('active');
                        });
                    });
                });
            </script>
        </body>
    </html>
    '''

    return render_template_string(html, sheets=sheets, sheet_names=sheet_names)

if __name__ == '__main__':
    app.run(debug=True)
