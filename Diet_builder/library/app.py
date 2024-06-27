from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():

    paths = {
        '2300': "/Users/liviobasile/Documents/Machine Learning/lillo097/Diet_builder/output_data/diet_plan_2300.xlsx",
        '2000': "/Users/liviobasile/Documents/Machine Learning/lillo097/Diet_builder/output_data/diet_plan_2000.xlsx"
    }

    all_sheets = {'2300': {}, '2000': {}}

    for version, path in paths.items():
        xls = pd.ExcelFile(path)
        sheet_names = xls.sheet_names

        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df = df.fillna('')
            all_sheets[version][sheet_name] = df.to_html(classes='table table-striped', index=False)

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
                <h1 class="mt-5">2300 Kcal diet (Gym day)</h1>
                <div class="mt-3">
                    <ul class="nav nav-tabs" id="sheet-tabs-2300">
                        {% for sheet in all_sheets['2300'].keys() %}
                            <li class="nav-item">
                                <a class="nav-link {% if loop.index == 1 %}active{% endif %}" href="#" data-sheet="{{ sheet }}" data-version="2300">{{ sheet }}</a>
                            </li>
                        {% endfor %}
                    </ul>
                    <div class="mt-3">
                        {% for sheet, table in all_sheets['2300'].items() %}
                            <div class="sheet-table {% if loop.index == 1 %}active{% endif %}" id="table-2300-{{ sheet }}">
                                {{ table | safe }}
                            </div>
                        {% endfor %}
                    </div>
                </div>
                <h1 class="mt-5">2000 Kcal diet (Rest day)</h1>
                <div class="mt-3">
                    <ul class="nav nav-tabs" id="sheet-tabs-2000">
                        {% for sheet in all_sheets['2000'].keys() %}
                            <li class="nav-item">
                                <a class="nav-link {% if loop.index == 1 %}active{% endif %}" href="#" data-sheet="{{ sheet }}" data-version="2000">{{ sheet }}</a>
                            </li>
                        {% endfor %}
                    </ul>
                    <div class="mt-3">
                        {% for sheet, table in all_sheets['2000'].items() %}
                            <div class="sheet-table {% if loop.index == 1 %}active{% endif %}" id="table-2000-{{ sheet }}">
                                {{ table | safe }}
                            </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const tabs2300 = document.querySelectorAll('#sheet-tabs-2300 a');
                    tabs2300.forEach(tab => {
                        tab.addEventListener('click', function(event) {
                            event.preventDefault();
                            tabs2300.forEach(t => t.classList.remove('active'));
                            this.classList.add('active');

                            const tables = document.querySelectorAll('.sheet-table');
                            tables.forEach(table => table.classList.remove('active'));

                            const sheet = this.getAttribute('data-sheet');
                            document.getElementById('table-2300-' + sheet).classList.add('active');
                        });
                    });

                    const tabs2000 = document.querySelectorAll('#sheet-tabs-2000 a');
                    tabs2000.forEach(tab => {
                        tab.addEventListener('click', function(event) {
                            event.preventDefault();
                            tabs2000.forEach(t => t.classList.remove('active'));
                            this.classList.add('active');

                            const tables = document.querySelectorAll('.sheet-table');
                            tables.forEach(table => table.classList.remove('active'));

                            const sheet = this.getAttribute('data-sheet');
                            document.getElementById('table-2000-' + sheet).classList.add('active');
                        });
                    });
                });
            </script>
        </body>
    </html>
    '''

    return render_template_string(html, all_sheets=all_sheets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
