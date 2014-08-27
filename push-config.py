#!/usr/bin/env python

import pexpect, sys, serial, fdpexpect, os

# change these.
console_server_ip = "10.0.0.1"
# relies on ssh keys.
console_username = "user"

ips = []
for i in range(2,32):
  ips.append("10.0.0." + str(i))
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

s.sendline("")

cs = (
("Switch>", "enable"),
("Switch#", "terminal length 0"),
("Switch#", "conf t"),
("Switch\(config\)#", "int Vlan 1"),
("Switch\(config-if\)", "ip address " + ip + " 255.255.255.0"),
("Switch\(config-if\)", "no shutdown"),
("Switch\(config-if\)", "exit"),
("Switch\(config\)#", "exit"),
("Switch#", "show ver"), # this gets us the System serial number
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

s.timeout = 120
s.expect("System serial number")
sn = s.readline()
sn = sn.strip()
sn = sn[2:]
print sn
c = "copy tftp://10.0.0.1/c/" + sn + " running-config"
print c
s.sendline(c)

# copy tftp://10.0.0.1/c/CAT1037ZHHV running-config 
# Destination filename

cs = (
("Destination filename", ""),
("#", ""),
("#", "conf t"),
("\(config\)#", "crypto key generate rsa general-keys modulus 2048"),
("\(config\)#", "exit"),
("#", "write mem"),
("\[OK\]", ""),
)

# XXX TODO : for the 2950's they need this instead
# crypto key generate rsa modulus 2048

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

#
# needs to be after the config is loaded
#

print
print ip

if os.path.exists(ip):
  os.remove(ip)
