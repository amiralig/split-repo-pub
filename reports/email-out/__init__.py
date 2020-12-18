import sqlite3
import sys
import smtplib
from email.mime.base import MIMEBase
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from email.mime.multipart import MIMEMultipart


class Email:
    dict = {'Sabrina': 'sabrinag@lifeinharmony.ca',
            'Dave': 'davek@lifeinharmony.ca',
            'Stefanie': 'stefanief@lifeinharmony.ca',
            'Mariella': 'mariellap@lifeinharmony.ca',
            'Johanna': 'johannag@lifeinharmony.ca',
            'Joanne': 'joanned@lifeinharmony.ca',
            'Sandra': 'sandram@lifeinharmony.ca',
            'Meri': 'meric@lifeinharmony.ca',
            'Melissa': 'melissap@lifeinharmony.ca',
            'Teresa': 'teresac@lifeinharmony.ca',
            'Peter': 'peterm@lifeinharmony.ca',
            'Rosemary': 'rosemaryc@lifeinharmony.ca',
            'Mary':'maryd@lifeinharmony.ca',
            'Lisa':'lisab@lifeinharmony.ca',
            'Helena':'helenab@lifeinharmony.ca',
            'Alex': 'alexe@lifeinharmony.ca'

            }



    # dictTest = {'Dave': 'amiralig@gmail.com', 'Alex': 'info@tekbridge.ca'}

    def __init__(self):
        self.sent_from = 'info@lifeinharmony.ca'
        self.to = ['amiralig@gmail.com']
        self.subject = 'Payroll'

    def get_payroll(self, dbPath, invoice_date):

        try:

            db = sqlite3.connect(dbPath + "/lifeVCC")
            # f = open(filePath, "r")
            cursor = db.cursor()
            cursor1 = db.cursor()
            db.row_factory = sqlite3.Row
            db.text_factory = str
            sDate = datetime.strptime(invoice_date, '%Y-%m-%d')
            cursor.execute('''select name, invoice_date, invoice_file from associate_invoices where invoice_date > ?''',
                           (sDate,))
            all_invoices = cursor.fetchall()
            for one in all_invoices:
                print one[0]
                print one[1]
                self.reportUnpaid(one[2], invoice_date, one[0], None)

            cursor1.execute(
                '''select super_name, invoice_date, invoice_file, supervisor_type from supervisor_invoices where invoice_date > ?''',
                (sDate,))
            all_invoices = cursor1.fetchall()
            for one in all_invoices:
                print one[0]
                print one[1]
                self.reportUnpaid(one[2], invoice_date, one[0], one[3])

        except Exception as e:
            print e.message
            # Roll back any change if something goes wrong
            db.rollback()
            raise e

        finally:
            # Close the db connection
            cursor.close()
            cursor1.close()
            db.close()

    def reportUnpaid(self, f, invoice_date, name, supervisor):
        try:
            print 'jl' + 'Here\'s the list: '
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            # server.sendmail(sent_from, to, 'List is as follows:')

            msg = MIMEMultipart()
            msg['From'] = self.sent_from
            if self.dict[name] is not None:
                msg['To'] = self.dict[name]
            else:
                return
            msg['Date'] = formatdate(localtime=True)
            if supervisor is not None:
                subject = self.subject + '-' + supervisor + '-' + invoice_date
            else:
                subject = self.subject + '-' + invoice_date
            msg['Subject'] = subject

            inv_name = ''
            if supervisor is not None:
                inv_name = ' ' + supervisor
            body = 'Dear ' + name + ',\n'+'Please find attached your' + inv_name + ' invoice as of ' + invoice_date + '. Kindly let Sabrina (sabrinag@lifeinharmony.ca) know if any issues with this invoice. This is an automated message. \n' + 'Regards'
            body = MIMEText(body)

            msg.attach(body)
            # msg['Content-Type'] = "text/html"

            with open("/Users/amirali/temp/tosend.pdf", 'wb') as file:
                file.write(f)

            part = MIMEBase('application', "octet-stream")
            part.set_payload(open("/Users/amirali/temp/tosend.pdf", "rb").read())
            encoders.encode_base64(part)
            # Encoders.encode_base64(part)
            if supervisor is not None:
                filename = name + '-' + supervisor + '-' + invoice_date
            else:
                filename = name + '-' + invoice_date
            part.add_header('Content-Disposition', 'attachment; filename="' + filename + '.pdf"')

            # After the file is closed
            msg.attach(part)
            server.sendmail(self.sent_from, self.dict[name], msg.as_string())
            server.close()

        except Exception as e:
            print 'Something went wrong...' + e.message


email = Email()
dbPath = sys.argv[1]
email.get_payroll(dbPath=dbPath, invoice_date='2020-11-27')
# email.reportUnpaid()
