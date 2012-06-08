#!/usr/bin/env python
import sys, time

import pexpect
from pexpect import EOF, TIMEOUT

repla = pexpect.spawn('python repla.py', timeout=3)

CTRL_C = 1
CTRL_D = 2

prompt = '\r\n\\$'

strings = (
    ( 'sanity', CTRL_C, prompt),
    ( 'basic command', '--version', 'git version'),
  )

#Give Python time to start up
time.sleep(1)

for name,send,expect in strings:
  print >>sys.stderr, name, '...',
  if send is CTRL_C:
    repla.sendintr()
  elif send is CTRL_D:
    repla.sendeof()
  else:
    repla.sendline(send)

  try:
    repla.expect(expect)
    print >>sys.stderr, 'ok'
  except EOF, TIMEOUT:
    print >>sys.stderr, 'FAIL'
    raise
