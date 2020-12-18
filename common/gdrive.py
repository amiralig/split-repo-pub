from __future__ import print_function
import os
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']

class GDrive:
    def share_file(self, userList, file):
        service = self.create_service()
        for i in userList:
            print('Sharing folder with '+i)
            service.permissions().create(body={"role": "reader", "type": "user", "emailAddress": i},
                                    fileId=file).execute()

    def create_drive(self, start_date, end_date):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        service = self.create_service()

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        folder_name = sys.argv[1]
        if folder_name is None:
            print('Folder nam should be non-empty')
            exit(1)


        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

        file_metadata = {
            'name': 'payroll-lifeVCC-'+start_date+'-to-'+end_date,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = service.files().create(body=file_metadata,
                                            fields='id').execute()


        print('File ID issssssss: %s' % file.get('id'))
        return file

    def create_service(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('drive', 'v3', credentials=creds)
        return service

    def create_file(self, file, pdf_name, pdf_path):
        service = self.create_service()
        file_metadata = {
            'name': pdf_name,
                    'parents': [file.get('id')]
        }
        media = MediaFileUpload(pdf_path,
                                mimetype='application/pdf')
        file2 = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        return file2