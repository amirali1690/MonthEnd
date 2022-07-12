'''
Functions to Create a pdf from a specific string
'''
import locale
from fpdf import FPDF


def create_pdf(data):
    '''
    get the data and create a pdf and store it in Lambda tmp directory
    '''
    locale.setlocale( locale.LC_ALL, 'en_US' )
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
            locale.currency(data['billed']['total']['current'],grouping=True),ln=1,align='L')
    pdf.cell(200,10,txt='Insurance: $'+
            locale.currency(data['billed']['insurance']['current'],grouping=True),
            ln=1,align='L')
    pdf.cell(200,10,txt='PI: $'+
            locale.currency(data['billed']['pi']['current'],grouping=True),ln=1,align='L')
    pdf.cell(200,12,txt='',ln=1,align='L')

    pdf.cell(200,10,txt='Previous Month Billed Amount: $'+
            locale.currency(data['billed']['total']['previous'],grouping=True),
            ln=1,align='L')
    pdf.cell(200,10,txt='Insurance: $'+
            locale.currency(data['billed']['insurance']['previous'],grouping=True),
            ln=1,align='L')
    pdf.cell(200,10,txt='PI: $'+
            locale.currency(data['billed']['pi']['previous'],grouping=True),ln=1,align='L')
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
                    locale.currency(data['collection']['insurance']
                    ,grouping=True)+
                    ' + ('+locale.currency(data['collection']['copay/coins/ded']
                    ,grouping=True)+') = $'+
                    locale.currency(insuranceCollection),ln=1,align='L')
    pdf.cell(200,10,txt='PI: $'+
                        locale.currency(data['collection']['pi'],grouping=True),ln=1,align='L')
    pdf.cell(200,10,txt='Copays/Coins/Ded: $'+
                    locale.currency(data['collection']['copay/coins/ded'],grouping=True),
            ln=1,align='L')
    pdf.cell(200,10,txt='OTC Collecetions: $'+
                    locale.currency(data['collection']['otc'],grouping=True)+
                    ' - ('+locale.currency(data['collection']['copay/coins/ded'],
                    grouping=True)+') = $'+
                    locale.currency(otcCollections),ln=1,align='L')
    pdf.cell(200,10,txt='Total Collections: $'+locale.currency(totalCollection),ln=1,align='L')


    collectionPercentage = str(
                                round(
                                    float(totalCollection)/
                                    float(data['billed']['total']['previous'])
                                    ,2
                                    )*100
                                )
    pdf.cell(200,12,txt='',ln=1,align='L')
    pdf.cell(200,10,txt='Percentage of Collections: '+
                locale.currency(collectionPercentage)+'%',ln=1,align='L')
    pdf.cell(200,12,txt='',ln=1,align='L')
    pdf.cell(200,10,txt='Chiropractic charges: $'+
            locale.currency(data['specialty']['chiro'],grouping=True),
            ln=1,align='L')
    pdf.cell(200,10,txt='Medical charges: $'+
                locale.currency(data['specialty']['md'],grouping=True),ln=1,align='L')
    try:
        pdf.cell(200,10,txt='DPT charges: $'+
            locale.currency(data['specialty']['pt'],grouping=True),ln=1,align='L')
    except ValueError:
        pdf.cell(200,10,txt='DPT charges: $'+
            locale.currency(0,grouping=True),ln=1,align='L')
    pdf.output('/tmp/'+data['month']+'-'+data['clinic']+'.pdf')
    return True
