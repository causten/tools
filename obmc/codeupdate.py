#!/usr/bin/python
#################################################################################
# * "THE BEER-WARE LICENSE" (Revision 42):
# * <austenc@us.ibm.com> wrote this file.  As long as you retain this notice you
# * can do whatever you want with this stuff. If we meet some day, and you think
# * this stuff is worth it, you can buy me a beer in return.   Chris Austen
#################################################################################
import sys
import getpass
import getopt
import obmcrequests
import paramiko
from scp import SCPClient
import time


def chassis_power_off(e):

	e.post('/org/openbmc/control/chassis0/action/getPowerState', [])
	msg = e.data()

	if msg == 1:
		print 'Chassis powered on, will power off'
		e.post('/org/openbmc/control/chassis0/action/powerOff', [])

	while msg == 1:
		time.sleep(2)
		e.post('/org/openbmc/control/chassis0/action/getPowerState', [])
		msg = e.data()
		print 'Power State now: ', msg


def scp_file(ip, uname, pswd, image):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.load_system_host_keys()
	ssh.connect(ip, username=uname, password=pswd)
	scp = SCPClient(ssh.get_transport())
	scp.put(image, '/tmp/flashimg')

def code_update_bios(ip, uname, pswd, image):

	print 'Copying bios ' + image + ' to remote system'
	scp_file(ip, uname, pswd, image)

	print 'Establishing REST connection'

	e  = obmcrequests.obmcConnection(ip, uname, pswd)

	chassis_power_off(e)

	e.post('/org/openbmc/control/flash/bios/action/update', ['/tmp/biosflashimg'])
	e.get('/org/openbmc/control/flash/bios/attr/status')
	msg = e.data()

	print 'BMC indicates ' + msg


def code_update_bmc(ip, uname, pswd, image):

	print 'Copying ' + image + ' to remote system'
	scp_file(ip, uname, pswd, image)

	e  = obmcrequests.obmcConnection(ip, uname, pswd)
	e.put('/org/openbmc/control/flash/bmc/attr/preserve_network_settings', 1)
	e.post('/org/openbmc/control/flash/bmc/action/update', ['/tmp/flashimg'])
	e.get('/org/openbmc/control/flash/bmc/attr/status')
	msg = e.data()

	if 'Update Success' in msg:
		e.post('/org/openbmc/control/bmc0/action/warmReset', [])
	else:
		print 'Error: '+ msg




def usage():
	name = 'codeupdate.py'
	print 'Usage: Version 0.2'  
	print name, '(command)-i <ip> -u <username> -t <[bmc|bios]>  <-p> <-c dir> -f <file>'
	print '\t-i | --ip=        : IP / Hostname of the target BMC'
	print '\t-u | --user=      : user name for REST interaction'
	print '\t-p | --password=  : password for REST interaction'
	print '\t-t | --target=    : bmc | bios'
	print '\t-f | --file=      : image to be flashed'

def main(argv):

	pswd 	= ''
	ip 		= ''
	uname 	= ''
	target = ''

	try:
		opts, args = getopt.getopt(argv,"hc:d:u:p:i:t:f:",["target=", "ip=","user=","password=","file="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-i", "--ip"):
			ip = arg
		elif opt in ("-u", "--user"):
			uname = arg
		elif opt in ("-p", "--password"):
			pswd = arg
		elif opt in ("-t", "--target"):
			target = arg
		elif opt in ("-f", "--file"):
			image = arg

	if target == '':
		usage()
		print 'ERROR: must define what you are flashing [bmc|bios]'
		sys.exit(2)

	if image == '':
		usage()
		print 'ERROR: missing a image file to flash'
		sys.exit(2)

	if ip == '' or uname == '':
		usage()
		print 'ERROR: ip and user parmeters are required'
		sys.exit(2)

	if pswd == '':
		pswd = getpass.getpass('Password:')


	if target == 'bmc':
		code_update_bmc(ip, uname, pswd, image)

	elif target == 'bios':
		code_update_bios(ip, uname, pswd, image)

	else:
		usage()
		print 'Image target of ' + target + ' is not supported'

if __name__ == "__main__":
   main(sys.argv[1:])
