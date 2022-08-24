#!/usr/bin/env python3

import os
import queue
import socket
import pymysql

#from matplotlib.pyplot import eventplot
import certutil
import ssl
import xmltodict

from xml.etree import cElementTree as ElementTree

cert_pass = "atakatak"  #TODO ENV
IP = "161.35.154.238"   #TODO ENV
PORT = 8089             #TODO ENV

SQLUSER = "root"    #TODO ENV
SQLPASS = "mypass"  #TODO ENV

SCRT = certutil.CERT_PATH + "/server.crt"
CCRT = certutil.BOT_CERT_PATH + "/taky-connect.crt"
CKEY = certutil.BOT_CERT_PATH + "/taky-connect.key"

def main():

  certutil.build_certs(cert_pass)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock_ssl = ssl.wrap_socket(sock, ca_certs=SCRT, cert_reqs=ssl.CERT_NONE, certfile=CCRT, keyfile=CKEY)
  conn = sock_ssl.connect((IP, PORT))
  if (sock_ssl._connected == True):
    print("[+] Connected to TAKY")

  while(True):
    rawcot = sock_ssl.recv()
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
  
  # sql_conn = pymysql.connect(host='localhost', user=SQLUSER, password=SQLPASS, cursorclass=pymysql.cursors.DictCursor)

  # cursor = sql_conn.cursor()

  # cursor.execute('CREATE DATABASE IF NOT EXISTS taky;')
  # sql_conn.commit()
  return

if __name__ == '__main__':
  main()