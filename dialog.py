import os
import i18n
import json
import logging
from datetime import datetime, timezone, timedelta

# Constants
DEFAULT_LANG = 'ja'
JST = timezone(timedelta(hours=+9), 'JST')
DATETIME_FORMAT = '%Y-%m-%d %H:00' 

# Set locale
def set_locale(lang):
  i18n.set('locale', lang)
  i18n.set('fallback', DEFAULT_LANG)

# Open dialog
def guest_entry_dialog(params):
  logging.info('Open dialog for guest entry')
  logging.info(params)

  # Locale setting
  set_locale(params['lang'])

  # Slack user not found
  if params['user']['real_name'] == '':
    logging.info('Slack user not found....[ERROR]')
    # Return response
    return json.dumps({
      'slack': True,
      'type': 'message',
      'message': i18n.t('MESSAGE_GUEST_REGISTER_USER_NOT_FOUND'),
      'channel': params['channel']['id']
    })

  # Set default time to 1 hour from now
  now = datetime.now(JST)
  time = (now + timedelta(hours=1)).strftime(DATETIME_FORMAT)
    
  # Dialog Box
  DIALOG = {'callback_id': 'T_Guestentry_Yes',
            'title': i18n.t('MESSAGE_GUEST_REGISTER_DIALOG_TITLE'),
            'submit_label': i18n.t('MESSAGE_GUEST_REGISTER_DIALOG_SUBMIT'),
            'state': params['lang'],
            'notify_on_cancel': True,
            'elements': [{'type': 'text',
                          'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_COMPANY_NAME'),
                          'name': 'company_name',
                          'placeholder': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_COMPANY_NAME')},
                        {'type': 'text',
                          'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_VISITOR_NAME'),
                          'name': 'visitor_name'},
                        {'type': 'text',
                          'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_NUMBER_OF_VISITORS'),
                          'name': 'number_of_visitors',
                          'placeholder': 3},
                        {'type': 'text',
                          'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_MEETING_TIME'),
                          'name': 'meeting_time',
                          'value': time,
                          'placeholder': 'YYYY-MM-DD HH:MM',
                          'hint': i18n.t('MESSAGE_GUEST_REGISTER_HINT_MEETING_TIME')},
                        {'type': 'select',
                          'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_MEETING_FLOOR'),
                          'name': 'meeting_floor',
                          'options': [{'label': '18{postfix}'.format(postfix=i18n.t('MESSAGE_GUEST_REGISTER_LABEL_FLOOR_POSTFIX')),
                                      'value': 18},
                                      {'label': '21{postfix}'.format(postfix=i18n.t('MESSAGE_GUEST_REGISTER_LABEL_FLOOR_POSTFIX')),
                                      'value': 21},
                                      {'label': '25{postfix}'.format(postfix=i18n.t('MESSAGE_GUEST_REGISTER_LABEL_FLOOR_POSTFIX')),
                                      'value': 25},
                                      {'label': '43{postfix}'.format(postfix=i18n.t('MESSAGE_GUEST_REGISTER_LABEL_FLOOR_POSTFIX')),
                                      'value': 43}]},
                        {'type': 'text',
                          'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_CONTACT_NAME'),
                          'name': 'contact_name',
                          'placeholder': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_CONTACT_NAME'),
                          'value': params['user']['real_name']},
                        {'type': 'text',
                          'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_CONTACT_PHONE'),
                          'name': 'contact_phone',
                          'placeholder': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_CONTACT_PHONE'),
                          'value': params['user']['phone']}]}

  # Return response
  return json.dumps({
    'slack': True,
    'type': 'dialog',
    'dialog': DIALOG,
    'trigger_id': params['trigger_id'],
    'channel': params['channel']['id']
  })