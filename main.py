import os
import logging
import i18n
import json
from datetime import datetime, timezone, timedelta
import threading
import queue

import Guest_Entry_Register

# Constants
DEFAULT_LANG = 'ja'
JST = timezone(timedelta(hours=+9), 'JST')
DATETIME_FORMAT = '%Y-%m-%d %H:00' 

# Logging
logging.getLogger().setLevel(logging.INFO)

# i18n Configuration
base_path = os.path.dirname(os.path.abspath(__file__))
i18n.load_path.append(os.path.join(base_path, './locales'))
i18n.set('filename_format', '{locale}.{format}')
i18n.set('file_format', 'yaml')
i18n.set('skip_locale_root_data', True)

# Set locale
def set_locale(lang):
  i18n.set('locale', lang)
  i18n.set('fallback', DEFAULT_LANG)

# Entry point
def guest_entry_registration(request):
  logging.info('Guest Entry Registeration...[Start]')

  if not request.method == 'POST':
    return 'Service is Up and Running....'

  # Request
  request_body = request.get_data()
  request_json = request.get_json()
  
  # Load json payload from request body
  if request_json is None:
    logging.info('Loading json payload from request body')
    data = request_body.decode('utf8')
    params = json.loads(data)

  logging.info(params)

  # Dialog Submission
  if 'type' in params and params['type'] == 'dialog_submission':
    # Queue
    que = queue.Queue()
    # Add thread
    thread = threading.Thread(target=lambda q, arg1: q.put(
            Guest_Entry_Register.register(arg1)), args=(
            que, params))
    # Execute thread
    logging.info('Processing Thread.....[START]')
    thread.start()
    thread.join()
    logging.info('Processing Thread.....[END]')

    # Get thread response
    res = que.get()
    if not isinstance(res, bool) and res is not None:
      return res
    else:
      return json.dumps({})
  else:
    logging.info('Open slack dialog to enter guest details')

    # Locale setting
    set_locale(params['lang'])

    # Slack user not found
    if params['user_real_name'] == '':
      logging.info('Slack user not found....[ERROR]')
      # Return response
      return json.dumps({
        'slack': True,
        'type': 'message',
        'message': i18n.t('MESSAGE_GUEST_REGISTER_USER_NOT_FOUND'),
        'channel': params['channel']
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
                            'value': params['user_real_name']},
                          {'type': 'text',
                            'label': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_CONTACT_PHONE'),
                            'name': 'contact_phone',
                            'placeholder': i18n.t('MESSAGE_GUEST_REGISTER_LABEL_CONTACT_PHONE'),
                            'value': params['user_phone']}]}

    # Return response
    return json.dumps({
      'slack': True,
      'type': 'dialog',
      'dialog': DIALOG,
      'trigger_id': params['trigger_id'],
      'channel': params['channel']
    })