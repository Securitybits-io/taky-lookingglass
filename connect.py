#!/usr/bin/env python3

import os
import socket
import certutil
import ssl


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
while(True):
  print(sock_ssl.recv())

sock_ssl.close()