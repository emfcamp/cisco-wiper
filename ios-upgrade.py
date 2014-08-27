#!/usr/bin/env python

import pexpect, sys, serial, fdpexpect, os

# change these.
console_server_ip = "10.0.0.1"
# relies on ssh keys.
console_username = "user"
ips = ("10.0.0.2", "10.0.0.3", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7")
tftp_server_ip = "10.0.0.1"

if len(sys.argv) > 1:
  port = sys.argv[1]
else:
  port = '5'

if 'dev' in port:
  print "serial port"
  sp = serial.Serial(port=port)
  s = fdpexpect.fdspawn(sp.fd, timeout=300)
  s.logfile = sys.stdout
else:
  s = pexpect.spawn('ssh '+ console_username + '@' + console_server_ip, timeout=300)
  s.logfile = sys.stdout
  s.expect('$')
  s.sendline('pmshell')
  s.expect('Connect to port > ')
  s.sendline(port)

ip = None

for t in ips:
  if not os.path.exists(t):
    os.system("touch " + t)
    ip = t
    break

if ip == None:
  print "no spare IP?!?!"
  exit()

cs = (
'flash_init', 
'load_helper',
'delete flash:private-config.text',
("(y/n)?", 'y'),
'delete flash:config.text',
("(y/n)?", 'y'),
'delete flash:vlan.dat',
("(y/n)?", 'y'),
'boot',

#Would you like to terminate autoinstall? [yes]: 
# enter
#         Would you like to enter the initial configuration dialog? [yes/no]: 
# no
# Switch>
         
("Press RETURN to get started", ""),
(".*", ""),
#("LINEPROTO-5-UPDOWN", ""),
#("LINEPROTO-5-UPDOWN", ""),
#("changed state to up", ""),
("Would you like to terminate autoinstall", ""),
("Would you like to enter the initial configuration dialog", "no"),
("Switch>", "enable"),
("Switch#", "terminal length 0"),
("Switch#", "write erase"),
("Erasing the nvram filesystem will remove all", "c"),
("Switch#", "delete flash:vlan.dat"),
("Delete filename", ""),
("Delete flash:", ""),
# just incase
("Switch#", "dir flash:"),
("Switch#", "delete /recursive /force flash:c3560-advipservicesk9-mz.122-25.SEE2"),
("Delete filename", ""),
#("Switch#", "write mem"),
("Switch#", "conf t"),
("Switch\(config\)#", "int Vlan 1"),
("Switch\(config-if\)", "ip address " + ip + " 255.255.255.0"),
("Switch\(config-if\)", "no shutdown"),
("Switch\(config-if\)", "exit"),
("Switch\(config\)#", "exit"),
# delete recursivly 
("Switch#", "copy tftp://" + tftp_server_ip +  "/c3560-ipservicesk9-mz.122-55.SE9.bin flash:"),
("Destination filename", ""),
#("Address or name of remote host", ""),
("OK - ", ""),
("Switch#", "conf t"),
("Switch\(config\)#", "boot system flash:c3560-ipservicesk9-mz.122-55.SE9.bin"),
("Switch\(config\)#", "exit"),
("Switch#", "show boot"),
#("Switch#", "write mem"),
("Switch#", "verify flash:c3560-ipservicesk9-mz.122-55.SE9.bin"),
("Verified", ""),

("Switch#", "reload"),
("System configuration has been modified", "no"),
("Proceed with reload", ""),
("Press RETURN to get started", "\n \n"),
(".*", ""),
("LINEPROTO-5-UPDOWN", ""),
(".*", ""),
("Would you like to", "no"),
("Switch>", "enable"),
("Switch#", "terminal length 0"),

("Switch#", "conf t"),
("Switch\(config\)#", "int Vlan 1"),
("Switch\(config-if\)", "ip address " + ip + " 255.255.255.0"),
("Switch\(config-if\)", "no shutdown"),
("Switch\(config-if\)", "exit"),
("Switch\(config\)#", "exit"),

("Switch#", "show ver"), # this gets us the System serial number

# copy tftp://10.0.0.1/c/CAT1037ZHHV running-config 
# Destination filename

)

# write mem
# reload (?)

for c in cs:
  if type(c) == type("str"):
    s.expect('switch:')
    s.sendline(c)
  else:
    again = True
    while again:
      try:
        print "*" * 20, 
        print c[0]
        s.expect(c[0])
        s.sendline(c[1])
        again = False
      except pexpect.EOF:
        print "EOF?"
        pass

print "#" * 75

print ip
os.remove(ip)
print

res = (
("Cisco IOS Software", "Version", lambda x: x[0][:-1], "IOS Version"),
("System image file is", "flash:", lambda x: x[0][:-1], "IOS Image"),
("Base ethernet MAC Address", "Base ethernet MAC Address:", lambda x: x[0], "MAC"),
("Model number", "Model number", lambda x: x[0], "Model"),
("System serial number", "System serial number", lambda x: x[0], "Serial"),
)

out = {}

s.timeout = 5

for r in res:
  try:
    print r
    while True:
      l = s.readline()
#      print l
      if r[0] in l:
        print "### found" + r[0]
        t = l.find(r[1]) + len(r[1])
        o = r[2](l[t:].split())
        print '*' * 20
        print r[3] + " : " + o
        out[r[3]] = o
        break
  except pexpect.TIMEOUT:
    # some ios versions are a bit different etc...
    pass
  except pexpect.EOF:
    # some ios versions are a bit different etc...
    pass

print "#" * 75

for k in out:
  print k + " : " + out[k]

s.timeout = 120
s.expect("Switch#")
print out["Serial"]
print "copy tftp://10.0.0.1/c/" + out["Serial"] + " running-config"

# config ip again

# copy tftp://10.0.0.1/c/CAT1037ZHHV running-config 
# Destination filename

#
# needs to be after the config is loaded
#
#("Switch#", "conf t"),
#("Switch\(config\)#", "crypto key generate rsa general-keys modulus 2048"),
#("Switch\(config\)#", "exit"),

#s.sendline("reload")
print
print ip

if os.path.exists(ip):
  os.remove(ip)



