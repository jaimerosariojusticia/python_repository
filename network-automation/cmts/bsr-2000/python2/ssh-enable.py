#!/usr/bin/env python
#
#===========================================================================#
# Import modules
#===========================================================================#
import subprocess
import sys
import telnetlib
import time
import getpass

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
#
if GetCMTSVendor.__contains__("BSR") == True:
    tn = telnetlib.Telnet(host)
#
#===========================================================================#
# Login
#===========================================================================#
    tn.read_until("Password: ")
    tn.write(password + "\n")
    tn.read_until(">")
    tn.write("en \n")
    tn.read_until("Password: ")
    tn.write(password + "\n")

#===========================================================================#
# Commands
#===========================================================================#
    tn.read_until("#")
    tn.write("page off\n")
    tn.write("ssh-keygen2 bits 1024 type rsa \n")
    time.sleep(2)
    tn.read_until("#")
    tn.write("config \n")
    tn.write("username root privilege rw \n")
    tn.write("username root password " + password + "\n")
    tn.write("ssh password-authentication radius local-password \n")
    tn.write("service password-encryption \n")
    tn.write("ssh enable \n")
    tn.write("exit \n")
    tn.write("copy running-config startup-config \n")
    print("SSH enabled. Saving configuration...")
    time.sleep(2)
    tn.close()
    print("SSH configuration completed.")
    exit()