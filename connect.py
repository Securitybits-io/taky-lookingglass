#!/usr/bin/env python3

import os
import queue
import socket

from matplotlib.pyplot import eventplot
import certutil
import ssl
import xmltodict

from xml.etree import cElementTree as ElementTree


cert_pass = "atakatak"
IP = "161.35.154.238"
PORT = 8089

SCRT = certutil.CERT_PATH + "/server.crt"
CCRT = certutil.BOT_CERT_PATH + "/taky-connect.crt"
CKEY = certutil.BOT_CERT_PATH + "/taky-connect.key"



certutil.build_certs(cert_pass)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_ssl = ssl.wrap_socket(sock, ca_certs=SCRT, cert_reqs=ssl.CERT_NONE, certfile=CCRT, keyfile=CKEY)
conn = sock_ssl.connect((IP, PORT))
print("[+] Connected")
while(True):
  rawcot = sock_ssl.recv()
  cot = xmltodict.parse(rawcot)
  detail = cot['event']['detail']
  
  time = cot['event']['@time']
  callsign = detail['contact']['@callsign']
  group = detail['__group']['@name']
  role = detail['__group']['@role']
  coords = cot['event']['point']

  log = '{} | {} | {} | {} | {} | {}'.format(time, callsign, group, role, coords['@lat'], coords['@lon'])
  print(log)


# Connect MariaBD
# Creates tables in MariaDB

# Connect TAKY Server
# when new CoT
  # if CoT is location data for user
  # store in MariaDB table
  # Update last seen table