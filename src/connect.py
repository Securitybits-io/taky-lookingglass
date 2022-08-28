#!/usr/bin/env python3

import os
import socket
import pymysql
import ssl
import xmltodict
import certutil
import logging

from time import sleep
from datetime import datetime
from queue import Queue
from threading import Thread

cert_pass = os.getenv("CERT_PASS", default="atakatak")
IP = os.getenv("IP")
PORT = os.getenv("PORT", default=8089)

SQLROOTUSER = "root"
SQLROOTPASS = os.getenv("MYSQL_ROOT_PASSWORD")

SQLHOST = os.getenv("MYSQL_HOST")
SQLUSER = os.getenv("MYSQL_USER")
SQLPASS = os.getenv("MYSQL_PASSWORD")
SQLDB   = "TAKYCoT"

SCRT = certutil.CERT_PATH + "/server.crt"
CCRT = certutil.BOT_CERT_PATH + "/taky-connect.crt"
CKEY = certutil.BOT_CERT_PATH + "/taky-connect.key"

LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO").upper()


def getCOT(socket, queue):
  logging.info('[+] Producer Thread started, waiting on CoTs...')

  while(True):
    rawcot = socket.recv()
    logging.debug("Raw Socket CoT: %s", rawcot)
    
    cot = checkCOT(rawcot)
    logging.debug("Raw Valid CoT: %s", cot)

    if cot != False:
      parsed_cot = parse_cot(cot)
      queue.put(parsed_cot)
    
def checkCOT(cot):
  for start in range(0, len(cot)):
    if cot[start:start+6] == "<event":
      for end in range(start, len(cot)):
        if cot[end:end+8] == "</event>":
          return cot[start:end+8]
  return False

def sql_configure(conn):
  cursor = conn.cursor()
  
  logging.info('[+] Create CoTs table if not exists...')
  cursor.execute('CREATE TABLE IF NOT EXISTS cots (cot_id INT AUTO_INCREMENT PRIMARY KEY, time DATETIME NOT NULL, callsign VARCHAR(24), cot_group VARCHAR(10), role VARCHAR(16), lat DOUBLE, lon DOUBLE);')
  conn.commit()
  
  logging.info('[+] Create Grafana Read-Only User if not exist...')
  cursor.execute('GRANT SELECT ON TAKYCoT.* to "grafana" IDENTIFIED BY "9AUZaNACtnc2TFcDups8euUy";')
  conn.commit()

  cursor.execute('FLUSH PRIVILEGES;')
  conn.commit()
  return


def postCOT(sql, queue):
  logging.info('[+] Consumer Thread started, waiting on queued CoTs...')
  sql_insert = "INSERT INTO `cots` (`time`, `callsign`, `cot_group`, `role`, `lat`, `lon`) VALUES (%s, %s, %s, %s, %s, %s)"

  cursor = sql.cursor()
  while (True):
    if queue.empty():
      sleep(5)
    else:
      try:
        row = queue.get()
        cot = parse_cot(row)

        logging.debug("Raw CoT: %s", row)
        logging.debug("Parsed CoT: %s", cot)

        cursor.execute(sql_insert, (cot['time'], cot['callsign'], cot['tak_color'], cot['tak_role'], cot['lat'], cot['lon']))
        sql.commit()
      except UnboundLocalError as e:
        logging.error("msg: %s", e)
      except:
        logging.error('Something went wrong')
        logging.error('Raw Cot: %s', row)
        logging.error('Parsed Cot: %s', cot)
      sleep(0.5)
      

def parse_cot(rawcot):
  dict_cot = xmltodict.parse(rawcot)
  logging.debug(dict_cot)
  
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
    logging.debug("Formatted CoT: %s", log)
  return cot


def main():
  logging.basicConfig(format='%(levelname)s:%(threadName)s:%(message)s', level=LOG_LEVEL)

  queue = Queue()
  certutil.build_certs(cert_pass)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock_ssl = ssl.wrap_socket(sock, ca_certs=SCRT, cert_reqs=ssl.CERT_NONE, certfile=CCRT, keyfile=CKEY)
  conn = sock_ssl.connect((IP, PORT))
  if (sock_ssl._connected == True):
    logging.info("[+] Connected to TAKY")
    producer = Thread(target=getCOT, args=(sock_ssl, queue))
    producer.start()

  sql_root = pymysql.connect(host=SQLHOST, user=SQLROOTUSER, password=SQLROOTPASS, db=SQLDB, cursorclass=pymysql.cursors.DictCursor)
  if sql_root.open:
    sql_configure(sql_root)
    sql_root.close()

  sql = pymysql.connect(host=SQLHOST, user=SQLUSER, password=SQLPASS, db=SQLDB, cursorclass=pymysql.cursors.DictCursor) 
  if sql.open:
    consumer = Thread(target=postCOT, args=(sql, queue))
    consumer.start()

if __name__ == '__main__':
  main()