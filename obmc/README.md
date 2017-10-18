# Tools for OpenBMC #


## Error log Interaction ##

`errl.py -i <ip> -u <user> [-p <password> | -c <cache>]`

The `errl.py` tool will connect over REST to a BMC and collect all the event logs
You then get the option to display the details.  By adding the `-c <dir>` you get
to cache the data so the next time you run the command it will skip the https
traffic and use a local copy.  The cache option will collect from the REST source
correctly if the file didn't exist yet.  If you want to erase the cached data simply
delete all the files that start with the ip address in the directory pointed to
by the -c option.  If you do not add the password in the cli the script will
prompt you

Note: A future add would be to parse the ESEL rather then just a hexdump.
The ESEL follows the loPAPR format as described in chapter 8
http://openpowerfoundation.org/?resource_lib=linux-on-power-architecture-platform-reference


## LED Interaction ##

	`leds.py -i <ip> -u <user> [-p <password> | -c <cache>]`

Displays a menu to toggle LED groups on/off
