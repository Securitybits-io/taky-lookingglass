#!/usr/bin/env python3

import os
import socket
from sqlite3 import SQLITE_DROP_TABLE
import pymysql
import ssl
import xmltodict
import certutil

from queue import Queue
from threading import Thread
from xml.etree import cElementTree as ElementTree

cert_pass = "atakatak"  #TODO ENV
IP = "161.35.154.238"   #TODO ENV
PORT = 8089             #TODO ENV

SQLUSER = "root"    #TODO ENV
SQLPASS = "mypass"  #TODO ENV
SQLDB   = "TAKYCoT"    #TODO ENV

SCRT = certutil.CERT_PATH + "/server.crt"
CCRT = certutil.BOT_CERT_PATH + "/taky-connect.crt"
CKEY = certutil.BOT_CERT_PATH + "/taky-connect.key"

def getCOT(socket, queue):
  print('[+] Thread started, waiting on CoTs...')

  while(True):

    rawcot = socket.recv()
    #queue.put(rawcot)
    
    # Below should be moved to another function
    # as the following doesnt really pertain to the getCOT producer thread
    cot = xmltodict.parse(rawcot)
    print(cot)
    
    if ('a-f-G-U-C' in cot['event']['@type']):
      detail = cot['event']['detail']
      
      time = cot['event']['@time']
      callsign = detail['contact']['@callsign']
      group = detail['__group']['@name']
      role = detail['__group']['@role']
      coords = cot['event']['point']

      log = '{} | {} | {} | {} | {} | {}'.format(time, callsign, group, role, coords['@lat'], coords['@lon'])
      print(log)


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



  sql = pymysql.connect(host='localhost', user=SQLUSER, password=SQLPASS, db=SQLDB, cursorclass=pymysql.cursors.DictCursor)
  if sql.open:
    sql_configure(sql)
    
if __name__ == '__main__':
  main()