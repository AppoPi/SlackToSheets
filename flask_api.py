from flask import Flask
from flask_restful import Api, Resource, reqparse

from pprint import pprint
import requests
from datetime import datetime

from oauth2client.service_account import ServiceAccountCredentials
import json
import gspread

class CheckIn(Resource):
    # Scope gives permissions to user to read/write
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly',
             'https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    # Spreadsheet id intended to be written to/read from
    spreadsheet_id = '16JpPj52_s3GAglZaslVIHlGfARBe7P8ubN0OjPTnRBg'
    # File that stores the authentication token for Google Sheets
    token_file_name = 'slacktosheets-580c7b119901.json'
    
    
    def post(self):
        # Prepare argument list of Slack values being passed in
        # These are the arguments documented in Slack that you have access
        # to process and use.
        parser = reqparse.RequestParser()
        parser.add_argument('token')
        parser.add_argument('command')
        parser.add_argument('text')
        parser.add_argument('response_url')
        parser.add_argument('trigger_id')
        parser.add_argument('user_id')
        parser.add_argument('user_name')
        parser.add_argument('channel_id')
        args = parser.parse_args()
        
        # Authenticate credentials for access to Google Sheets
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            self.token_file_name, self.scope)
            
        client = gspread.authorize(creds)
        sheet = client.open("SlackToSheet").sheet1
        
        # How to get all values in Google Sheets
        # list_of_hashes = sheet.get_all_records()
        # pprint(list_of_hashes)
        
        # Prepare body hash
        timestamp = datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
        
        body = {
          # Values to be written to "database"
          "values": [
            args['user_name'],timestamp
          ],
        }
        # Append time to Google sheet
        result = sheet.append_row(body)
        
        # Return response to Slack
        # Displays as message in channel
        # 200 is the http response code for "all good"
        return {
            'response_type': 'in_channel',
            'text': 'Thank you, <@' + args['user_id'] + 
                '>, for checking in. The time is: ' + timestamp
        }, 200

# Initialize app
app = Flask(__name__)
api = Api(app)
# Add the api endpoint to your app
api.add_resource(CheckIn, '/checkin/')
# Start running the app so that it will respond to api calls
app.run(host="0.0.0.0", port=int("80"), debug=True)