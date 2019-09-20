#!/usr/bin/python3
# conding=utf-8
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



def getIDcardinfo_1(txt_file):
   
    with open (txt_file,"r",encoding="utf-8") as f:
        opt_text = f.read()

    txt=opt_text.encode('utf-8').decode('utf-8-sig')
    judge=re.findall('中華民國|國民|身分證|發證日期',txt)
    

    if len(judge)>0:
      all_text=re.findall(u"[\w\W\u4e00-\u9fff]+",opt_text)
      name=re.findall(u"姓名\s*[\u4e00-\u9fa5]{0,4}",opt_text)
      cop = re.compile("[^\u4e00-\u9fa5^.^0-9]")
      if len(name)>0:
        name[0] = re.sub(cop,"", name[0])
        name[0] = re.sub("姓","", name[0])
        name[0] = re.sub("名","", name[0])
      birth=re.findall(u"民國\d{2,3}年\d{1,2}月\d{1,2}日",opt_text)
      getting_Date=re.findall(u"民國\d{2,3}年\d{1,2}月\d{1,2}日.+發",opt_text)
      personal_ID=re.findall('[A-Z]{0,1}[0-9]{9}',opt_text)
      # print(all_text)
      if len(birth)> 1:
        del birth[1]
      
      print(name,birth,getting_Date,personal_ID)
      return name,birth,getting_Date,personal_ID
    else :
      print("請確認上傳文件是否正確")

def getIDcardinfo_2(txt_file):
  with open (txt_file,"r",encoding="utf-8") as f:
        opt_text = f.read()
  

  txt=opt_text.encode('utf-8').decode('utf-8-sig')
  judge=re.findall('配偶|役別|出生地',txt)
  if len(judge)>0: 
    txt1=re.sub("\s","",txt)
    parents_name=re.findall('父\s*[\u4e00-\u9fa5]{2,3}母*[\u4e00-\u9fa5\s]{2,3}|父*\s*[\u4e00-\u9fa5]{2,3}母\s*[\u4e00-\u9fa5\s]{2,3}',txt1)
    if len(parents_name)>0:
      cop1 = re.compile(u"父|母")
      parents_name[0]=re.sub(cop1,"",parents_name[0])
    parents_name.append(parents_name[0][0:3])
    parents_name.append(parents_name[0][3:6])
    del parents_name[0]
    print(parents_name)

    address=re.sub("[0-9]{10}","",opt_text)
    address=re.findall('[\u4e00-\u9fa5]{2}[市縣][\u4e00-\u9fa50-9]{2,4}[鄉鎮市區][\u4e00-\u9fa50-9\s\n]+',address)

    if len(address)>0: 
      cop2 = re.compile(u"住址|址|任址")
      address[0]=re.sub(cop2,"",address[0])
      address[0]=re.sub("\n|\s","",address[0])
      
    print(address)
    return parents_name,address
  else :
    print("請確認上傳文件是否正確")



def getIDcardinfo_3(txt_file):
  with open (txt_file,"r",encoding="utf-8") as f:
        opt_text = f.read()
  txt=opt_text.encode('utf-8').decode('utf-8-sig')
  judge=re.findall('全民健康|健康保險',txt)
  if len(judge)>0 :
    name=re.findall('[\u4e00-\u9fa5]{3}\n[A-Z]{1}[0-9]{9}',opt_text)
    cop3=re.compile("\n[A-Z]{1}[0-9]{9}")
    name[0]=re.sub(cop3,"",name[0])
    personal_ID=re.findall('[A-Z]{0,1}[0-9]{9}',opt_text)
    birth=re.findall("[0-9]{2}/[0-9]{2}/[0-9]{2}",opt_text)
    NHI_num=re.findall("[0-9]{4}\s[0-9]{4}\s[0-9]{4}",opt_text)
    print(name,personal_ID,birth,NHI_num)
  else:
    print("請確認上傳文件是否正確")

def OCR(txt_file,card_type):
  if card_type ==1 : 
    getIDcardinfo_1(txt_file)  #身分證正面
  elif card_type==2:
    getIDcardinfo_2(txt_file)  #身分證背面
  elif card_type==3:
    getIDcardinfo_3(txt_file)  #健保卡正面 


def main(filename,card_type):

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

  
  OCR('output.txt',card_type)
  






if __name__ == '__main__':
    
  start_time=time.time()
  file_name="cooper_IDH.jpg"
  print("Img : " + file_name + " reading....\n")
  main(file_name,3) 
  #身分證正面:1
  #身分證背面:2
  #健保卡正面:3
  end_time=time.time()
  print("Spending Time:",end_time-start_time,"\n")
  


