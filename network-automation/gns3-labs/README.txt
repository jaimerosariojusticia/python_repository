This is a python script that uses telnet to configure IOSv devices in GNS3.

There's a lot on this going on, but I'll keep working on documenting this.

This only works with a dedicated GNS3 Linux server.
It may work on the GNS3 VMWare/VBox images, but I don't have the hardware and the IOSv images
to properly debug this. This is a work in progress.

This script simply follows a previous old version I used to configure old Cisco routers and switches.


What this script does is it adds to the initial configuration, your SSH public key
into either the L2 or Router IOSv image.

You need to edit 'credentials.py' and change "iamgroot" to your host userid
and the ssh public key string.

You can get the right format by running:


	cat ~/.ssh/id_rsa.pub | cut -d ' ' -f2 | fold -b -w100


Yeah, yeah, useless use of cat. I know. I don't care.
Copy and paste between the comment (''') in credentials.py


In ios-telnet-config.py, it uses subprocess to get the list of ports used in GNS3.
Keep in mind, this is a Linux GNS3 server dedicated for GNS3 and GNS3 only.
It will scan for ports from 5000 through 5030 ( that's what 50[\\00-30] is for).

If a non-cisco device is using any port within the range, the script will not work.


	sudo netstat -tupanl | grep -P "(?=.*python)(?=.*LISTEN)(?=.*0.0.0.0:50[\\00-30])" | column -tx | cut -d " " -f7 | sort -V


Then, run it with python3:

python3 ios-telnet-config.py