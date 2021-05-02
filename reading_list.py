from __future__ import print_function
import requests
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from bs4 import BeautifulSoup
import parser
import io
import email
import boto3
from datetime import datetime
from datetime import timedelta
import json


s3 = boto3.resource('s3') 

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main(event=None, context=None):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
   
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('/var/task/src/token.json'):
        creds = Credentials.from_authorized_user_file('/var/task/src/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/var/task/src/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            #creds = flow.run_console()
        # Save the credentials for the next run
        with open('/tmp/token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

 
    # Call the Gmail API to get a list of message id from the subscribed email ids
    results = service.users().messages().list(userId='your@email.id',
                                              q='from:(subscibed@email.one OR subscibed@email.two OR subscibed@email.three)').execute()
    msgIdDict = results.get('messages', [])

    print(msgIdDict)

    msgIdList = []

    for item in msgIdDict:
        msg_id = item['id']
        msgIdList.append(msg_id)


    web_page = '<p>A feed of some good email newsletters that I subscribe to. Updates daily.</p><br>'

    #Traverse the list of message ids to extract subject, email body and from

    for msg in msgIdList:
        message = service.users().messages().get(
            userId='your@email.id', id=msg, format='full').execute()

        timestamp = int(message['internalDate'])/1000
        internal_date = datetime.fromtimestamp(timestamp)


        #Only check emails arrived in the last 24 hours
        if ((datetime.now() - internal_date) < timedelta(hours=24)):
            snippet = message['snippet'].encode('ascii', 'ignore').decode()
            message_header = message['payload']['headers']

            by = '~ '

            #Subject and from are found in the header of the response
            for element in message_header:
                if element['name'] == 'Subject':
                    subject = element['value']
                if element['name'] == 'From':
                    by = by + element['value']
             

            message = service.users().messages().get(
                userId='your@email.id', id=msg, format='raw').execute()
            messageBody = base64.urlsafe_b64decode(
                message['raw'].encode('ASCII'))
            msg_str = email.message_from_bytes(messageBody)


            #Body is found in the payload of the response
            if msg_str.is_multipart():
                for part in msg_str.get_payload():
                    messageBody = part.get_payload(decode=True)
                # more processing?
            else:
                messageBody = msg_str.get_payload(decode=True)

            #Parse HTML using BeautifulSoup
            messageBody = BeautifulSoup(messageBody, 'html.parser')

            #Write the email body to an html file
            with io.open("/tmp/"+msg+".html", "w", encoding="utf-8") as file:
                file.write(str(messageBody))

            #Save to the body of the email as an html file in s3
            key = msg + '.html'
            bucket_name = YOUR_BUCKET_NAME
            s3.Bucket(bucket_name).upload_file('/tmp/'+msg+'.html', msg+'.html', ExtraArgs={"ContentDisposition": 'inline',
                                                                                                "ContentType": 'text/html', "ACL": 'public-read'
                                                                                                })

            #Fetch s3 url
            url = "https://s3-%s.amazonaws.com/%s/%s" % (
                YOUR_SERVER_REGION, bucket_name, key)

            #Prepare list to be sent as response - add HTML
            if by == '~ ':
                web_page = web_page + '<h4><a href='+url+' target='+'_blank'+'>'+subject+'</h4></a><p><br></p><br>'
            else:
                web_page = web_page + '<h4><a href='+url+' target='+'_blank'+'>'+subject+'</h4></a><p><i>'+by+'</i><br></p><br>'

           

        else:
            break


    #After the loop has prepared the email list, fetch last 24 hours' data from Pocket API        
    try:
    	d = datetime.today() - timedelta(days=1)
    	d = datetime.timestamp(d)
    	parameters = {"consumer_key": YOUR_KEY ,"access_token": YOUR_TOKEN,  "sort": "oldest", "since": d}
    	pocket_response = requests.get("https://getpocket.com/v3/get", params=parameters)

    	article_list = json.loads(pocket_response.text)
    	article_list = article_list['list']
    	for item in article_list:
        	pocket_url = article_list[item]['resolved_url']
       		pocket_title = article_list[item]['resolved_title']

	        try:
	            if article_list[item]['domain_metadata'] != None:
	                pocket_by = '~ ' + \
	                    article_list[item]['domain_metadata']['name']
	            else:
	                pocket_by = pocket_url.split('/')[2]
	        except:
	            pocket_by = '~ ' + pocket_url.split('/')[2]

          #Add to the response list
	        web_page = web_page + '<h4><a href='+pocket_url+' target='+'_blank'+'>'+pocket_title+'</h4></a><p><i>'+pocket_by+'</i><br></p><br>'

    except:
    	pass

    #Write the response to a text file
    with io.open("/tmp/html_code.txt", "w", encoding="utf-8") as file:
        file.write(web_page)

    #Save to s3
    s3.Bucket(bucket_name).upload_file('/tmp/html_code.txt', 'html_code.txt', ExtraArgs={"ContentDisposition": 'inline',
                                                                                                "ContentType": 'text/html', "ACL": 'public-read'
                                                                                                })

    return "fin."


if __name__ == '__main__':
    main()
