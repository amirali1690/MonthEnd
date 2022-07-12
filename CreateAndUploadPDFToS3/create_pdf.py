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
    pdf.set_font("Arial",'B',size=15)
    pdf.set_text_color(100,100,100)
    pdf.cell(200,12,txt='Ateah Management, LLC',ln=1,align='C')
    pdf.cell(200,12,txt='',ln=1,align='L')
    pdf.set_font("Arial",size=11)
    pdf.set_text_color(0,0,0)
    pdf.cell(200,10,txt='Clinic: '+data['clinic'],ln=1,align='L')
    pdf.cell(200,10,txt='Month: '+data['month'].replace('-',' '),ln=1,align='L')
    pdf.cell(200,10,txt='Current Billed Amount: $'+
            "{:,}".format(float(data['billed']['total']['current'])),ln=1,align='L')
    pdf.cell(200,10,txt='Insurance: $'+"{:,}".format(float(data['billed']['insurance']['current'])),
            ln=1,align='L')
    pdf.cell(200,10,txt='PI: $'+
            "{:,}".format(float(data['billed']['pi']['current'])),ln=1,align='L')
    pdf.cell(200,12,txt='',ln=1,align='L')

    pdf.cell(200,10,txt='Previous Month Billed Amount: $'+
            "{:,}".format(float(data['billed']['total']['previous'])),
            ln=1,align='L')
    pdf.cell(200,10,txt='Insurance: $'+
            "{:,}".format(float(data['billed']['insurance']['previous'])),
            ln=1,align='L')
    pdf.cell(200,10,txt='PI: $'+
            "{:,}".format(float(data['billed']['pi']['previous'])),ln=1,align='L')
    insuranceCollection= str(
                            round(
                                float(data['collection']['insurance'])+
                                float(data['collection']['copay/coins/ded'])
                                ,2)
                            )
    pdf.cell(200,12,txt='',ln=1,align='L')
    otcCollections = str(
                            round(
                                float(data['collection']['otc'])-
                                float(data['collection']['copay/coins/ded'])
                                ,2)
                            )
    totalCollection = str(
                            round(
                                float(data['collection']['insurance'])+
                                float(data['collection']['pi'])+
                                float(data['collection']['otc'])
                                ,2)
                            )

    pdf.cell(200,10,txt='Insurance Collections: $'+
                    "{:,}".format(float(data['collection']['insurance']))+
                    ' + ('+"{:,}".format(float(data['collection']['copay/coins/ded']))+') = $'+
                    "{:,}".format(float(insuranceCollection)),ln=1,align='L')
    pdf.cell(200,10,txt='PI: $'+
                        "{:,}".format(float(data['collection']['pi'])),ln=1,align='L')
    pdf.cell(200,10,txt='Copays/Coins/Ded: $'+
                    "{:,}".format(float(data['collection']['copay/coins/ded'])),
            ln=1,align='L')
    pdf.cell(200,10,txt='OTC Collecetions: $'+
                    "{:,}".format(float(data['collection']['otc']))+
                    ' - ('+"{:,}".format(float(data['collection']['copay/coins/ded']))+') = $'+
                    "{:,}".format(float(otcCollections)),ln=1,align='L')
    pdf.cell(200,10,txt='Total Collections: $'+"{:,}".format(float(totalCollection)),ln=1,align='L')


    collectionPercentage = str(
                                round(
                                    float(totalCollection)/
                                    float(data['billed']['total']['previous'])
                                    ,2
                                    )*100
                                )
    pdf.cell(200,12,txt='',ln=1,align='L')
    pdf.cell(200,10,txt='Percentage of Collections: '+
                "{:,}".format(float(collectionPercentage))+'%',ln=1,align='L')
    pdf.cell(200,12,txt='',ln=1,align='L')
    pdf.cell(200,10,txt='Chiropractic charges: $'+
            "{:,}".format(float(data['specialty']['chiro'])),
            ln=1,align='L')
    pdf.cell(200,10,txt='Medical charges: $'+
                "{:,}".format(float(data['specialty']['md'])),ln=1,align='L')
    try:
        pdf.cell(200,10,txt='DPT charges: $'+
            "{:,}".format(float(data['specialty']['pt'])),ln=1,align='L')
    except ValueError:
        pdf.cell(200,10,txt='DPT charges: $'+
            "{:,}".format(0),ln=1,align='L')
    pdf.output('/tmp/'+data['month']+'-'+data['clinic']+'.pdf')
    return True
