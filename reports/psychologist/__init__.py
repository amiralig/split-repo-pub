
import smtplib
import sys

from email.mime.text import MIMEText
from datetime import datetime
import sqlite3

sent_from = 'tekbridgeconsulting@gmail.com'
to = ['amiralig@gmail.com','info@lifeinharmony.ca','info@tekbridge.ca']

subject = 'Psychologist Report'
from email.utils import COMMASPACE, formatdate
from email.mime.multipart import MIMEMultipart

def emailPsychologist(list, invoice_date, invoice_date2):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        # server.sendmail(sent_from, to, 'List is as follows:')

        part1 = MIMEText(list, 'html')

        msg = MIMEMultipart('alternative')
        msg['From'] = sent_from
        msg['To'] = COMMASPACE.join(to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject + ": "+invoice_date+ " - " +invoice_date2
        msg.attach(part1)


        server.sendmail(sent_from, to, msg.as_string())
        server.close()

    except Exception as e:
        print 'Something went wrong...' + e.message

def reportPsychologist(dbPath, invoice_date, invoice_date2):
    db = sqlite3.connect(dbPath + "/lifeVCC")
    # f = open(filePath, "r")
    cursor = db.cursor()
    #cursor1 = db.cursor()
    db.row_factory = sqlite3.Row
    db.text_factory = str
    sDate = datetime.strptime(invoice_date, '%Y-%m-%d')
    eDate = datetime.strptime(invoice_date2, '%Y-%m-%d')

    cursor.execute('''select client, name, i.invoice_date from invoices i join supervisor_invoices s on i.supervisor_invoice_fk = s.id where i.status <> 'cancelled' and s.supervisor_type='PSY' and i.invoice_date >= ? and i.invoice_date < ? order by i.invoice_date''',
                   (sDate, eDate))
    all_invoices = cursor.fetchall()
    line = "<table><tr><td>Client<td>Therapist<td>Date</tr>"
    for one in all_invoices:
        line = line + "<tr>"+"<td>"+one[0] + "<td>" + one[1] + "<td>" + one[2] + "</tr>"
    return line

dbPath = sys.argv[1]
list=reportPsychologist(dbPath, sys.argv[2], sys.argv[3])
emailPsychologist(list, sys.argv[2], sys.argv[3])
