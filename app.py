from flask import Flask, request, flash, render_template, redirect, url_for, send_file
import base64
import os
from io import BytesIO, StringIO

import pdfkit
import treepoem
from jinja2 import Environment, select_autoescape, FileSystemLoader

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf'

pdfkit_config = pdfkit.configuration(wkhtmltopdf='/opt/local/bin/wkhtmltopdf')

@app.route('/', methods=['POST', 'GET'])
def application():
    barcodes = [bc.split(' ')[0] for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if
                bc.endswith('.pdf')]
    names = [' '.join(bc.split(' ')[1:]).replace('.pdf', '') for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if bc.endswith('.pdf')]
    items = list(reversed(sorted(list(zip(barcodes, names)))))

    if request.method == 'POST':
        env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape()
        )

        stripped_barcodes = [int(bc.split('-')[1]) for bc in barcodes]
        if len(stripped_barcodes) > 0:
            next_barcode = f"PAT-{max(stripped_barcodes) + 1:08d}"
        else:
            next_barcode = None

        name = request.form['item_name']
        barcode_text = request.form['barcode']

        if barcode_text in barcodes:
            flash(f'ERROR: Barcode {barcode_text} already exists')
            return render_template('app.html', items=items)
        elif barcode_text.lower() == "" and next_barcode:
            barcode_text = next_barcode
        elif barcode_text.lower() == "":
            flash('ERROR: No next barcode')
            return render_template('app.html', items=items)

        print(name)
        print(barcode_text)

        barcode_image = treepoem.generate_barcode(barcode_type='datamatrix', data=barcode_text)
        barcode_data = BytesIO()
        barcode_image.save(barcode_data, format="PNG")
        barcode = 'data:image/png;base64, ' + base64.b64encode(barcode_data.getvalue()).decode()

        template = env.get_template("template.html")

        render = template.render(name=name, barcode=barcode, code=barcode_text)

        f = StringIO()
        f.write(render)
        f.seek(0)

        pdfkit.from_file(f, barcode_text + ' ' + name + '.pdf', options={
                'page-height': '2in',
                'page-width': '3in',
                'margin-top': '0',
                'margin-right': '0',
                'margin-bottom': '0',
                'margin-left': '0',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
            }, configuration=pdfkit_config)

        items.insert(0, (barcode_text, name))

        flash(f'{barcode_text} {name} created')

    return render_template('app.html', items=items)


@app.route('/<barcode>')
def tag(barcode=None):
    if barcode is None:
        return redirect(url_for('application'))

    files = [bc for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if
     bc.endswith('.pdf')]
    barcodes = [bc.split(' ')[0] for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if
                bc.endswith('.pdf')]
    names = [' '.join(bc.split(' ')[1:]).replace('.pdf', '') for bc in
             os.listdir(os.path.dirname(os.path.realpath(__file__))) if bc.endswith('.pdf')]
    items = reversed(sorted(list(zip(barcodes, names, files))))

    if barcode not in barcodes:
        flash(f'404: Asset Tag {barcode} not found')
        return redirect(url_for('application'))

    pdf_name = [item for item in items if item[0] == barcode][0][2]

    return send_file(pdf_name, download_name=pdf_name)


@app.route('/download/<barcode>')
def download(barcode=None):
    if barcode is None:
        return redirect(url_for('application'))

    files = [bc for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if
     bc.endswith('.pdf')]
    barcodes = [bc.split(' ')[0] for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if
                bc.endswith('.pdf')]
    names = [' '.join(bc.split(' ')[1:]).replace('.pdf', '') for bc in
             os.listdir(os.path.dirname(os.path.realpath(__file__))) if bc.endswith('.pdf')]
    items = reversed(sorted(list(zip(barcodes, names, files))))

    if barcode not in barcodes:
        flash(f'404: Asset Tag {barcode} not found')
        return redirect(url_for('application'))

    pdf_name = [item for item in items if item[0] == barcode][0][2]

    return send_file(pdf_name, download_name=pdf_name, as_attachment=True)


@app.route('/delete/<barcode>', methods=['POST', 'GET'])
def delete(barcode=None):
    if barcode is None:
        return redirect(url_for('application'))

    files = [bc for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if
             bc.endswith('.pdf')]
    barcodes = [bc.split(' ')[0] for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if
                bc.endswith('.pdf')]
    names = [' '.join(bc.split(' ')[1:]).replace('.pdf', '') for bc in
             os.listdir(os.path.dirname(os.path.realpath(__file__))) if bc.endswith('.pdf')]
    items = reversed(sorted(list(zip(barcodes, names, files))))

    if barcode not in barcodes:
        flash(f'404: Asset Tag {barcode} not found')
        return redirect(url_for('application'))

    pdf_name = [item for item in items if item[0] == barcode][0][2]

    os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), pdf_name))

    flash(f'{pdf_name.replace(".pdf", "")} deleted')

    return redirect('/')