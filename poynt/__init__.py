import requests
import logging
import httplib
import urllib
import json
import sys
import time
import rsa
import uuid
import ConfigParser
import getopt
import jwt
import random
import pprint
import time
import locale
import os
from calendar import timegm
from datetime import datetime, timedelta
from decimal import Decimal
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key, load_ssh_public_key
)





class Poynt:

    def __init__(self):
        self.name = 'Poynt'

    def ensure_bytes(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        return key

    def _sendFormPostRequest(self, url, payload, customHeaders):
        requestId = str(uuid.uuid4())
        commonHeaders = { 'api-version':self.POYNT_API_VERSION,
                    "User-Agent": 'PoyntSample-Python',
                    'Poynt-Request-Id': requestId }
        headers = dict(commonHeaders.items() + customHeaders.items())
        startTime = datetime.now()
        req = requests.Request('POST', url, data=payload, headers=headers)
        prepared = req.prepare()
        if self.debug == True:
            #print 'prettify'
            self.pretty_print_POST(prepared)
        else:
            print "\tPOST " + url
        s = requests.Session()
        r = s.send(prepared)
        endTime = datetime.now()
        delta = endTime - startTime
        print "\tHTTP RESPONSE CODE:" + str(r.status_code)
        print "\tRESPONSE TIME: " + str(delta.total_seconds() * 1000) + " msecs"
        if self.debug == True:
            print "\tRESPONSE JSON:"
            self.prettyPrint(r.json())
        if r.status_code == 401:
            print "\t Request merchant authorization by sending them to: " + self._generateAuthzUrl()
        return r.status_code, r.json()

    def prettyPrint(self, jsonObj):
        print json.dumps(jsonObj, sort_keys=True, indent=4)
        print '*' * 60

    def pretty_print_POST(self, req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".
        However pay attention at the formatting used in
        this function because it is programmed to be pretty
        printed and may differ from the actual request.
        """
        print('{}\n{}\n{}\n\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    def getAccessToken(self):
        poyntTokenUrl = self.apiHost + "/token"
        currentDatetime = datetime.utcnow()
        expiryDatetime = datetime.utcnow() + timedelta(seconds=300)
        payload = {
            'exp': expiryDatetime,
            'iat': currentDatetime,
            'iss': self.applicationId,
            'sub': self.applicationId,
            'aud': 'https://services.poynt.net',
            'jti': str(uuid.uuid4())
        }
        encodedJWT = jwt.encode(payload, self.rsaPrivateKey, algorithm='RS256')
        print 'encodedjwt'+encodedJWT
        payload = {'grantType':'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion':encodedJWT}
        print "Obtaining AccessToken using self-signed JWT:"
        code, jsonObj = self._sendFormPostRequest(poyntTokenUrl, payload, {})
        #r = requests.post(poyntTokenUrl, data=payload, headers=headers)
        #prettyPrint(r.json())
        if code == requests.codes.ok:
            self.accessToken = jsonObj['accessToken']
            self.tokenType = jsonObj['tokenType']
            self.refreshToken = jsonObj['refreshToken']
            return True
        else:
            print "*** FAILED TO OBTAIN ACCESS TOKEN ***"+str(jsonObj)
            return False

    def communicate(self):
        POYNT_CONFIG = ConfigParser.ConfigParser()

        base_dir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))


        POYNT_ENV = 'LIVE'
        self.debug = True

        try:
            opts, args = getopt.getopt(sys.argv, "he:v", ['env=', 'verbose'])
        except getopt.GetoptError:
            print 'PoyntAPI.py -e < CI or LIVE > -v'
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                print 'PoyntAPI.py -e < CI or LIVE > -v'
                sys.exit()
            elif opt in ('-e', '--env'):
                POYNT_ENV = arg.upper()
            elif opt in ('-v', '--verbose'):
                DEBUG = True

        print "Executing APIs in ", POYNT_ENV
        POYNT_CONFIG.read(base_dir + '/config/poynt.ini')
        ### POYNT API URL and VERSION, Application settings
        self.apiHost = POYNT_CONFIG.get(POYNT_ENV, 'POYNT_API_HOST_URL')
        self.POYNT_API_VERSION = POYNT_CONFIG.get(POYNT_ENV, 'POYNT_API_VERSION')
        self.POYNT_AUTHZ_HOST_URL = POYNT_CONFIG.get(POYNT_ENV, 'POYNT_AUTHZ_HOST_URL')
        self.BUSINESS_ID = POYNT_CONFIG.get(POYNT_ENV, 'BUSINESS_ID')
        self.STORE_ID = POYNT_CONFIG.get(POYNT_ENV, 'STORE_ID')
        self.applicationId = POYNT_CONFIG.get(POYNT_ENV, 'APPLICATION_ID')
        self.PRIVATE_KEY_FILE = base_dir + '/' + POYNT_CONFIG.get(POYNT_ENV, 'PRIVATE_KEY_FILE')
        self.PUBLIC_KEY_FILE = base_dir + '/' + POYNT_CONFIG.get(POYNT_ENV, 'PUBLIC_KEY_FILE')
        self.POYNT_PUBLIC_KEY_FILE = base_dir + '/' + POYNT_CONFIG.get(POYNT_ENV, 'POYNT_PUBLIC_KEY_FILE')

        with open(self.PRIVATE_KEY_FILE, 'r') as rsa_priv_file:
            self.rsaPrivateKey = load_pem_private_key(self.ensure_bytes(rsa_priv_file.read()), password=None,
                                                      backend=default_backend())
        with open(self.PUBLIC_KEY_FILE, 'r') as rsa_pub_file:
            self.rsaPublicKey = load_pem_public_key(self.ensure_bytes(rsa_pub_file.read()), backend=default_backend())
        '''with open(self.POYNT_PUBLIC_KEY_FILE, 'r') as rsa_poynt_pub_file:
            self.rsaPoyntPublicKey = load_pem_public_key(self.ensure_bytes(rsa_poynt_pub_file.read()),
                                                         backend=default_backend())'''

    def _generateAuthzUrl(self):
        poyntAuthzUrl = self.POYNT_AUTHZ_HOST_URL + "/applications/authorize?"
        params = { 'applicationId' : self.applicationId,
                    'callback' : 'http://52.24.118.196:5002/poynt',
                    'context' : 'python-test-script'
                    }
        return poyntAuthzUrl + urllib.urlencode(params)

    def _sendGetRequest(self, url, queryParameters, customHeaders):
            commonHeaders = { 'api-version':self.POYNT_API_VERSION,
                        "User-Agent": 'PoyntSample-Python',
                        'Authorization': self.tokenType + " " + self.accessToken }
            headers = dict(commonHeaders.items() + customHeaders.items())
            startTime = datetime.now()
            req = requests.Request('GET', url, params=queryParameters, headers=headers)
            prepared = req.prepare()
            if self.debug == True:
                self.pretty_print_POST(prepared)
            else:
                print "\tGET " + url
            s = requests.Session()
            r = s.send(prepared)
            endTime = datetime.now()
            delta = endTime - startTime
            print "\tHTTP RESPONSE CODE:" + str(r.status_code)
            print "\tRESPONSE TIME: " + str(delta.total_seconds() * 1000) + " msecs"
            if self.debug == True:
                print "\tRESPONSE JSON:"
                self.prettyPrint(r.json())
            if r.status_code == requests.codes.unauthorized:
                print "\t Request merchant authorization by sending them to: " + self._generateAuthzUrl()

            if r.status_code == requests.codes.not_modified:
                print "\t Order not modified since given if-modified-since time"
                return r.status_code, {}
            else:
                return r.status_code, r.json()

    def createOrder(self):
        poyntOrderUrl = self.apiHost + "/businesses/" + self.BUSINESS_ID + "/orders"
        currentDatetime = datetime.utcnow()
        expiryDatetime = datetime.utcnow() + timedelta(seconds=300)
        order = {
          "items":[
              {
                 "status":"FULFILLED",
                 "name":"Coffee",
                 "unitOfMeasure":"EACH",
                 "unitPrice":260,
                 "quantity":1.0,
                 "tax":0,
                 "sku": "ABC123"
              },
              {
                 "status":"FULFILLED",
                 "name":"Bagel",
                 "unitOfMeasure":"EACH",
                 "unitPrice":160,
                 "quantity":1.0,
                 "tax":0,
                 "sku": "ABC122"
              },
              {
                 "status":"FULFILLED",
                 "name":"Cream Cheese",
                 "unitOfMeasure":"EACH",
                 "unitPrice":100,
                 "quantity":1.0,
                 "tax":0,
                 "sku": "ABC122"
              }
           ],
           "amounts": {
              "taxTotal":0,
              "subTotal":500,
              "discountTotal":0,
              "currency":"USD"
           },
           "context": {
              "source":"WEB",
              "businessId": self.BUSINESS_ID,
              "storeId": self.STORE_ID,
              "storeDeviceId": self.applicationId
           },
           "statuses": {
              "status":"OPENED"
           },
           "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }


        print "Recording a new Order:"
        code, jsonObj = self._sendPostRequest(poyntOrderUrl, json.dumps(order), {}, {})


    def _sendPostRequest(self, url, payload, queryParameters, customHeaders):
        requestId = str(uuid.uuid4())
        commonHeaders = { 'api-version':self.POYNT_API_VERSION,
                    "User-Agent": 'PoyntSample-Python',
                    'Poynt-Request-Id': requestId,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Authorization': self.tokenType + " " + self.accessToken}
        headers = dict(commonHeaders.items() + customHeaders.items())
        startTime = datetime.now()
        req = requests.Request('POST', url, data=payload, params=queryParameters, headers=headers)
        prepared = req.prepare()
        if self.debug == True:
            self.pretty_print_POST(prepared)
        else:
            print "\tPOST " + url
        s = requests.Session()
        r = s.send(prepared)
        endTime = datetime.now()
        delta = endTime - startTime
        print "\tHTTP RESPONSE CODE:" + str(r.status_code)
        print "\tRESPONSE TIME: " + str(delta.total_seconds() * 1000) + " msecs"
        if r.status_code == requests.codes.unauthorized:
                    print "\t Request merchant authorization by sending them to: " + self._generateAuthzUrl()
        if r.text and self.debug:
            print "\tRESPONSE JSON:"
            self.prettyPrint(r.json())
        if r.text:
            return r.status_code, r.json()
        else:
            return r.status_code, None

    def getOrders(self):
        poyntOrdersUrl = self.apiHost + "/businesses/" + self.BUSINESS_ID + "/orders"
        print "Fetching last 5 Orders updated in the last 1 month:"
        lastHourDateTime = datetime.now() +  timedelta(hours=24*30)
        headers = { 'If-Modified-Since': lastHourDateTime.strftime("%Y-%m-%dT%H:%M:%SZ") }
        queryParameters = { 'limit': 5 }
        code, jsonObj = self._sendGetRequest(poyntOrdersUrl, queryParameters, headers)

p = Poynt()
p.communicate()
p.getAccessToken()
#p.getOrders()
#p.createOrder()
p.getOrders()