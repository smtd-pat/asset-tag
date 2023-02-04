import base64
import os
from io import BytesIO, StringIO

import pdfkit
import treepoem
from jinja2 import Environment, select_autoescape, FileSystemLoader

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape()
)

while True:
    existing_barcodes = [bc.split(' ')[0] for bc in os.listdir(os.path.dirname(os.path.realpath(__file__))) if bc.endswith('.pdf')]
    stripped_barcodes = [int(bc.split('-')[1]) for bc in existing_barcodes]
    if len(stripped_barcodes) > 0:
        next_barcode = f"PAT-{max(stripped_barcodes) + 1:08d}"
    else:
        next_barcode = None

    name = input("Item name: ")
    barcode_text = input("Item barcode: ")

    if barcode_text in existing_barcodes:
        print('ERROR: Barcode already exists\n---')
        continue
    elif barcode_text.lower() == "" and next_barcode:
        barcode_text = next_barcode
        print(barcode_text)
        os.system(f'echo {barcode_text} | tr -d "\n" | pbcopy')
        print("Copied to clipboard")
    elif barcode_text.lower() == "":
        print('ERROR: No next barcode\n---')
        continue

    barcode_image = treepoem.generate_barcode(barcode_type='datamatrix', data=barcode_text)
    barcode_data = BytesIO()
    barcode_image.save(barcode_data, format="PNG")
    barcode = 'data:image/png;base64, ' + base64.b64encode(barcode_data.getvalue()).decode()

    template = env.get_template("template.html")

    render = template.render(name=name, barcode=barcode, code=barcode_text)

    # with open('out.html', 'w') as f:
    #     f.write(render)

    f = StringIO()
    f.write(render)
    f.seek(0)

    config = pdfkit.configuration(wkhtmltopdf='/opt/local/bin/wkhtmltopdf')
    pdfkit.from_file(f, barcode_text + ' ' + name + '.pdf', options={
            'page-height': '2in',
            'page-width': '3in',
            'margin-top': '0',
            'margin-right': '0',
            'margin-bottom': '0',
            'margin-left': '0',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }, configuration=config)

    print('---')
