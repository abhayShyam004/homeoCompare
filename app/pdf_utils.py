from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import logging

logger = logging.getLogger(__name__)

def render_to_pdf(template_src, context_dict={}):
    """
    Render a Django template to a PDF file.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Create PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    
    logger.error("PDF Generation Error: %s", pdf.err)
    return None
