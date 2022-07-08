"""
lambda function gets current pi cases from database and send them to sqs.
"""
import os
import logging
import pymysql
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def dateToString(date):
    string=date.strftime("%Y-%m-%d")
    return string
    
def month_before(firstDayCurrent):
     
    if firstDayCurrent.month==1:
        month=12
        year=firstDayCurrent.year-1
        result = datetime(year,month,1)    
    else:
        month=firstDayCurrent.month-1
        result=datetime(firstDayCurrent.year,month,1)
    
    return result.date()

def lambda_handler(event, context):
    """
    gets current pi cases from database and send them to sqs.
    """
    clinicList=['Chandler','Gilbert','Tempe','Ocotillo','Desert Ridge',
                'Queen Creek','Goodyear','Phoenix','Mesa']
    today=datetime.now().date()
    thisMonth=datetime(today.year,today.month-1,1).date()
    lastMonth = month_before(thisMonth)
    lastMonthMonth=lastMonth.month
    monthBeforeLastMonth = month_before(lastMonth)
    monthBeforeLastMonthMonth=monthBeforeLastMonth.month
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)
    result={}
    print("Lambda function memory limits in MB:",context.memory_limit_in_mb)
    connection = pymysql.connect(host=os.getenv('RDS_HOST'),
                                user = os.getenv('RDS_USER'),
                                password = os.getenv('RDS_PASSWORD'),
                                database = os.getenv('RDS_DB'),
                                port = 3306,
                                cursorclass= pymysql.cursors.DictCursor)
    cursor=connection.cursor()
    
    
    #### Get Total Billed for the last two months
    sql =   "SELECT SUM(P.charged) AS CurrentBilled,CL.name AS clinic,MONTH(P.transactionDate) AS month "\
            "FROM payments P "\
            "LEFT JOIN appointments A ON A.id=P.appointmentID "\
            "LEFT JOIN customers CU ON CU.id=A.customerID "\
            "LEFT JOIN clinics CL ON CL.id=CU.clinicID "\
            "LEFT JOIN casetypes CT ON CT.id=CU.casetypeID "\
            "LEFT JOIN providers PR ON PR.id=P.providerID "\
            "WHERE P.tranSubType='SV' AND P.transactionDate>=%s AND "\
            "P.transactionDate<%s AND PR.name NOT LIKE '%%cryo t%%'  "\
            "AND CT.name NOT LIKE '%%cryo%%' AND P.tranSubType<>'OT' "\
            "GROUP BY CL.name,MONTH(P.transactionDate)"
    cursor.execute(sql,(dateToString(monthBeforeLastMonth),dateToString(thisMonth)))
    currentBilled = cursor.fetchall()
    for info in currentBilled:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        if info['month']==lastMonthMonth:
            result[info['clinic']]['billed']['total']['current']=str(info['CurrentBilled'])
        if info['month']==monthBeforeLastMonthMonth:
            result[info['clinic']]['billed']['total']['previous']=str(info['CurrentBilled'])
            
            
            
    #### Get Total insurance Billed for the last two months        
    sql = "SELECT SUM(P.charged) AS insuranceBilled,CL.name AS clinic, MONTH(P.transactionDate) AS month "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id=P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id=A.customerID "\
          "LEFT JOIN clinics CL ON CL.id=CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id=CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id=P.providerID "\
          "WHERE P.tranSubType='SV' AND P.transactionDate>=%s AND "\
          "P.transactionDate<%s AND "\
          "PR.name NOT LIKE '%%cryo t%%' AND CT.name NOT LIKE '%%cryo%%' AND  "\
          "P.tranSubType<>'OT' AND CT.name NOT LIKE '%%PI%%' AND CT.name NOT LIKE '%%WC%%'  "\
          "GROUP BY CL.name, MONTH(P.transactionDate)"
    cursor.execute(sql,(dateToString(monthBeforeLastMonth),dateToString(thisMonth)))
    insuranceBilled = cursor.fetchall()
    for info in insuranceBilled:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        if info['month']==lastMonthMonth:
            result[info['clinic']]['billed']['insurance']['current']=str(info['insuranceBilled'])
        if info['month']==monthBeforeLastMonthMonth:
            result[info['clinic']]['billed']['insurance']['previous']=str(info['insuranceBilled'])   


    #### Get Total PI Billed for the last two months
    sql = "SELECT SUM(P.charged) AS piBilled,CL.name AS clinic, MONTH(P.transactionDate) AS month  "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id=P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id=A.customerID "\
          "LEFT JOIN clinics CL ON CL.id=CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id=CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id=P.providerID "\
          "WHERE P.tranSubType='SV' AND P.transactionDate>=%s AND P.transactionDate<%s AND "\
          "PR.name NOT LIKE '%%cryo t%%' AND CT.name NOT LIKE '%%cryo%%' AND  "\
          "P.tranSubType<>'OT' AND ( CT.name LIKE '%%PI%%' OR CT.name LIKE '%%WC%%' ) "\
          "GROUP BY CL.name, MONTH(P.transactionDate)"
    cursor.execute(sql,(dateToString(monthBeforeLastMonth),dateToString(thisMonth)))
    piBilled = cursor.fetchall()
    for info in piBilled:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        if info['month']==lastMonthMonth:
            result[info['clinic']]['billed']['pi']['current']=str(info['piBilled'])
        if info['month']==monthBeforeLastMonthMonth:
            result[info['clinic']]['billed']['pi']['previous']=str(info['piBilled']) 


     #### Get Insurance Collection for the last two months       
    sql = "SELECT SUM(P.charged) AS insuranceCollection,CL.name AS clinic "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id=P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id=A.customerID "\
          "LEFT JOIN clinics CL ON CL.id=CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id=CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id=P.providerID "\
          "WHERE P.tranSubType='IN' AND P.transactionDate>=%s AND P.transactionDate<%s AND "\
          "PR.name NOT LIKE '%%cryo t%%' AND CT.name NOT LIKE '%%cryo%%' AND P.tranSubType<>'OT' AND "\
          "(CT.name NOT LIKE '%%PI%%' AND CT.name NOT LIKE '%%WC%%' ) "\
          "GROUP BY CL.name "

    cursor.execute(sql,(dateToString(lastMonth),dateToString(thisMonth)))
    insuranceCollection = cursor.fetchall()
    for info in insuranceCollection:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        result[info['clinic']]['collection']['insurance']=str(info['insuranceCollection'])


     #### Get pi Collection for the last two months       
    sql = "SELECT SUM(P.charged) AS piCollection,CL.name AS clinic "\
           "FROM payments P "\
           "LEFT JOIN appointments A ON A.id=P.appointmentID "\
           "LEFT JOIN customers CU ON CU.id=A.customerID "\
           "LEFT JOIN clinics CL ON CL.id=CU.clinicID "\
           "LEFT JOIN casetypes CT ON CT.id=CU.casetypeID "\
           "LEFT JOIN providers PR ON PR.id=P.providerID "\
           "WHERE P.tranType='P' AND P.transactionDate>=%s AND  "\
           "P.transactionDate<%s AND PR.name NOT LIKE '%%cryo t%%' AND "\
           "CT.name NOT LIKE '%%cryo%%' AND P.tranSubType<>'OT' AND "\
           "(CT.name LIKE '%%PI%%' OR CT.name LIKE '%%WC%%' ) "\
          "GROUP BY CL.name "

    cursor.execute(sql,(dateToString(lastMonth),dateToString(thisMonth)))
    piCollection = cursor.fetchall()
    for info in piCollection:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        result[info['clinic']]['collection']['pi']=str(info['piCollection'])


    #### Get otc Collection for the last two months       
    sql = "SELECT SUM(P.charged) AS otcCollection,CL.name AS clinic "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id=P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id=A.customerID "\
          "LEFT JOIN clinics CL ON CL.id=CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id=CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id=P.providerID "\
          "WHERE P.tranType='P' AND P.tranSubType IN ('CC','CK','CS','DD') AND  "\
          "P.transactionDate>=%s AND P.transactionDate<%s AND  "\
          "PR.name NOT LIKE '%%cryo t%%' AND CT.name NOT LIKE '%%cryo%%' AND  "\
          "P.tranSubType<>'OT' AND ( CT.name NOT LIKE '%%PI%%' AND CT.name NOT LIKE '%%WC%%') "\
          "GROUP BY CL.name "

    cursor.execute(sql,(dateToString(lastMonth),dateToString(thisMonth)))
    otcCollection = cursor.fetchall()
    for info in otcCollection:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        result[info['clinic']]['collection']['otc']=str(info['otcCollection'])


    #### Get copay/coins/ded Collection for the last two months       
    sql = "SELECT SUM(P.charged) AS copayCollection,CL.name AS clinic "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id = P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id = A.customerID "\
          "LEFT JOIN clinics CL ON CL.id = CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id = CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id = P.providerID "\
          "WHERE P.tranType = 'P' AND P.tranSubType <> 'IN' AND "\
          "P.transactionDate >= %s AND P.transactionDate < %s AND "\
          "CT.name NOT LIKE '%%cryo%%' AND CT.name NOT LIKE '%%denied care%%' AND  "\
          "CT.name NOT IN('Weight Loss','DO NOT USE','Wellness','Weight Loss Cas') AND  "\
          "CT.name NOT LIKE '%%cash%%' AND CT.name NOT LIKE '%%vip%%' AND  "\
          "CT.name NOT LIKE '%%massage%%' "\
          "GROUP BY CL.name "

    cursor.execute(sql,(dateToString(lastMonth),dateToString(thisMonth)))
    copayCollection = cursor.fetchall()
    for info in copayCollection:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        result[info['clinic']]['collection']['copay/coins/ded']=str(info['copayCollection'])


    #### Get Chiro Charges for the last month
    sql = "SELECT SUM(P.charged) AS chiroCharges,CL.name AS clinic "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id = P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id = A.customerID "\
          "LEFT JOIN clinics CL ON CL.id = CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id = CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id = P.providerID "\
          "WHERE P.tranSubType ='SV' AND P.transactionDate >= %s AND  "\
          "P.transactionDate < %s AND PR.Specialty='Chiro' "\
          "GROUP BY CL.name "

    cursor.execute(sql,(dateToString(lastMonth),dateToString(thisMonth)))
    chiroCharges = cursor.fetchall()
    for info in chiroCharges:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        result[info['clinic']]['specialty']['chiro']=str(info['chiroCharges'])


    #### Get PT Charges for the last month
    sql = "SELECT SUM(P.charged) AS ptCharges,CL.name AS clinic "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id = P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id = A.customerID "\
          "LEFT JOIN clinics CL ON CL.id = CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id = CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id = P.providerID "\
          "WHERE P.tranSubType ='SV' AND P.transactionDate >= %s AND  "\
          "P.transactionDate < %s AND PR.Specialty='PT' "\
          "GROUP BY CL.name "

    cursor.execute(sql,(dateToString(lastMonth),dateToString(thisMonth)))
    ptCharges = cursor.fetchall()
    for info in ptCharges:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        result[info['clinic']]['specialty']['pt']=str(info['ptCharges'])


    #### Get MD Charges for the last month
    sql = "SELECT SUM(P.charged) AS mdCharges,CL.name AS clinic "\
          "FROM payments P "\
          "LEFT JOIN appointments A ON A.id = P.appointmentID "\
          "LEFT JOIN customers CU ON CU.id = A.customerID "\
          "LEFT JOIN clinics CL ON CL.id = CU.clinicID "\
          "LEFT JOIN casetypes CT ON CT.id = CU.casetypeID "\
          "LEFT JOIN providers PR ON PR.id = P.providerID "\
          "WHERE P.tranSubType ='SV' AND P.transactionDate >= %s AND  "\
          "P.transactionDate < %s AND PR.Specialty='MD' "\
          "GROUP BY CL.name "

    cursor.execute(sql,(dateToString(lastMonth),dateToString(thisMonth)))
    mdCharges = cursor.fetchall()
    for info in mdCharges:
        if info['clinic'] not in result.keys():
            result[info['clinic']]={'billed':{'total':{},'insurance':{},'pi':{}},'collection':{'insurance':'','pi':'','copay/coins/ded':'','otc':''},'specialty':{'chiro':'','md':'','pt':''}} 
        result[info['clinic']]['specialty']['md']=str(info['mdCharges'])



    client = boto3.client('sqs',region_name='us-west-2',
    endpoint_url='https://sqs.us-west-2.amazonaws.com')
    queueInfo = client.get_queue_url(QueueName='MonthEnd')
    for clinic in result.keys():
        client.send_message(
                            QueueUrl = queueInfo['QueueUrl'],
                            MessageBody=result[clinic]
                        )

    print(result)
    return True
