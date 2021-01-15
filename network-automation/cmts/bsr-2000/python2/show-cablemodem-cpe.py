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
COMMAND = 'show cable modem cpe'
remote_conn.send(COMMAND + "\n")

#===============================================================#
time.sleep(3)
output = remote_conn.recv(65535)
output = output.replace(COMMAND,'').replace('bsr#','').strip()
output = output.replace('Cable  ','Cable__').replace('CM ', 'CM_').replace('CPE ', 'CPE_').replace(' ',';')
for num in range(0, 9):
    output = output.replace(';' + str(num) + '\n\r',';' + str(num) + ';')
output = output.replace('CPE_IP\n\r','CPE_IP;').replace('Count\n\r','Count;')
for num in range(9, 1, -1):
    output = output.replace(';' * num,';')
output = output.replace('CPE_MAC;CPE_IP;','').replace('Interface;PSID;CM_MAC;CM_IP;CPE_Count;Cable__0/0/','')
output = output.replace('\n\r\n\r','\n\r').replace(';\n\r',';').replace(';D0/','\n\rD0/')
output = output.upper()
#
SPC = ' '
#
print (
    'Interface  PSID    CM_MAC' + SPC * 14 + 'CM_IP' + SPC * 11 +
    'CPE   CPE_MAC1' + SPC * 12 + 'CPE_IP1' + SPC * 11 +
    'CPE_MAC2' + SPC * 12 + 'CPE_IP2' + SPC * 11 +
    'CPE_MAC3' + SPC * 12 + 'CPE_IP3' + SPC * 11
    )
print ('-' * 172)
#
for line in output.split():
    line = line.strip()
    element = line.split(';')
#
    INTERFACE = element[0]
    PSID = element[1]
    CM_MAC = convertmac.mac2colon(element[2])
    CM_IP = element[3]
    CPEC = element[4]
    CPECOUNT = (int(CPEC))
#
    if CPECOUNT == 0:
        CPE_MAC1 = [' ' * 13]; CPE_IP1 = [' ' * 11]
        CPE_MAC2 = [' ' * 13]; CPE_IP2 = [' ' * 11]
        CPE_MAC3 = [' ' * 13]; CPE_IP3 = [' ' * 11]
    elif CPECOUNT == 1:
        CPE_MAC1 = convertmac.mac2colon(element[5]); CPE_IP1 = element[6]
        CPE_MAC2 = [' ' * 13]; CPE_IP2 = [' ' * 11]
        CPE_MAC3 = [' ' * 13]; CPE_IP3 = [' ' * 11]
    elif CPECOUNT == 2:
        CPE_MAC1 = convertmac.mac2colon(element[5]); CPE_IP1 = element[6]
        CPE_MAC2 = convertmac.mac2colon(element[7]); CPE_IP2 = element[8]
        CPE_MAC3 = [' ' * 13]; CPE_IP3 = [' ' * 11]
    elif CPECOUNT == 3:
        CPE_MAC1 = convertmac.mac2colon(element[5]); CPE_IP1 = element[6]
        CPE_MAC2 = convertmac.mac2colon(element[7]); CPE_IP2 = element[8]
        CPE_MAC3 = convertmac.mac2colon(element[9]); CPE_IP3 = element[10]
#
    OUTPUT = (
        str(INTERFACE),
        str('{:<{}}'.format(PSID, 5)),
        str('{:<{}}'.format(CM_MAC, 15)), str('{:<{}}'.format(CM_IP, 15)),
        str('{:<{}}'.format(CPEC, 1)),
        str('{:<{}}'.format(CPE_MAC1, 15)), str('{:<{}}'.format(CPE_IP1, 15)),
        str('{:<{}}'.format(CPE_MAC2, 15)), str('{:<{}}'.format(CPE_IP2, 15)),
        str('{:<{}}'.format(CPE_MAC3, 15)), str('{:<{}}'.format(CPE_IP3, 15)),
        )
#   
    print (str(OUTPUT).replace('(','').replace(')','').replace('"[','').replace(']"','').replace("', '",' ' * 3).replace("'",''))
#
remote_conn.close()