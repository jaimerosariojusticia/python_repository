#!/usr/bin/env python3
#=============================================#
import subprocess
import telnetlib
import time
import credentials

#=============================================#
# Set variables
#=============================================#
# ROUTER = b'flash0:/vios-adventerprisek9-m'
# SWITCH = b'flash0:/vios_l2-adventerprisek9-m'

#=============================================#

USERID = credentials.ssh_local_id()
SSHKEYSTRING = credentials.ssh_local_keystring()
SSHKEYHASH = credentials.ssh_local_keyhash()

#
GETPORTS = subprocess.check_output('sudo netstat -tupanl | grep -P "(?=.*python)(?=.*LISTEN)(?=.*0.0.0.0:50[\\00-30])" | column -tx | cut -d " " -f7 | sort -V', shell=True).decode()
output = GETPORTS

# If ip address list (with ports) included in text file 'inventory', use this instead
#f = open("inventory", "rt")
#output = f.read()

HOST = '127.0.0.1'
SWITCH = False

for line in output.split():
    #HOST = line.split(':')[0]
    PORT = line.split(':')[1]

#=============================================#
# Initiate telnet session
#=============================================#
    tn = telnetlib.Telnet(HOST, PORT)

#=============================================#
# Configuration
#=============================================#
    tn.write(b'\r\n\r\n\r\n')
    tn.write(b'show version | include flash0' + '\n'.encode('ascii'))
    if tn.read_until(b"9-m").__contains__(b"vios_l2"):
        SWITCH = True
        tn.read_until(b">"); tn.write(b'terminal length 0' + '\n'.encode('ascii'))
        tn.read_until(b">"); tn.write(b'enable' + '\n'.encode('ascii'))
        tn.read_until(b"#"); tn.write(b'del /force flash:vlan.dat' + '\n'.encode('ascii'))
        tn.read_until(b"#"); tn.write(b'del /force nvram:vlan.dat' + '\n'.encode('ascii'))
        tn.read_until(b"#"); tn.write(b'wr erase' + '\n'.encode('ascii'))
        tn.read_until(b"[confirm]"); tn.write('\n'.encode('ascii'))

    tn.read_until(b"#"); tn.write(b'terminal length 0' + '\n'.encode('ascii'))
    tn.read_until(b"#"); tn.write(b'config terminal' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'username cisco privilege 15 password C!$C01234' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'service password-encryption' + '\n'.encode('ascii'))
    #
    tn.read_until(b"(config)#"); tn.write(b'banner exec ^ ^' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'banner incoming ^ ^' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'banner login ^ ^' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'banner motd ^ ^' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'no cdp run' + '\n'.encode('ascii'))
    #
    tn.read_until(b"(config)#"); tn.write(b'no ip domain lookup' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'ip domain name GNS3.LAB' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'crypto key zero' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'crypto key generate rsa general-keys modulus 2048 label Default' + '\n'.encode('ascii'))
    time.sleep(5)
    tn.read_until(b"(config)#"); tn.write(b'ip ssh version 2' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'ip ssh dh min size 2048' + '\n'.encode('ascii'))
    #
    # Public Key Chain
    tn.read_until(b"(config)#"); tn.write(b'ip ssh pubkey-chain' + '\n'.encode('ascii'))
    tn.read_until(b"(conf-ssh-pubkey)#"); tn.write(b'username ' + str(USERID).encode('ascii') + '\n'.encode('ascii'))
    # --- key-hash ---
    #tn.read_until(b"(conf-ssh-pubkey-user)#"); tn.write(b'key-hash ssh-rsa ' + str(SSHKEYHASH).encode('ascii') + '\n'.encode('ascii'))
    #tn.read_until(b"(conf-ssh-pubkey-user)#"); tn.write(b'exit' + '\n'.encode('ascii'))
    # --- key-string --- (.ssh/id_rsa.pub)
    tn.read_until(b"(conf-ssh-pubkey-user)#"); tn.write(b'key-string' + '\n'.encode('ascii'))
    tn.read_until(b"(conf-ssh-pubkey-data)#"); tn.write(b'' + str(SSHKEYSTRING).encode('ascii') + '\n'.encode('ascii'))
    tn.read_until(b"(conf-ssh-pubkey-data)#"); tn.write(b'exit' + '\n'.encode('ascii'))
    tn.read_until(b"(conf-ssh-pubkey-user)#"); tn.write(b'exit' + '\n'.encode('ascii'))
    # -------------------------------------
    tn.read_until(b"(conf-ssh-pubkey)#"); tn.write(b'exit' + '\n'.encode('ascii'))
    #
    tn.read_until(b"(config)#"); tn.write(b'line console 0' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b' exec-timeout 0 0' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b' privilege level 15' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b' logging synchronous' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b' login local' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)"); tn.write(b'exit' + '\n'.encode('ascii'))
    #
    tn.read_until(b"(config)#"); tn.write(b'line vty 0 4' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b' logging synchronous' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b' login local' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b' transport input ssh telnet' + '\n'.encode('ascii'))
    tn.read_until(b"(config-line)#"); tn.write(b'exit' + '\n'.encode('ascii'))
    tn.read_until(b"(config)#"); tn.write(b'end' + '\n'.encode('ascii'))
    #
    tn.read_until(b"#"); tn.write(b'wr memory' + '\n'.encode('ascii'))
    tn.read_until(b"#"); tn.write(b'\r\n\r\n\r\n')
    tn.read_until(b"#"); tn.write(b'reload' + '\n'.encode('ascii'))
    tn.read_until(b"[confirm]"); time.sleep(5); tn.write('\n'.encode('ascii'))
### exit
    print (tn.read_all)
    tn.close()