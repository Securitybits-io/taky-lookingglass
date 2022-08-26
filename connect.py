#!/usr/bin/env python3

import os
import socket
from sqlite3 import SQLITE_DROP_TABLE
import pymysql
import ssl
import xmltodict
import certutil

from datetime import datetime
from queue import Queue
from threading import Thread
from xml.etree import cElementTree as ElementTree

cert_pass = "atakatak"  #TODO ENV
IP = "161.35.154.238"   #TODO ENV
PORT = 8089             #TODO ENV

SQLROOTUSER = "root"    #TODO ENV
SQLROOTPASS = "mypass"  #TODO ENV

SQLUSER = "lookingglass"  #TODO ENV
SQLPASS = "V42Lm4j9"      #TODO ENV
SQLDB   = "TAKYCoT"       #TODO ENV

SCRT = certutil.CERT_PATH + "/server.crt"
CCRT = certutil.BOT_CERT_PATH + "/taky-connect.crt"
CKEY = certutil.BOT_CERT_PATH + "/taky-connect.key"

def getCOT(socket, queue):
  print('[+] Producer Thread started, waiting on CoTs...')

  while(True):
    rawcot = socket.recv()
    queue.put(rawcot)
    

def sql_configure(conn):
  cursor = conn.cursor()
  
  print('[+] Create CoTs table if not exists...')
  cursor.execute('CREATE TABLE IF NOT EXISTS cots (cot_id INT AUTO_INCREMENT PRIMARY KEY, time DATETIME NOT NULL, callsign VARCHAR(24), cot_group VARCHAR(10), role VARCHAR(16), lat DOUBLE, lon DOUBLE);')
  conn.commit()
  
  print('[+] Create Grafana Read-Only User if not exist...')
  cursor.execute('GRANT SELECT ON TAKYCoT.* to "grafana" IDENTIFIED BY "password123";')
  conn.commit()

  cursor.execute('FLUSH PRIVILEGES;')
  conn.commit()
  return


def postCOT(sql, queue):
  print('[+] Consumer Thread started, waiting on queued CoTs...')
  sql_insert = "INSERT INTO `cots` (`time`, `callsign`, `cot_group`, `role`, `lat`, `lon`) VALUES (%s, %s, %s, %s, %s, %s)"

  cursor = sql.cursor()
  while (True):
    if not queue.empty():
      row = queue.get()
      cot = parse_cot(row)

      cursor.execute(sql_insert, (cot['time'], cot['callsign'], cot['tak_color'], cot['tak_role'], cot['lat'], cot['lon']))
      sql.commit()

      print(cot)
  

def parse_cot(rawcot):
  dict_cot = xmltodict.parse(rawcot)
  print(dict_cot)
  
  if ('a-f-G-U-C' in dict_cot['event']['@type']):
    detail = dict_cot['event']['detail']
    
    time = dict_cot['event']['@time']
    callsign = detail['contact']['@callsign']
    color = detail['__group']['@name']
    role = detail['__group']['@role']
    coords = dict_cot['event']['point']

    utc_time = time.replace("Z","UTC")
    utc_dt = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%S.%f%Z")
    #YYYY-MM-DD hh:mm:ss
    cot = {
      "time": time.strip("Z"),
      "callsign": callsign,
      "tak_color": color,
      "tak_role": role,
      "lat": coords['@lat'],
      "lon": coords['@lon'],
    }

    log = '{} | {} | {} | {} | {} | {}'.format(time, callsign, color, role, coords['@lat'], coords['@lon'])
    print(log)
  return cot


def main():
  queue = Queue()
  certutil.build_certs(cert_pass)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock_ssl = ssl.wrap_socket(sock, ca_certs=SCRT, cert_reqs=ssl.CERT_NONE, certfile=CCRT, keyfile=CKEY)
  conn = sock_ssl.connect((IP, PORT))
  if (sock_ssl._connected == True):
    print("[+] Connected to TAKY")
    producer = Thread(target=getCOT, args=(sock_ssl, queue))
    producer.start()

  sql_root = pymysql.connect(host='10.0.40.6', user=SQLROOTUSER, password=SQLROOTPASS, db=SQLDB, cursorclass=pymysql.cursors.DictCursor)
  if sql_root.open:
    sql_configure(sql_root)
    sql_root.close()

  sql = pymysql.connect(host='10.0.40.6', user=SQLUSER, password=SQLPASS, db=SQLDB, cursorclass=pymysql.cursors.DictCursor) 
  if sql.open:
    consumer = Thread(target=postCOT, args=(sql, queue))
    consumer.start()

if __name__ == '__main__':
  main()