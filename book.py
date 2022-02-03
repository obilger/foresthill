'''
pour lister les entrées: crontab -l
pour editer la crontab: 
export EDITOR=nano
crontab -e

entree crontab:
1 0 * * WED python3 $HOME/foresthill/book.py olivier HIITSTRONG

Alt+H pour terminal ds rep courant
'''

import json
import requests
import sys
import argparse
import urllib.parse
from datetime import timedelta, date
import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


parser = argparse.ArgumentParser()
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('activity', choices=['BODYATTACK','HIITSTRONG','RPM','RPMXL','BODYPUMP','BODYBALANCE','CXWORKS','PILATES'], default='BODYATTACK')
parser.add_argument('-s', '--slot', help='default value: 0', type=int, default=0)
parser.add_argument('-t', '--test', help='default value: false', action='store_true')
parser.add_argument('-l', '--list', help='default value: false', action='store_true')
args = parser.parse_args()

username = args.username
password = args.password
activity = args.activity
activities = {'BODYATTACK':7, 'HIITSTRONG': 1852, 'RPM': 115, 'RPMXL': 119, 'BODYPUMP': 35, 'BODYBALANCE': 88, 'CXWORKS': 36, 'PILATES': 111}
activity_id = activities[activity]
slot = args.slot
test = args.test
list_activities = args.list


file_handler = RotatingFileHandler(username+'.log', 'a', 10000)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# création d'un second handler qui va rediriger chaque écriture de log
# sur la console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)





# calcul de la date de la semaine prochaine 
# le script est lance a 00:01 pour reserver une place pour la semaine prochaine
today = date.today()
next_week = today + timedelta(days=7)
str_next_week = next_week.strftime('%Y-%m-%d')

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
text = 'Capture session ID & access token'
logging.info(text)


url = 'http://api.forest-hill.fr/oauth/v2/token?client_id=1_1n7nbckev468kw4kgswcgw0sg40sc88gc8swog0sgocs0o0g0k&client_secret=45gxoi6ikwowsk00k44gc04sc4s8ksssg4ckg4c48gw80s8gwc&grant_type=password&password=' + password + '&username=' + username
payload = {}
response = session.get(url, headers=headers, data=payload)
try: 
    tokens = json.loads(response.text)
except Exception as e:
    text = 'Erreur chargement json string: ' + str(e)
    logging.error(text)
    
    text = 'Response:' + response.text
    logging.error(text)
    
    sys.exit(-1)
else:
    try: 
        text = 'access token: ' + tokens['access_token']
        logging.info(text)
        
        text = 'session id: ' + session.cookies['PHPSESSID']
        logging.info(text)
        
    except Exception as e:
        text = 'Erreur parsing json object: ' + str(e)
        logging.error(text)
        
        text = 'Response:' + response.text
        logging.error(text)
        
        sys.exit(-1)

if list_activities:

    url = 'http://api.forest-hill.fr/V1/club/2/activity-groups?access_token=' + tokens['access_token']
    payload = {}
    response = session.get(url,  headers=headers, data = payload)
    logging.error(response.text)
    activities = json.loads(response.text)
    pairs = activities. items()
    for key, value in pairs:
        print(value)

else:
    text = activity + ' pour le ' + str_next_week + ' - slot ' + str(slot)
    logging.info(text)

    text = 'Collecte des slots'
    logging.info(text)

    url = 'http://api.forest-hill.fr/V1/booking/club/2/activity/' + str(activity_id) + '/date/' + str_next_week + '?access_token=' + tokens['access_token']
    payload = {}
    response = session.get(url, headers=headers, data=payload)

    try:
        slots = json.loads(response.text)
    except Exception as e:
        text = 'Erreur chargement json string: ' + str(e)
        logging.error(text)
        
        text = 'Response:' + response.text
        logging.error(text)
        
        sys.exit(-1)
    else:
        try:  
            externalid = slots[int(slot)]['externalId']
            bookable = slots[int(slot)]['link']
        except Exception as e:
            text = 'Erreur parsing json object: ' + str(e)
            logging.error(text)
            
            text = 'Response:' + response.text
            logging.error(text)
            
            sys.exit(-1)
        else:
            text = 'externalId: ' + str(externalid)
            logging.info(text)
            
            text = 'bookable: ' + str(bookable)
            logging.info(text)
            


    if not test:
        text = '-- Reservation'
        

        logging.info(text)
        if bookable:
            url = 'http://api.forest-hill.fr/V1/Redshift/booking/' + str(externalid) + '/subscribe?access_token=' + tokens['access_token']
            payload = {}
            response = session.post(url, headers=headers, data=payload)
            logging.info(response.text)
        else:
            text = 'Cours complet !'
            logging.info(text)
            
            sys.exit(99)

    else:
        text = 'Mode TEST, reservation abandonnee'
        logging.info(text)
        