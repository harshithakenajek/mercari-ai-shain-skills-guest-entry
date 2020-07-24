# -*- coding: utf-8 -*-
import os
import requests
import json
import logging
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
import i18n
import mojimoji

# Env Vars
EHILLS_MEMBER_ID = os.environ.get('EHILLS_MEMBER_ID')
EHILLS_PASSWORD  = os.environ.get('EHILLS_PASSWORD')

# Constants
JST = timezone(timedelta(hours=+9), 'JST')
LOGIN_URL = 'https://www.ehills.co.jp/sso/dfw'
HIDE_URL = '/EHILLS/damiyLogin.php'
LOGIN_KEYWORD = 'ICEWALL_LOGIN'
ACCOUNT_UID = 'ehills_{member_id}'
COMPANY_NAME = 'Mercari'
USER_TITLE = 'No Title'
ADVANCE_REGISTRATION_URL = 'https://www.ehills.co.jp/sso/dfw/AVR/visitor/login.asp'
GUEST_ENTRY_REGISTRATION_URL = 'https://www.ehills.co.jp/sso/dfw/AVR/visitor/input_e.asp'
CONFIRM_REGISTRATION_URL = 'https://www.ehills.co.jp/sso/dfw/AVR/visitor/regist_e.asp'
ERROR_MESSAGE = 'ERROR: {}'

# Session
session = requests.Session()

def register(request):
  logging.info('Registration....[START]')

  # Locale setting
  i18n.set('locale', request['state'])
  
  # Login for registration
  res = login(request)
  return res

def login(request):
  logging.info('Login to eHills...[START]')
  try:
    payload = {
        'PLAIN_ACCOUNTUID': EHILLS_MEMBER_ID,
        'PASSWORD': EHILLS_PASSWORD,
        'HIDEURL': HIDE_URL,
        'LOGIN': LOGIN_KEYWORD,
        'ACCOUNTUID': ACCOUNT_UID.format(member_id=EHILLS_MEMBER_ID),
        'log': 'login',
        'co': ''
    }
    logging.info(payload)

    res = session.post(
        url=LOGIN_URL,
        data=payload
    )
    soup = BeautifulSoup(res.text, 'html.parser')
    if soup.find('div', class_="sub-title") is not None:
      error_msg = soup.find('div', class_="sub-title").text
      logging.error('Login ERROR: ' + error_msg)
      # Send error message to slack
      return json.dumps({
        'slack': True,
        'type': 'message',
        'message': i18n.t('MESSAGE_GUEST_ENTRY_LOGIN_ERROR'),
        'channel': request['channel']['id']
      })
    else:
      logging.info('Login to eHills...[OK]')
      # Register new guest entry
      res = register_guest_entry(request)
      return res

  except BaseException:
    logging.error('Login to eHills...[ERROR]')
    return json.dumps({})

def register_guest_entry(request):
  try:
    # Advance visitor registration link
    res = session.get(
        url=ADVANCE_REGISTRATION_URL,
        params={'buil': 66}
    )
    logging.info(res)

    user_title = request['user_title'] if request['user_title'] != '' else USER_TITLE
    
    try:
      guest_meeting_info = request['submission']['meeting_time'].split(' ')
      meeting_date = guest_meeting_info[0].split('-')
      meeting_time = guest_meeting_info[1].split(':')
      year = meeting_date[0]
      month = meeting_date[1]
      day = meeting_date[2]
      hour = meeting_time[0]
      minute = meeting_time[1]
    except BaseException:
      logging.error('Meeting time seems to be in unexpected format')
      logging.error(request['submission']['meeting_time'])
      # Send error message to slack
      return json.dumps({
        'slack': True,
        'type': 'message',
        'message': i18n.t('MESSAGE_GUEST_REGISTER_ERROR_MEETING_TIME'),
        'channel': request['channel']['id']
      })

    today = datetime.now(JST).strftime('%Y/%m/%d')

    payload = {
        'registtype': 'input',
        'repeattype': 1,
        'startdate': today,
        'repeatdate': today,
        'douhanflag': 'false',
        'person': 1,
        'kigyou': request['submission']['company_name'].encode('cp932'),
        'daihyou': request['submission']['visitor_name'].encode('cp932'),
        'ninzu': mojimoji.zen_to_han(request['submission']['number_of_visitors']),
        'repeat': 1,
        'day1': day,
        'month1': month,
        'year1': year,
        'hour1': hour,
        'min1': minute,
        'every': 1,
        'floor': request['submission']['meeting_floor'],
        'hkigyou': COMPANY_NAME,
        'hname': request['submission']['contact_name'].encode('cp932'),
        'hbusho': user_title,
        'htelephone': request['submission']['contact_phone'],
        'ikigyou': COMPANY_NAME,
        'iname': request['submission']['contact_name'].encode('cp932'),
        'ibusho': user_title,
        'itelephone': request['submission']['contact_phone']
    }
    logging.info(payload)

    # New guest registration
    register_res = session.post(
        url=GUEST_ENTRY_REGISTRATION_URL,
        data=payload
    )
    soup = BeautifulSoup(register_res.text, 'html.parser')
    if soup.find('div', class_="errorRed") is not None:
      error_msg = soup.find('div', class_="errorRed").text.strip()
      logging.error('Registration ERROR: ' + error_msg)
      # Send error message to slack
      return json.dumps({
        'slack': True,
        'type': 'message',
        'message': i18n.t('MESSAGE_GUEST_REGISTER_ERROR', error=ERROR_MESSAGE.format(error_msg)),
        'channel': request['channel']['id']
      })
    else:
      logging.info('Guest entry register....[OK]')
      # Confirm guest registration
      confirm_reg = session.post(url=CONFIRM_REGISTRATION_URL)
      
      # Extract the reservation number for guest visit
      soup = BeautifulSoup(confirm_reg.text, 'html.parser')
      if soup.find('p', class_="reservenumber") is not None:
        reservation_text = soup.find('p', class_="reservenumber").text
        pin = reservation_text.split('Visit Reservation Number is ')[1]
        
        # Send completion message and visit reservation number to slack
        # Posting as an ephemeral message
        requests.post(request['response_url'], data=json.dumps(
            {"text":  i18n.t('MESSAGE_GUEST_ENTRY_RESERVATION_OK') + '\n\n' + 
                      i18n.t('MESSAGE_GUEST_ENTRY_RESERVATION_RESULT',
                            pin=pin,
                            company_name=request['submission']['company_name'],
                            visitor_name=request['submission']['visitor_name'],
                            number_of_visitors=mojimoji.zen_to_han(
                                request['submission']['number_of_visitors']),
                            meeting_time=request['submission']['meeting_time'],
                            meeting_floor=request['submission']['meeting_floor'],
                            contact_name=request['submission']['contact_name'],
                            contact_phone=request['submission']['contact_phone'])}))
        logging.info("Confirm guest registeration PIN...[OK]")
      else:
        logging.error("Confirm guest registeration PIN...[ERROR]")
  except BaseException:
    logging.error('Guest entry register...[ERROR]')
    return json.dumps({})
