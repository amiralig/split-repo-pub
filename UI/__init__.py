import json

import os


from Crypto.Cipher import AES
from OpenSSL import SSL
from Padding import removePadding, appendPadding
from flask import Flask, request, render_template, jsonify, send_file, send_from_directory, flash, redirect
from flask_restful import Resource, Api
import sys
import openpyxl
import datetime
import sqlite3
from dateutil import parser
from dateutil import relativedelta
from werkzeug.utils import secure_filename
from Crypto.Protocol.KDF import PBKDF2
from flask import Markup

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
api = Api(app)
app.secret_key = "secret key of life in harmony app"
salt = dummy
dbPath = "/app/git/lifeVCC-pay"
filePath = "/app/upload"

# use decorators to link the function to a url
@app.route('/')
def home():
    return "Hello, World!"  # return a string

@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    print 'fdfdsfdsfsd'
    data = json.loads(request.data.decode())
    url = data["url"]
    if 'http://' not in url[:7]:
        url = 'http://' + url

    return '333333333'

@app.route('/index')
def welcome():
    return render_template('index.html')  # render a template


@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/upload')
def file_upload():
    return render_template('upload.html')

@app.route('/uploaded', methods=['POST'])
def upload():
    tmpDir = filePath + '/'
    if request.method == 'POST':
        # check if the post request has the file part

        if 'file' not in request.files:
            flash('No file part')
            return redirect('/upload')
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect('/upload')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename).lower()
            file.save(os.path.join(tmpDir, filename))
            tmp = open(tmpDir+'/'+filename, 'rb')
            data = tmp.read()
            writeEncrypted(data, tmpDir+ '/'+filename)
            filenameparts = str(file.filename).split(".")
            if filenameparts is not None and filenameparts[0] is not None:
                message = Markup('File successfully uploaded: <a href="'+"http://52.24.118.196:5002/download?"+"clientid="+filenameparts[0]+'">'+filenameparts[0]+"</a>")
                flash(message)
            else:
                message = Markup('File successfully uploaded: <a href="' + "http://52.24.118.196:5002/download?" + "clientid=" + filename+'">'+filename+"</a>")
                flash(message)
            return redirect('/upload')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect('/upload')




def writeEncrypted(data, output_file):
    password = 'dummy'  # Password provided by the user, can use input() to get this
    #v = os.urandom(16)

    key = PBKDF2(password, salt, dkLen=32)  # Your key that you can encrypt with
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC,iv)  # Create a AES cipher object with the key using the mode CBC
    ciphered_data = cipher.encrypt(appendPadding(data, AES.block_size))  # Pad the input data and then encrypt

    file_out = open(output_file, "wb")  # Open file to write bytes
    file_out.write(cipher.IV)  # Write the iv to the output file (will be required for decryption)
    file_out.write(ciphered_data)  # Write the varying length cipher text to the file (this is the encrypted data)
    file_out.close()


    # Read the data from the file


@app.route("/poynt", methods=['POST'])
def get_poynt_token():
    accessToken = request.form['accessToken']
    print 'accessToken:'+accessToken


@app.route("/view-client", methods=['POST'])
def view_client ():

    try:
        password = request.form['password']
        client_id = request.form['clientid']
        tmpDir = filePath + '/'

        file_in = None
        for eachType in ALLOWED_EXTENSIONS:
            if os.path.isfile(tmpDir+client_id+'.'+eachType):
                file_in = open(tmpDir+client_id+'.'+eachType, 'rb')  # Open the file to read bytes
            if file_in is not None:
                break
        if file_in is None:
            flash(
                'File not found for client:'+client_id)
            return redirect('/download')
        iv = file_in.read(16)  # Read the iv out - this is 16 bytes long
        ciphered_data = file_in.read()  # Read the rest of the data
        file_in.close()
        key = PBKDF2(password, salt, dkLen=32)  # Your key that you can encrypt with

        cipher = AES.new(key, AES.MODE_CBC, iv)  # Setup cipher
        original_data = removePadding(cipher.decrypt(ciphered_data), AES.block_size)  # Decrypt and then up-pad the result

        basename = os.path.basename(file_in.name)
        file_out1 = open(tmpDir+'dec-'+basename, "wb")
        file_out1.write(original_data)
        file_out1.close()

        #uploads = os.path.join('/Users/amirali/PycharmProjects/CalendarICS/UI/static/', "associate")
        to_send = send_from_directory(directory=tmpDir, filename='dec-'+basename)
        #os.remove('dec-'+client_id+'.pdf')

        return to_send
        #return send_file('/Users/Amirali/associate/'+path)
    except Exception as e:
        print "an exception happend file sending file"+e.message
        flash(
            'File not found for client:' + client_id+", exception:"+e.message)
        return redirect('/download')

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

@app.route("/results/<user_input>/<invoice_date>", methods=['GET'])
def get_results(user_input, invoice_date):
    db = dbPath + "/lifeVCC"

    database = sqlite3.connect(db)
    database.row_factory = sqlite3.Row
    cursor = database.cursor()
    enddate = parser.parse(invoice_date)
    startDate = enddate - relativedelta.relativedelta(months=1)
    results=cursor.execute(
        '''SELECT id, name, invoice_date, tax, subtotal, total, status FROM associate_invoices where name=? and invoice_date <= ? and invoice_date >=?''',
        (user_input,enddate,startDate))
    allinvoices = cursor.fetchall()
    json_output = json.dumps([dict(ix) for ix in allinvoices])

    #return json.dumps([{'status':'hi', 'name':'me'},{'status':'hi1', 'name':'me1'}])
    return json_output


@app.route("/supervisor-results/<user_input>/<invoice_date>", methods=['GET'])
def get_supervisor_results(user_input, invoice_date):
    db = dbPath + "/lifeVCC"
    try:
        database = sqlite3.connect(db)
        database.row_factory = sqlite3.Row
        cursor = database.cursor()
        enddate = parser.parse(invoice_date)
        startDate = enddate - relativedelta.relativedelta(months=1)
        results=cursor.execute(
            '''SELECT id, super_name, invoice_date, tax, subtotal, total, status, supervisor_type FROM supervisor_invoices where super_name=? and invoice_date <= ? and invoice_date >=?''',
            (user_input,enddate,startDate))
        allinvoices = cursor.fetchall()
        json_output = json.dumps([dict(ix) for ix in allinvoices])
        #return json.dumps([{'status':'hi', 'name':'me'},{'status':'hi1', 'name':'me1'}])
    except Exception as e:
        print "an exception happend file sending file"+e.message
        return '1'
    finally:
        # Close the db connection
        database.close()
    return json_output

@app.route("/update-invoice", methods=['POST'])
def update_invoice (path = None):
    if path is None:
        print "path is none"
    try:
        data = json.loads(request.data.decode())
        db = dbPath + "/lifeVCC"

        database = sqlite3.connect(db)
        database.row_factory = sqlite3.Row
        cursor = database.cursor()

        if (data is not None and len(data) > 0):
            for eachInvoice in data:
                print eachInvoice
                tax=eachInvoice['tax']
                id=eachInvoice['id']
                subtotal=eachInvoice['subtotal']
                total=eachInvoice['total']
                cursor.execute(
                    '''update associate_invoices set tax=?, subtotal=?, total=? where id=?''',
                    (tax, subtotal, total, id))

        database.commit()
        return '0'
        #return send_file('/Users/Amirali/associate/'+path)
    except Exception as e:
        print "an exception happend file sending file"+e.message
        return '1'
    finally:
        # Close the db connection
        database.close()

@app.route("/recreate-invoice/<invoice_id>", methods=['POST'])
def createInvoice (invoice_id):
    try:
        db = dbPath + "/lifeVCC"

        database = sqlite3.connect(db)
        database.row_factory = sqlite3.Row
        database.text_factory = str

        invoicePath = dbPath
        invoicePath = invoicePath + "/test"

        from common import Common

        c = Common()
        c.updateAssociateInovice(database=database, invoiceid=invoice_id, invoicePath=invoicePath)


        return '0'
        #return send_file('/Users/Amirali/associate/'+path)
    except Exception as e:
        print "an exception happend file sending file"+e.message
        return '1'
    finally:
        # Close the db connection
        database.close()

@app.route("/api/associate-invoice/<path>")
def getInvoiceFile (path = None):
    if path is None:
        print "path is none"
    try:
        db = dbPath + "/lifeVCC"
        database = sqlite3.connect(db)
        database.row_factory = sqlite3.Row
        database.text_factory = str

        cursor = database.cursor()
        path_to_assoc=dbPath+"/associate/"
        if not os.path.exists(path_to_assoc):
            os.makedirs(path_to_assoc)
        path_to_assoc_file=path_to_assoc+path
        file = open(path_to_assoc_file+".pdf", 'w')
        cursor.execute('''SELECT invoice_file from associate_invoices where id=?''', (path,))
        photo = cursor.fetchone()[0]
        file.write(photo)
        file.close()
        #uploads = os.path.join('/Users/amirali/PycharmProjects/CalendarICS/UI/static/', "associate")
        return send_from_directory(directory=path_to_assoc, filename=path+".pdf")
        #return send_file('/Users/Amirali/associate/'+path)
    except Exception as e:
        print "an exception happend file sending file"+e.message


@app.route("/api/supervisor-invoice/<path>")
def getSuperInvoiceFile (path = None):
    if path is None:
        print "path is none"
    try:
        db = dbPath + "/lifeVCC"
        database = sqlite3.connect(db)
        database.row_factory = sqlite3.Row
        database.text_factory = str

        cursor = database.cursor()
        path_to_super=dbPath+"/supervisor/";
        if not os.path.exists(path_to_super):
            os.makedirs(path_to_super)
        path_to_super_file=path_to_super+path
        file = open(path_to_super_file+".pdf", 'w')
        cursor.execute('''SELECT invoice_file from supervisor_invoices where id=?''', (path,))
        photo = cursor.fetchone()[0]
        file.write(photo)
        file.close()
        #uploads = os.path.join('/Users/amirali/PycharmProjects/CalendarICS/UI/static/', "supervisor")
        return send_from_directory(directory=path_to_super, filename=path+".pdf")
        #return send_file('/Users/Amirali/associate/'+path)
    except Exception as e:
        print "an exception happend file sending file"+e.message

class Employees(Resource):
    def get(self):
        return {'employees': [{'id':1, 'name':'Balram'},{'id':2, 'name':'Tom'}]}

api.add_resource(Employees, '/employees') # Route_1

if __name__ == '__main__':
    context = SSL.Context(SSL.SSLv3_METHOD)
    context.options |= SSL.OP_NO_TLSv1
    context.options |= SSL.OP_NO_TLSv1_1
    context.use_privatekey_file('dummy/cert.pem')
    context.use_certificate_file('dummy/privkey.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context)
