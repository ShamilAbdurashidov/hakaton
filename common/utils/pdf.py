import pdfkit

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings


pdf_gen_config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF)
pdf_gen_options = {
    "enable-local-file-access": "",
    'margin-bottom': 15,
    'margin-left': 15,
    'margin-right': 15,
    'margin-top': 15,
    'header-font-name':  'Arial, Helvetica, sans-serif',
    'header-font-size': 10,
    'footer-font-name':  'Arial, Helvetica, sans-serif',
    'footer-font-size': 10
    #"disable-local-file-access": None,
    #"print-media-type": None
    }


def render_to_pdf(
        template, 
        context={}, 
        filename='file', 
        download=False, 
        footer_url=None,
        opts={}
        ):
    config = pdf_gen_config
    options = pdf_gen_options

    if footer_url:
        options.update({ 'footer-html': footer_url })
    else:
        options.update({ 'footer-right': '[page]/[topage]' })
    options.update(opts)
    pdf = pdfkit.from_string(render_to_string(template, context), None, configuration=config, options=options)
    response = HttpResponse(pdf, content_type='application/pdf')
    if download:
        response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % filename
    return response