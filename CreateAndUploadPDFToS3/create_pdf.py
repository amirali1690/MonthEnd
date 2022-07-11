'''
Functions to Create a pdf from a specific string
'''
from fpdf import FPDF

def create_pdf(data):
    '''
    get the data and create a pdf and store it in Lambda tmp directory
    '''
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font("Arial",size=15)
    pdf.cell(200,10,txt=data['clinic'],ln=1,align='C')
    pdf.output('/tmp/'+data['month']+'-'+data['clinic']+'.pdf')
    return True
