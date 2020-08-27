import os
import logging
import i18n
import json
import threading
import queue
import guest_entry
import dialog

# Logging
logging.getLogger().setLevel(logging.INFO)

# i18n Configuration
base_path = os.path.dirname(os.path.abspath(__file__))
i18n.load_path.append(os.path.join(base_path, './locales'))
i18n.set('filename_format', '{locale}.{format}')
i18n.set('file_format', 'yaml')
i18n.set('skip_locale_root_data', True)


# Entry point
def main(request):
  logging.info('========[START]========')

  if not request.method == 'POST':
    return 'Service is Up and Running....'

  # Request parameters
  payload = request.get_data()
  params = json.loads(payload)
  logging.info(params)

  # Queue
  que = queue.Queue()

  # Dialog Submission
  if 'type' in params and params['type'] == 'dialog_submission':
    # Add thread
    thread = threading.Thread(target=lambda q, arg1: q.put(
            guest_entry.register(arg1)), args=(
            que, params))
  # Open Dialog
  else:
    # Add thread
    thread = threading.Thread(target=lambda q, arg1: q.put(
            dialog.guest_entry_dialog(arg1)), args=(
            que, params))
  
  # Execute thread
  thread.start()
  thread.join()

  # Send response
  res = que.get()
  if not isinstance(res, bool) and res is not None:
    return res
  else:
    return json.dumps({})