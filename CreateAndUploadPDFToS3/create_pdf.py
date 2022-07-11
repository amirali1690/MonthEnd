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
    pdf.cell(200,6,txt='Month: '+data['month'].replace('-',' '),ln=1,align='L')
    pdf.cell(200,6,txt='Current Billed Amount: $'+data['billed']['total']['current'],ln=1,align='L')
    pdf.cell(200,6,txt='Insurance: $'+data['insurance']['total']['current'],ln=1,align='L')
    pdf.cell(200,6,txt='PI: $'+data['PI']['total']['current'],ln=1,align='L')

    pdf.cell(200,30,txt='Previous Month Billed Amount: $'+data['billed']['total']['previous'],
            ln=1,align='L')
    pdf.cell(200,6,txt='Insurance: $'+data['insurance']['total']['previous'],ln=1,align='L')
    pdf.cell(200,6,txt='PI: $'+data['PI']['total']['previous'],ln=1,align='L')
    insuranceCollection= str(
                            round(
                                float(data['collection']['insurance'])+
                                float(data['collection']['copay/coins/ded'])
                                ,2)
                            )
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

    pdf.cell(200,30,txt='insurance Collections: $'+data['collection']['insurance']+
                    ' + ( '+data['collection']['copay/coins/ded']+') = $'+
                    insuranceCollection,ln=1,align='L')
    pdf.cell(200,6,txt='PI: $'+data['collection']['pi'],ln=1,align='L')
    pdf.cell(200,6,txt='Copays/Coins/Ded: $'+data['collection']['copay/coins/ded'],ln=1,align='L')
    pdf.cell(200,6,txt='otc: $'+data['collection']['otc']+
                    ' - ( '+data['collection']['copay/coins/ded']+') = $'+
                    otcCollections,ln=1,align='L')
    pdf.cell(200,6,txt='Total Collections: $'+totalCollection,ln=1,align='L')


    collectionPercentage = str(
                                round(
                                    float(totalCollection)/
                                    float(data['billed']['total']['previous'])
                                    ,2
                                    )*100
                                )
    pdf.cell(200,30,txt='Percentage of Collections: %'+collectionPercentage,ln=1,align='L')

    pdf.cell(200,30,txt='Chiropractic charges: $'+data['specialty']['chiro'],ln=1,align='L')
    pdf.cell(200,6,txt='Medical charges: $'+data['specialty']['md'],ln=1,align='L')
    pdf.cell(200,6,txt='DPT charges: $'+data['specialty']['pt'],ln=1,align='L')

    pdf.output('/tmp/'+data['month']+'-'+data['clinic']+'.pdf')
    return True
