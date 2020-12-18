import openpyxl
import os
import smtplib
import glob
import sys

from email.mime.text import MIMEText
from datetime import datetime
import sqlite3

from collections import defaultdict
try:
        print "yes"
except ImportError:
        print "yws1"
#url = "http://lifeinharmony.janeapp.com/ical/QdK1sX3uAX1O6g1VkJfS/appointments.ics"
print "hi1"

#testfile = urllib.URLopener()
#testfile.retrieve("http://lifeinharmony.janeapp.com/ical/QdK1sX3uAX1O6g1VkJfS/appointments.ics", "/Users/amirali/Downloads/sabrina-appointments.ics")

def jane_sales(combinedFile):
    #with open(combinedFile) as csvfile:
    reader = openpyxl.load_workbook(filename=combinedFile)
    #db = sqlite3.connect(dbXlsxPath+"/lifeVCC")
    unpaid = ''
    try:

        inSheet = reader.get_sheet_by_name('Export')
        #writer = csv.DictWriter(csvwriter, fieldnames=['Customer','Email','Telephone','StartDate','EndDate'])
        #writer.writeheader()
        #myworkbook = openpyxl.load_workbook(filename=separatedFile)
        today = datetime.now()
        myDictionary={}
        therapistDic=defaultdict(list)
        for row in inSheet.rows:
            currentRow = str(row[0].row)
            #outputRow = str(currentRow + 1)
            if currentRow == '1':
                continue
            #print(row['Email'])
            if inSheet['A'+currentRow].value is None:
                break
            firstName = inSheet['G'+currentRow].value
            firstName = str(firstName).split()[0]

            if firstName in myDictionary:
                value = myDictionary[firstName]
                value += 1
                myDictionary[firstName] = value
                #print myDictionary[eachItem]
            else:
                myDictionary[firstName] = 2

            counsellingType=inSheet['F'+currentRow].value
            subtotal = inSheet['L'+currentRow].value
            hst=inSheet['M'+currentRow].value
            total=inSheet['N'+currentRow].value
            invoiceno=inSheet['H'+currentRow].value
            patient=inSheet['D'+currentRow].value
            status=inSheet['L'+currentRow].value
            #worksheet = myworkbook.get_sheet_by_name(firstName)
            #if worksheet
            todayStr = str(today.strftime("%Y%m%d-%H%M%S"))
            date = inSheet['C'+currentRow].value
            #worksheet['A'+str(myDictionary[firstName])].value=date
            #worksheet['C'+str(myDictionary[firstName])].value=subtotal
            #worksheet['B'+str(myDictionary[firstName])].value=hst
            #worksheet['D'+str(myDictionary[firstName])].value=total
            #worksheet['E'+str(myDictionary[firstName])].value=invoiceno
            #worksheet['F' + str(myDictionary[firstName])].value = patient
            #worksheet['']
            if (status == 'unpaid' or str(status).find('partially_paid')!=-1) and str(counsellingType).find('Counselling - Fee Only') == -1:
                firstLast = str(patient).split(' ')
                if (firstLast is not None and firstLast[0] is not None and firstLast[1] is not None):
                    therapistDic[firstName].append(firstLast[0] + ' ' + firstLast[1][0] + ", date: "+date)
                else:
                    therapistDic[firstName].append(patient+ ", date: "+date)

            #myworkbook.save(dbXlsxPath+"-"+todayStr+".xlsx")

        unpaid = ""
        for c, k in therapistDic.iteritems():
            unpaid = unpaid + "----------" + c + "------------" + '\n'
            for patient in k:
                unpaid = unpaid + patient + '\n'
        return unpaid
    except Exception as e:
        print e.message
        # Roll back any change if something goes wrong
        #db.rollback()
        raise e


sent_from = 'tekbridgeconsulting@gmail.com'
to = ['amiralig@gmail.com','info@lifeinharmony.ca','info@tekbridge.ca']

subject = 'LifeatVCC Balance Sheet Report (V3)'
from email.utils import COMMASPACE, formatdate

def reportUnpaid(list):
     try:
         print 'jl'+'Here\'s the list: '+str(list)
         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
         server.ehlo()

         msg = MIMEText(list)
         msg['From'] = sent_from
         msg['To'] = COMMASPACE.join(to)
         msg['Date'] = formatdate(localtime=True)
         msg['Subject'] = subject
         #msg['Content-Type'] = "text/html"



         server.sendmail(sent_from, to, msg.as_string())
         server.close()

     except Exception as e:
         print 'Something went wrong...'+e.message

#list_of_files = glob.glob('/Users/amirali/Downloads/*.xlsx') # * means all if need specific format then *.csv

list_of_files=[]
for file in os.listdir('/Users/amirali/Public/reports'):
    if file.endswith(".xlsx"):
        list_of_files.append('/Users/amirali/Public/reports/'+file)

latest_file = max(list_of_files, key=os.path.getctime)
print latest_file
list=jane_sales(latest_file)
reportUnpaid(list)
