#!/usr/bin/env python

import pexpect, sys

if len(sys.argv) > 1:
  port = sys.argv[1]
else:
  port = '5'

# change these.
console_server_ip = "10.0.0.1"
# relies on ssh keys.
console_username = "user"

s = pexpect.spawn('ssh ' + console_username + '@' + console_server_ip, timeout=300)
s.logfile = sys.stdout

s.expect('$')
s.sendline('pmshell')
s.expect('Connect to port > ')
s.sendline(port)

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
# ugg, escapeing [ and ] here since pexpect uses the strings as regular
# expressions? wat?
("you like to enter the initial configuration dialog", "no"),
("Press RETURN to get started!", "\n"),
("Switch>", "enable"),
("Switch#", "terminal length 0"),
("Switch#", "write erase"),
("Erasing the nvram filesystem will remove all", "c"),
("Switch#", "delete flash:vlan.dat"),
("Delete filename", ""),
("Delete flash:", ""),
("Switch#", "write mem"),
("Switch#", "show ver"),
)

for c in cs:
  if type(c) == type("str"):
    s.expect('switch:')
    s.sendline(c)
  else:
#    print "####>", c[0]
    s.expect(c[0])
    s.sendline(c[1])

print "#" * 75

res = (
("IOS (tm) [^ ]+ Software", "Version", lambda x: x[0][:-1], "IOS Version"),
("System image file is", "flash:/", lambda x: x[0][:-1], "IOS Image"),
("Model number:", "Model number:", lambda x: x[0], "Model"),
("System serial number:", "System serial number:", lambda x: x[0], "Serial"),
("Base ethernet MAC Address:", "Base ethernet MAC Address:", lambda x: x[0], "MAC"),
)

out = {}

c = 0
for l in s:
  for r in res:
    if r[0] in l:
      t = l.find(r[1]) + len(r[1])
      o = r[2](l[t:].split())
      print '*' * 20
      print r[3] + " : " + o
      out[r[3]] = o
      c += 1
  if c == len(res):
    break

print "#" * 75

for k in out:
  print k + " : " + out[k]

