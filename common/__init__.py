from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice, NumberedCanvas
import datetime
from collections import defaultdict
from dateutil import parser
import os

creator = Creator('Life in Harmony @ VCC Admin')
os.environ["INVOICE_LANG"] = "en"

# name, individual_clinic_rate, couples_clinic_rate,
clinicRates = defaultdict(list)
percentRates = {'Alex': 65, 'Lisa': 60, 'Mary': 60, 'Helena': 60}
transition = {'Dave': '2019-10-18', 'Stefanie': '2090-01-01', 'Rosemary': '2090-01-01'}


def getPercent(isPercentage, param):
    if isPercentage:
        if percentRates.get(param) is not None:
            return percentRates.get(param)
        else:
            return 60
    else:
        return 60


class Common:

    def getRate(self, name, subtotal, service_type):
        if clinicRates.get(name) is None:
            if subtotal is not None:
                return 45
            else:
                return 0
        elif str(service_type).lower().find('individual') != -1:
            #individual
            if clinicRates.get(name)[0] is not None:
                return clinicRates.get(name)[0]
            else:
                return 45

        elif str(service_type).lower().find('couples') != -1:
            if clinicRates.get(name)[1] is not None:
                return clinicRates.get(name)[1]
            else:
                return 45
        else:
            return 0

    def isRental(self, name, date):
        if transition.has_key(name) and date < transition.get(name):
            return True
        elif transition.has_key(name) and date >= transition.get(name):
            return False
        else:
            return False

    def getInvoiceRowInfo(self, client, counsellingType, invoice, invoiceid, isPartialInvoice, noshow, provider, row, sDate):
        abbrName = row['client']
        if str(abbrName).strip() != '':
            firstLast = str(row['client']).split(' ')
            if firstLast is not None and firstLast[0] is not None and firstLast[1] is not None:
                abbrName = firstLast[0] + ' ' + firstLast[1][0]
        else:
            abbrName = 'Unknown'
        abbrName = abbrName + " (" + row['invoice_date'] + ")"
        if invoice is None:
            invoice = Invoice(client, provider, creator)
            invoice.date = parser.parse(sDate)
            invoice.number = invoiceid
            invoice.use_tax = True
            invoice.currency_locale = 'en_US.UTF-8'
            invoice.currency = 'CAD'
        if str(counsellingType).lower().find('no show') != -1:
            noshow = True
        abbrName, multiplier = self.getServiceTypeMultiplier(abbrName, counsellingType, isPartialInvoice)
        return abbrName, invoice, multiplier, noshow

    def getServiceTypeMultiplier(self, abbrName, counsellingType, isPartialInvoice):
        multiplier = 1
        if str(counsellingType).lower().find('1.5') != -1 or str(counsellingType).lower().find('90min') != -1:
            multiplier = 1.5
            abbrName = abbrName + "-1.5 HOUR"
        elif str(counsellingType).lower().find('0.5') != -1 or str(counsellingType).lower().find('30min') != -1 \
                or str(counsellingType).lower().find('30 minute') != -1:
            multiplier = 0.5
            abbrName = abbrName + "-0.5 HOUR"
        if isPartialInvoice:
            multiplier = 0
            abbrName = abbrName + "-CORR LAST INV"
        return abbrName, multiplier

    def addItem(self, SWorPsy, abbrName, invoice, isPercentage, isRental, multiplier, noshow, row):
        #if self.isRental(row['name'], row['invoice_date']):

        subcat = None
        if row['service_type'] is not None and (str(row['service_type']).lower().find('psycholo') != -1):
            subcat = 'psy'
        elif row['service_type'] is not None and (
                        str(row['service_type']).lower().find('sw supervision') != -1 or str(
                    row['service_type']).lower().find('rsw') != -1):
            subcat = 'sw'

        if isRental:
            if row['subtotal'] is None or row['subtotal'] == 0:
                if noshow:
                    invoice.add_item(Item(1, 0, abbrName, tax=13))
                else:
                    invoice.add_item(Item(1, 0, abbrName, 'INVALID'))
            # elif row['status'] != 'paid':
            #     invoice.add_item(Item(1, 0, abbrName, 'UNPAID'))
            # this is the condition where we need to check exactly for the amount.
            elif row['status'] != 'cancelled':
                if row['subtotal'] is not None and row['subtotal'] == 45:
                    invoice.add_item(Item(1, 45, abbrName, tax=13))
                elif row['subtotal'] is not None and row['subtotal'] == 30:
                    invoice.add_item(Item(1, 30, abbrName, tax=13))
                elif row['subtotal'] is not None and row['subtotal'] > 45:
                    invoice.add_item(Item(1, 45, abbrName, tax=13))
                #elif row['subtotal'] is not None and row['subtotal'] <= 130:
                #    invoice.add_item(Item(1, 30, abbrName, tax=13))
            elif row['status'] == 'cancelled' and row['associate_invoice_fk'] is not None:
                if row['subtotal'] is not None and row['subtotal'] == 45:
                    invoice.add_item(Item(1, -45, abbrName, tax=13))
                elif row['subtotal'] is not None and row['subtotal'] == 30:
                    invoice.add_item(Item(1, -30, abbrName, tax=13))
                elif row['subtotal'] is not None and row['subtotal'] > 45:
                    invoice.add_item(Item(1, -45, abbrName, tax=13))
                #elif row['subtotal'] is not None and row['subtotal'] <= 130:
                 #   invoice.add_item(Item(1, -30, abbrName, tax=13))

        elif SWorPsy == 'psy' or SWorPsy == 'sw':
            # supervision
            if row['subtotal'] is None or row['subtotal'] == 0:
                if noshow:
                    invoice.add_item(Item(1, 0, abbrName))
                else:
                    invoice.add_item(Item(1, 0, abbrName, 'INVALID'))
            elif row['status'] != 'paid':
                invoice.add_item(Item(1, 0, abbrName, 'UNPAID'))
            elif SWorPsy == 'psy':
                invoice.add_item(Item(1, 30, abbrName, tax=0))
            else:
                invoice.add_item(Item(1, 20, abbrName, tax=0))
        elif isPercentage:
            if row['subtotal'] is None or row['subtotal'] == 0:
                if noshow:
                    invoice.add_item(Item(1, 0, abbrName))
                else:
                    invoice.add_item(Item(1, 0, abbrName, 'INVALID'))
            elif row['status'] == 'cancelled':
                # If cancelled, the amount needs to be deducted
                abbrName, prevmultiplier = self.getServiceTypeMultiplier(abbrName, row['service_type'], False)
                if subcat is None:
                    invoice.add_item(Item(1, -(row['subtotal'] * getPercent(isPercentage, row['name'])/100), abbrName, tax=0 if row['tax'] == 0 else 13))
                elif subcat == 'sw':
                    invoice.add_item(Item(1, -(((row['subtotal'] - 20) * getPercent(isPercentage, row['name'])/100) + 20), abbrName, tax=0 if row['tax'] == 0 else 13))
                elif subcat == 'psy':
                    invoice.add_item(Item(1, -(((row['subtotal'] - 30) * getPercent(isPercentage, row['name'])/100) + 30), abbrName, tax=0 if row['tax'] == 0 else 13))

            elif row['status'] != 'paid':
                invoice.add_item(Item(1, 0, abbrName, 'UNPAID'))
            elif row['subtotal'] is not None:
                # invoice.add_item(Item(1, row['subtotal']-45, abbrName, tax=0 if row['tax']==0 else 13))
                if subcat is None:
                    invoice.add_item(Item(1, (row['subtotal'] * getPercent(isPercentage, row['name'])/100), abbrName, tax=0 if row['tax'] == 0 else 13))
                elif subcat == 'sw':
                    invoice.add_item(Item(1, ((row['subtotal'] - 20) * getPercent(isPercentage, row['name'])/100) + 20, abbrName, tax=0 if row['tax'] == 0 else 13))
                elif subcat == 'psy':
                    invoice.add_item(Item(1, ((row['subtotal'] - 30) * getPercent(isPercentage, row['name'])/100) + 30, abbrName, tax=0 if row['tax'] == 0 else 13))

        else:
            if row['subtotal'] is None or row['subtotal'] == 0:
                if noshow:
                    invoice.add_item(Item(1, 0, abbrName))
                else:
                    invoice.add_item(Item(1, 0, abbrName, 'INVALID'))
            elif row['status'] == 'cancelled':
                # If cancelled, the amount needs to be deducted
                abbrName, prevmultiplier = self.getServiceTypeMultiplier(abbrName, row['service_type'], False)
                #if row['subtotal'] is not None and (row['subtotal'] > 130 or multiplier < 1):
                    # invoice.add_item(Item(1, row['subtotal']-45, abbrName, tax=0 if row['tax']==0 else 13))
                invoice.add_item(
                        Item(1, -(row['subtotal'] - self.getRate(row['name'], row['subtotal'], row['service_type']) * prevmultiplier), abbrName, tax=0 if row['tax'] == 0 else 13))
                #elif row['subtotal'] is not None and row['subtotal'] <= 130:
                    # invoice.add_item(Item(1, row['subtotal'] -30, abbrName, tax=0 if row['tax']==0 else 13)))
                #   invoice.add_item(
                #        Item(1, -(row['subtotal'] - self.getRate(row['name'], row['subtotal'], row['service_type']) * prevmultiplier), abbrName, tax=0 if row['tax'] == 0 else 13))
            elif row['status'] != 'paid':
                invoice.add_item(Item(1, 0, abbrName, 'UNPAID'))
            else:
                # invoice.add_item(Item(1, row['subtotal'] -30, abbrName, tax=0 if row['tax']==0 else 13)))
                invoice.add_item(
                    Item(1, (row['subtotal'] - self.getRate(row['name'], row['subtotal'], row['service_type']) * multiplier), abbrName, tax=0 if row['tax'] == 0 else 13))

    def updateAssociateInovice(self, database, invoicePath, invoiceid):
        invoice = None
        noshow = False
        cursor = database.cursor()


        cursor.execute('''SELECT * FROM associate_invoices where id=?''', [invoiceid])
        as_invoice = cursor.fetchone()

        if as_invoice is not None:
            cursor.execute('''SELECT * FROM invoices where associate_invoice_fk=?''', [invoiceid])
            sDate = as_invoice['invoice_date']

            allinvoices = cursor.fetchall()
            collector = None
            for row in allinvoices:
                collector = row['name']
                isPercentage = False
                if collector == 'Alex E' or collector == 'Mary' or collector == 'Lisa' or collector == 'Helena':
                    isPercentage = True

                client, provider = self.returnProviderCollector(collector, row['invoice_date'])

                counsellingType = row['service_type']
                isPartialInvoice = row['is_partial_invoice']
                #sDate = row['invoice_date']
                #provider = row['name']
                abbrName, invoice, multiplier, noshow = self.getInvoiceRowInfo(client, counsellingType, invoice, invoiceid,
                                                                          isPartialInvoice, noshow, provider, row, sDate)

                self.addItem('', abbrName, invoice, isPercentage, self.isRental(row['name'], row['invoice_date']), multiplier, noshow, row)

            today = datetime.datetime.now().today()


            if invoice is not None:
                cursor.execute('''UPDATE associate_invoices set total=?, subtotal=?, tax=? 
                        where id=?''', (
                    float(invoice.price_tax), float(invoice.price), float(invoice.price_tax - invoice.price), invoiceid))

                #invoice.title = 'Associate-Client Summary'
                pdf = SimpleInvoice(invoice)
                pdf.drawString(
                    (20 + 90) * 2.834,
                    260 * 2.834,
                    _(u'Associate-Client Summary num.: %s') % invoice.number,
                )
                pdfPath = invoicePath + "/" + collector + "-" + provider.address + "-" + str(
                    today.strftime("%Y%m%d-%H%M%S")) + ".pdf";
                pdf.gen(pdfPath,
                        generate_qr_code=True)
                #pdf.drawImage()
                file = open(pdfPath, 'r')
                file_content = file.read()
                cursor.execute('''UPDATE associate_invoices set invoice_file=? 
                        where id=?''', (file_content, invoiceid))
                database.commit()

    def returnProviderCollector(self, collector, invDate):
        payee = 'Life in Harmony at Vaughan Counselling Centre'
        if self.isRental(collector, invDate):
            client = Client(collector)
            provider = Provider(payee, bank_account=' ', bank_code=' ')
        else:
            client = Client(payee)
            provider = Provider(collector, bank_account=' ', bank_code=' ')
        return client, provider



print 'hi'
# = {'Kelly-Lee',[49.87, 56.99]}