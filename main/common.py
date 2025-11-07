from functools import wraps
from main import session, redirect, request, url_for, app
from datetime import datetime
import time
import os

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if session.get('userID') is None or session.get('userID') =='':
      return redirect(url_for('member.member_login', next_url=request.url))
    return f(*args, **kwargs)
  return decorated_function

@app.template_filter('formatdatetime')
def format_datetime(value):
  now_timestamp = time.time()
  offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
  value = datetime.fromtimestamp(int(value) / 1000) + offset
  return value.strftime('%Y-%m-%d %H:%M:%S')

@app.template_filter('fileNameParsing')
def fileNameParsing(value):
  fileName = value.split('\\')[-1]
  return fileName

def UserFolderCreate(userDirectory, request):
  ip_address = str(request.remote_addr)
  current_utc_time = str(round(datetime.utcnow().timestamp() * 1000))
  user_folder = ip_address + '_' + current_utc_time
  os.chdir(userDirectory)
  userFolder = os.path.join(userDirectory, user_folder)
  os.mkdir(userFolder)
  return userFolder

def ReceiveFileSave(userFolder, filename, request):
  f = request.files[filename]
  bdf_file = os.path.join(userFolder, f.filename)
  f.save(bdf_file)
  return bdf_file
