#!/usr/bin/python3
from __future__ import print_function
import httplib2
import io
import re,os
import sys
import time

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Python OCR'

def get_credentials():
  """取得有效的憑證
     若沒有憑證，或是已儲存的憑證無效，就會自動取得新憑證

     傳回值：取得的憑證
  """
  # credential_path = os.path.join("./", 'google-ocr-credential.json')
  # credential_path = os.path.join("./", 'credentials.json')
  credential_path = os.path.join("./", 'google-ocr-credential.json')
  
  store = Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
      credentials = tools.run_flow(flow, store, flags)
    else: # Needed only for compatibility with Python 2.6
      credentials = tools.run(flow, store)
    print('憑證儲存於：' + credential_path)
  return credentials



def getIDcardinfo(txt_file):
   
    with open (txt_file,"r",encoding="utf-8") as f:
        opt_text = f.read()

    all_text=re.findall(u"[\w\W\u4e00-\u9fff]+",opt_text)
    name=re.findall(u"姓名\s*[\u4e00-\u9fa5]{0,4}",opt_text)
    cop = re.compile("[^\u4e00-\u9fa5^.^0-9]")
    if len(name)>0:
      name[0] = re.sub(cop," ", name[0])
    birth=re.findall(u"民國\d{2,3}年\d{1,2}月\d{1,2}日",opt_text)
    getting_Date=re.findall(u"民國\d{2,3}年\d{1,2}月\d{1,2}日.+發",opt_text)
    personal_ID=re.findall('[A-Z]{0,1}[0-9]{9}',opt_text)
    # print(all_text)
    if len(birth)> 1:
      del birth[1]
    
    print(name,birth,getting_Date,personal_ID)


def main(filename):

  # 取得憑證、認證、建立 Google 雲端硬碟 API 服務物件
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('drive', 'v3', http=http)

  # 包含文字內容的圖片檔案（png、jpg、bmp、gif、pdf）
  imgfile = filename

  # 輸出辨識結果的文字檔案
  txtfile = 'output.txt'

  # 上傳成 Google 文件檔，讓 Google 雲端硬碟自動辨識文字
  mime = 'application/vnd.google-apps.document'
  res = service.files().create(
    body={
      'name': imgfile,
      'mimeType': mime
    },
    media_body=MediaFileUpload(imgfile, mimetype=mime, resumable=True)
  ).execute()

  # 下載辨識結果，儲存為文字檔案
  downloader = MediaIoBaseDownload(
    io.FileIO(txtfile, 'wb'),
    service.files().export_media(fileId=res['id'], mimeType="text/plain")
  )
  done = False
  while done is False:
    status, done = downloader.next_chunk()

  # 刪除剛剛上傳的 Google 文件檔案
  service.files().delete(fileId=res['id']).execute()

  
  getIDcardinfo("output.txt")
  




if __name__ == '__main__':
  for i in range(8):
    start_time=time.time()
    j=i
    file_name="IDtest"+ str(j) +'.jpg'
    print("IDcard "+ str(j)+" reading....\n")
    main(file_name)
    end_time=time.time()
    print("Spending Time:",end_time-start_time,"\n")

  
  # start_time=time.time()
  # file_name="ID.jpg"
  # print(file_name + " reading....\n")
  # main(file_name)
  # end_time=time.time()
  # print("Spending Time:",end_time-start_time,"\n")
  
