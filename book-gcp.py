import json
import requests
import sys
import argparse
import urllib.parse
from datetime import timedelta, date


import logging
# Imports the Cloud Logging client library
import google.cloud.logging

# Instantiates a client 
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.get_default_handler()
client.setup_logging()


parser = argparse.ArgumentParser()
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('activity', choices=['BODYATTACK','GRITFORCE','RPM','RPMXL','BODYPUMP','BODYBALANCE','CXWORKS','PILATES'])
parser.add_argument('-s', '--slot', help='default value: 0', type=int, default=0)
parser.add_argument('-t', '--test', help='default value: false', action='store_true')
args = parser.parse_args()


username = args.username
password = args.password
activity = args.activity
activities = {'BODYATTACK':7, 'GRITFORCE': 101, 'RPM': 115, 'RPMXL': 119, 'BODYPUMP': 35, 'BODYBALANCE': 88, 'CXWORKS': 36, 'PILATES': 111}
activity_id = activities[activity]
slot = args.slot
test = args.test

# calcul de la date de la semaine prochaine 
# le script est lance a 00:01 pour reserver une place pour la semaine prochaine
today = date.today()
next_week = today + timedelta(days=7)
str_next_week = next_week.strftime('%Y-%m-%d')

logging.info('Tentative reservation ' + activity + ' pour le ' + str_next_week + ' - slot: ' + str(slot))

session = requests.Session()

headers = {
  'accept': '*/*',
  'accept-encoding': 'gzip, deflate',
  'accept-language': 'fr-fr',
  'connection': 'keep-alive',
  'host': 'api.forest-hill.fr',
  'proxy-connection': 'keep-alive',
  'user-agent': 'ForestHill/260 CFNetwork/1197 Darwin/20.0.0',
}

# capture session ID & access token
logging.info('Capture session ID & access token')
url = 'http://api.forest-hill.fr/oauth/v2/token?client_id=1_1n7nbckev468kw4kgswcgw0sg40sc88gc8swog0sgocs0o0g0k&client_secret=45gxoi6ikwowsk00k44gc04sc4s8ksssg4ckg4c48gw80s8gwc&grant_type=password&password=' + password + '&username=' + username
payload = {}
response = session.get(url, headers=headers, data=payload)
try: 
    tokens = json.loads(response.text)
except Exception as e:
    logging.error('Erreur chargement json string: ' + str(e))
    logging.error('Response:' + response.text)
    sys.exit(-1)
else:
    try: 
        logging.info('access token: ' + tokens['access_token'])
        logging.info('session id: ' + session.cookies['PHPSESSID'])
    except Exception as e:
        logging.error('Erreur parsing json object: ' + str(e))
        logging.error('Response:' + response.text)
        sys.exit(-1)


"""
liste des activites
url = 'http://api.forest-hill.fr/V1/club/2/activity-groups?access_token=' + tokens['access_token']
payload = {}
response = session.get(url,  headers=headers, data = payload)
logging.error(response.text)
activities = json.loads(response.text)
print(actvities)
"""

"""
json_string = '{ {"id": 35, "name": "Body Pump"},{"id": 101, "name": "Grit Force"},{"id": 7, "name": "Body Attack"}'
#json_string = '{"id": 35, "name": "Body Pump"}'
activities = json.loads(json_string)
print(activities['name'])
"""

logging.info('Collecte des slots')
url = 'http://api.forest-hill.fr/V1/booking/club/2/activity/' + str(activity_id) + '/date/' + str_next_week + '?access_token=' + tokens['access_token']
payload = {}
response = session.get(url, headers=headers, data=payload)

try:
    slots = json.loads(response.text)
except Exception as e:
    logging.error('Erreur chargement json string: ' + str(e))
    logging.error('Response:' + response.text)
    sys.exit(-1)
else:
    try:  
        externalid = slots[int(slot)]['externalId']
        bookable = slots[int(slot)]['link']
    except Exception as e:
        logging.error('Erreur parsing json object: ' + str(e))
        logging.error('Response:' + response.text)
        sys.exit(-1)
    else:
        logging.info('externalId: ' + str(externalid))
        logging.info('bookable: ' + str(bookable))


if not test:

    if bookable:
        url = 'http://api.forest-hill.fr/V1/Redshift/booking/' + str(externalid) + '/subscribe?access_token=' + tokens['access_token']
        payload = {}
        response = session.post(url, headers=headers, data=payload)
        logging.info(response.text)
    else:
        logging.info('Cours plein !')
        sys.exit(99)
else:
    
    logging.info('Mode TEST, reservation abandonnee')