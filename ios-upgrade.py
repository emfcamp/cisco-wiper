#!/usr/bin/env python

import pexpect, sys, serial, fdpexpect, os

# change these.
console_server_ip = "10.0.0.1"
# relies on ssh keys.
console_username = "user"
ips = ("10.0.0.2", "10.0.0.3", "10.0.0.3", "10.0.0.5",)
tftp_server_ip = "10.0.0.10"

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
("Press RETURN to get started", "\r"),
(".*", "\r"),
("LINEPROTO-5-UPDOWN", "\r"),
("changed state to up", "\n"),
("Switch>", "enable"),
("Switch#", "terminal length 0"),
("Switch#", "write erase"),
("Erasing the nvram filesystem will remove all", "c"),
("Switch#", "delete flash:vlan.dat"),
("Delete filename", ""),
("Delete flash:", ""),
("Switch#", "write mem"),
("Switch#", "conf t"),
("Switch\(config\)#", "int Vlan 1"),
("Switch\(config-if\)", "ip address " + ip + " 255.255.255.0"),
("Switch\(config-if\)", "no shutdown"),
("Switch\(config-if\)", "exit"),
("Switch\(config\)#", "exit"),
("Switch#", "copy tftp://" + tftp_server_ip +  "/c2950-i6k2l2q4-mz.121-22.EA14.bin flash:"),
("Destination filename", ""),
#("Address or name of remote host", ""),
("OK - ", ""),
("Switch#", "conf t"),
("Switch\(config\)#", "boot system flash:c2950-i6k2l2q4-mz.121-22.EA14.bin"),
("Switch\(config\)#", "exit"),
#("Switch#", "write mem"),
("Switch#", "show boot"),
("Switch#", "reload"),
("System configuration has been modified", "no"),
("Proceed with reload", ""),
("Press RETURN to get started", "\n \n"),
(".*", ""),
("LINEPROTO-5-UPDOWN", ""),
("Switch>", "enable"),
("Switch#", "terminal length 0"),
("Switch#", "show ver"),
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
("IOS (tm) ", "Version", lambda x: x[0][:-1], "IOS Version"),
("System image file is", "flash:", lambda x: x[0][:-1], "IOS Image"),
("Base ethernet MAC Address:", "Base ethernet MAC Address:", lambda x: x[0], "MAC"),
("Model number:", "Model number:", lambda x: x[0], "Model"),
("System serial number:", "System serial number:", lambda x: x[0], "Serial"),
)

out = {}

s.timeout = 10

for r in res:
  try:
    print r
    while True:
      l = s.readline()
#      print l
      if r[0] in l:
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
#s.sendline("reload")
print
print ip
if os.path.exists(ip):
  os.remove(ip)
