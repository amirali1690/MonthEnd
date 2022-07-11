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
    pdf.set_font("Times",'B',size=15)
    pdf.set_text_color(100,100,100)
    pdf.cell(200,30,txt='Ateah Management, LLC',ln=1,align='C')
    pdf.set_font("Arial",size=12)
    pdf.set_text_color(0,0,0)
    pdf.cell(200,6,txt='Clinic: '+data['clinic'],ln=1,align='L')
    pdf.cell(200,6,txt='Month: '+data['month'],ln=1,align='L')
    pdf.output('/tmp/'+data['month']+'-'+data['clinic']+'.pdf')
    return True
