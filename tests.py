#!/usr/bin/env python
import sys, time

import pexpect
from pexpect import EOF, TIMEOUT

def spawn():
  return pexpect.spawn('python repla.py', timeout=3)

repla = spawn

CTRL_C = 1
CTRL_D = 2

prompt = '\r\n\\$'

strings = (
    ( 'sanity', CTRL_C, prompt),
    ( 'basic command', '--version', 'git version'),
    ( 'unknown command fun', '%thisnotacommand', 'repla.py: Unknown command: '),
    ( 'exit builtin', '%exit', EOF ),
    ( 'exit noninteger', '%exit noninteger', 'exit: Expected integer'),
    ( 'exit too many args', '%exit 1 2', 'Expected 1 args'),
  )

repla = spawn()

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
  except EOF as e:
    print >>sys.stderr, 'FAIL'
    print >>sys.stderr, e
  except TIMEOUT as e:
    print >>sys.stderr, 'FAIL'
    print >>sys.stderr, e
  finally:
    if expect == EOF:
      repla = spawn()
