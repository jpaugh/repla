#!/usr/bin/env python
import os, sys, time

import pexpect
from pexpect import EOF, TIMEOUT

def spawn():
  return pexpect.spawn('python repla.py', timeout=3)

def output(s, end='\n', *morestr):
  if morestr:
    print >>sys.stderr, s, ' '.join(s) + end,
  else:
    print >>sys.stderr, s + end,


def print_failure():
  output('<<patterns>>')
  output(repr(repla.searcher._searches))
  output('<<buffer>>')
  output(repla.buffer[-100:])
  output('<<before>>')
  output(repla.before[-100:])

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
    ( 'exit too many args', '%exit 1 2', 'Expected one arg'),
    ( 'pwd builtin', '%pwd', os.path.realpath(os.curdir)),
    ( 'pwd too many args', '%pwd arg', 'No arguments expected'),
    ( 'cd builtin', '%cd ..\n%pwd', os.path.dirname(os.path.realpath(os.curdir))),
    ( 'cd too many args', '%cd this other', 'Expected one arg'),
    ( 'cd too few args', '%cd', 'Expected one arg'),

  )

repla = spawn()

#Give Python time to start up
time.sleep(1)

for name,send,expect in strings:
  output(name + '...', end='')
  if send is CTRL_C:
    repla.sendintr()
  elif send is CTRL_D:
    repla.sendeof()
  else:
    repla.sendline(send)

  try:
    repla.expect(expect)
    output('ok')
  except EOF as e:
    output('FAIL')
    print_failure()
  except TIMEOUT as e:
    output('FAIL')
    print_failure()
  finally:
    if expect == EOF:
      repla = spawn()
