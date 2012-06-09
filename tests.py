#!/usr/bin/env python
import re
import os
import sys
import time

import pexpect
from pexpect import EOF, TIMEOUT

sys.path.insert(0, os.curdir)
import repla  #Allow introspection

def run_tests():
  output(time.strftime('Tests run at %T %Z %D'))
  output('')

  tests_passed = 0
  tests_failed = 0

  proc = spawn()
  time.sleep(1)	    #Give Python time to start up

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
      print_failure(proc)
    except TIMEOUT as e:
      output('FAIL')
      print_failure(proc)
    finally:
      if expect == EOF:
	proc = spawn()

def spawn():
  return pexpect.spawn('python repla.py', timeout=3)

def output(s, end='\n', *morestr):
  if morestr:
    print >>sys.stderr, s, ' '.join(s) + end,
  else:
    print >>sys.stderr, s + end,

def print_failure(proc):
  output('<<patterns>>')
  for patt in proc.searcher._searches:
    output(str(patt[0])+ ' '+ repr(patt[1].pattern))
  output('<<buffer>>')
  output(proc.buffer[-100:])
  output('<<before>>')
  output(proc.before[-100:])
  output('')


def re_escape(s):
  '''escape any re metachars'''
  re_meta = re.compile(r'([].^$*+?{}[|()])')
  return re_meta.sub(r'\\\1', s)

def test_ckopt(opt):
  '''generate test cases for an option'''
  val = re_escape(repr(repla.options[opt]))
  d = { 'opt': opt, 'val': val }
  return (  'check %(opt)s option' % d,
	    '%%set %(opt)s' % d,
	    '%(opt)s = %(val)s' % d)

def test_setopt(opt, val='foo'):
  val_r = re_escape(repr(val))
  d = { 'opt': opt, 'val': repr(val), 'val_r': val_r }
  return (  'set %(opt)s option' % d,
	    '%%set %(opt)s=%(val)s\n%%set %(opt)s' % d,
	    '%(opt)s = %(val_r)s' % d )

CTRL_C = 1
CTRL_D = 2

prompt = repla.options['PS1']
testdir = os.path.realpath(os.curdir)

strings = (
    # description, send, expect
    ( 'sanity', CTRL_C, prompt % repla.options),
    ( 'basic command', '--version', 'git version'),
    ( 'unknown builtin fun', '%thisnotacommand', 'repla.py: Unknown command: '),
    ( 'exit builtin', '%exit', EOF ),
    ( 'exit noninteger', '%exit noninteger', 'exit: Expected integer'),
    ( 'exit too many args', '%exit 1 2', repla.onearg),
    ( 'pwd builtin', '%pwd', testdir),
    ( 'pwd too many args', '%pwd arg', repla.noargs),
    ( 'cd builtin', '%cd ..\n%pwd', os.path.dirname(testdir)),
    ( 'cd too many args', '%cd this other', repla.onearg),
    ( 'cd too few args', '%cd', repla.onearg),
    ( 'set builtin', '%set', r'\w+ = \S+(, \w+ = \S+)*'),
    ( 'check unknown option', '%set figgily', repla.unknownopt % 'figgily'),
    ( 'set unknown option', '%set figgily=2', repla.unknownopt % 'figgily'),
    test_ckopt('wrapped'),
    test_setopt('wrapped', val='gitk'),
    test_ckopt('PS1'),
    test_setopt('PS1', '%(wrapped)s$ '),
    ( 'shell command', '!echo success', 'success'),
  )

run_tests()
