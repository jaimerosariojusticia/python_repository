#!/usr/bin/env python

#===========================================================================#
# Import modules
#===========================================================================#
import paramiko
import subprocess
import sys
import time
import getpass

#===========================================================================#
# 'import Crypto.Cipher.AES' to fix the output error using paramiko:
#
#   /usr/lib/python2.7/dist-packages/Crypto/Cipher/blockalgo.py:141: \
# FutureWarning: CTR mode needs counter parameter, not IV
#       self._cipher = factory.new(key, *args, **kwargs)
#===========================================================================#
import Crypto.Cipher.AES
orig_new = Crypto.Cipher.AES.new
def fixed_AES_new(key, *ls):
    if Crypto.Cipher.AES.MODE_CTR == ls[0]:
        ls = list(ls)
        ls[1] = ''
    return orig_new(key, *ls)

#===========================================================================#
# Set the host to 'cmts' by default if no host given in the CLI
#===========================================================================#
host = 'cmts'
if len(sys.argv) >= 2:
  host = sys.argv[1]

#===========================================================================#
# Set the default credentials for CMTS
#===========================================================================#
username = 'root'
password = getpass.getpass("Enter password: ")

#===========================================================================#
# Try SNMP string to identify CMTS vendor
#===========================================================================#
SNMPCOMM = 'private'

GetCMTSVendor = subprocess.check_output('timeout 1 echo "$(snmpwalk -t1 -v 2c -c ' + SNMPCOMM + ' ' + host + ' SNMPv2-MIB::sysDescr.0 | cut -d " " -f4-5)"', shell=True)

if GetCMTSVendor.__contains__("BSR") == False:
    exit()

#===========================================================================#
# SSH Client connection to CMTS
#===========================================================================#
remote_conn_pre=paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

Crypto.Cipher.AES.new = fixed_AES_new   # See the Crypto.Cipher.AES notes about this

remote_conn_pre.connect(
    host,
    port=22,
    username=username,
    password=password,
    look_for_keys=False,
    allow_agent=False
    )

#===========================================================================#
# Initiate BSR SSH connnection
#===========================================================================#
remote_conn = remote_conn_pre.invoke_shell()

#===========================================================================#
# This will not output the login process
#===========================================================================#
remote_conn.send("enable" + "\n" + password + "\n" + "page off" + "\n")

time.sleep(1)
if remote_conn.recv_ready():
    output = remote_conn.recv(65535)

#===============================================================#
#   Define and run common DOCSIS CMTS Command(s):
#===============================================================#
COMMAND = 'show running-config'
remote_conn.send(COMMAND + "\n")

#===============================================================#
#   Output
#===============================================================#
time.sleep(3)
output = remote_conn.recv(65535)
output = output.replace('bsr#','').replace(COMMAND,'')

print (output.strip())
remote_conn.close()
exit()