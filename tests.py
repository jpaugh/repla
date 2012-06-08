#!/usr/bin/env python
import os, sys, time

import pexpect
from pexpect import EOF, TIMEOUT

sys.path.insert(0, os.curdir)
import repla  #Allow introspection

def spawn():
  return pexpect.spawn('python repla.py', timeout=3)

def output(s, end='\n', *morestr):
  if morestr:
    print >>sys.stderr, s, ' '.join(s) + end,
  else:
    print >>sys.stderr, s + end,

def print_failure():
  output('<<patterns>>')
  output(repr(proc.searcher._searches))
  output('<<buffer>>')
  output(proc.buffer[-100:])
  output('<<before>>')
  output(proc.before[-100:])

CTRL_C = 1
CTRL_D = 2

prompt = '\r\n\\$'
testdir = os.path.realpath(os.curdir)

strings = (
    ( 'sanity', CTRL_C, prompt),
    ( 'basic command', '--version', 'git version'),
    ( 'unknown command fun', '%thisnotacommand', 'repla.py: Unknown command: '),
    ( 'exit builtin', '%exit', EOF ),
    ( 'exit noninteger', '%exit noninteger', 'exit: Expected integer'),
    ( 'exit too many args', '%exit 1 2', repla.onearg),
    ( 'pwd builtin', '%pwd', testdir),
    ( 'pwd too many args', '%pwd arg', repla.noargs),
    ( 'cd builtin', '%cd ..\n%pwd', os.path.dirname(testdir)),
    ( 'cd too many args', '%cd this other', repla.onearg),
    ( 'cd too few args', '%cd', repla.onearg),
  )

proc = spawn()

#Give Python time to start up
time.sleep(1)

for name,send,expect in strings:
  output(name + '...', end='')
  if send is CTRL_C:
    proc.sendintr()
  elif send is CTRL_D:
    proc.sendeof()
  else:
    proc.sendline(send)

  try:
    proc.expect(expect)
    output('ok')
  except EOF as e:
    output('FAIL')
    print_failure()
  except TIMEOUT as e:
    output('FAIL')
    print_failure()
  finally:
    if expect == EOF:
      proc = spawn()
