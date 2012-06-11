#!/usr/bin/env python
'''Copyright 2012 Jonathan Paugh. Please see LICENSE for details.'''

import re
import os
import sys
import time

import pexpect
from pexpect import EOF, TIMEOUT

sys.path.insert(0, os.curdir)
import repla  #Allow introspection

def run_tests():
  output('Running %s tests' % len(strings), end='')
  output(time.strftime(' at %T %Z %D'))
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
      tests_passed += 1
    except EOF as e:
      output('FAIL')
      print_failure(proc)
      tests_failed += 1
    except TIMEOUT as e:
      output('FAIL')
      print_failure(proc)
      tests_failed += 1
    finally:
      if expect == EOF:
	proc = spawn()

  output('')
  output('Passed %s/%s' % (tests_passed, len(strings)))
  if tests_failed != 0:
    output('Failed %s!' % tests_failed)

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
  output(repr(proc.buffer[-100:]))
  output('<<before>>')
  output(repr(proc.before[-100:]))
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

def test_setopt(opt, mesg=None, val='foo'):
  val_r = re_escape(repr(val))
  d = { 'opt': opt, 'val': repr(val), 'val_r': val_r }
  if not mesg:
    mesg = 'set %(opt)s option' % d
  return (  mesg,
	    '%%set %(opt)s=%(val)s\n%%set %(opt)s' % d,
	    '%(opt)s = %(val_r)s' % d )

CTRL_C = 1
CTRL_D = 2

prompt = repla.options['PS1']
testdir = os.path.realpath(os.curdir)

strings = (
    # description, send, expect
    ( 'sanity', CTRL_C, prompt % repla.options),
    ( 'Ctrl+D EOF', CTRL_D, EOF),
    ( 'basic command', '--version', 'git version'),
    ( 'unknown builtin fun', '%thisnotacommand', 'repla.py: Unknown command: '),
    ( 'exit builtin', '%exit', EOF ),
    ( 'exit noninteger', '%exit noninteger', repla.expectedint),
    ( 'exit too many args', '%exit 1 2', repla.manyargs),
    ( 'pwd builtin', '%pwd', testdir),
    ( 'pwd too many args', '%pwd arg', repla.noargs),
    ( 'cd builtin', '%cd ..\n%pwd', os.path.dirname(testdir)),
    ( 'cd too many args', '%cd this other', repla.onearg),
    ( 'cd too few args', '%cd', repla.onearg),
    ( 'dimen builtin', '%dimen', 'rows:.*cols:'),
    ( 'dimen too many args', '%dimen 1 2', repla.manyargs),
    ( 'dimen noninteger', '%dimen two', repla.expectedint),
    ( 'set builtin', '%set', r'\w+ = \S+(, \w+ = \S+)*'),
    ( 'check unknown option', '%set figgily', repla.unknownopt % 'figgily'),
    ( 'set unknown option', '%set figgily=2', repla.unknownopt % 'figgily'),
    test_ckopt('wrapped'),
    test_setopt('wrapped', val='gitk'),
    test_ckopt('PS1'),
    test_setopt('PS1', '%(wrapped)s$ '),
    test_ckopt('prefix'),
    test_setopt('prefix'),
    test_ckopt('postfix'),
    test_setopt('postfix'),
    test_setopt('prefix', val='--this=that', mesg='set option with embedded "="'),
    ( 'shell command', '!echo success', 'success'),
    ( 'line continuation', '!echo broken \\\nline', 'broken line'),
    ( 'reset to known state', '%exit', EOF ),
    ( 'empty line regression', '', prompt % repla.options),
  )

run_tests()
