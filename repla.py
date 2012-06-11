#!/usr/bin/env python
'''Copyright 2012 Jonathan Paugh. Please see LICENSE for details.'''

import os
import sys
import shlex
import subprocess
import readline

def main():
  print fmt_title(),
  while True:
    try:
      cmd = get_cmd()
      how_do_cmd(cmd)
    except KeyboardInterrupt:
      print

def how_do_cmd(cmd):
  '''Figure out how to run a cmd'''
  if not cmd:
    return
  if isinstance(cmd, basestring):
    if cmd[0] == '!':
      run_shcmd(cmd)
  elif cmd[0][0] == '%':
    run_cmdfun(cmd)
  else:
    run_cmd(cmd)

def run_cmd(cmd):
  '''Run the command with args as its arglist. Returns the command's
  returncode.
  '''
  cmd.insert(0, options['wrapped'])
  return sub(cmd)

def run_cmdfun(cmd):
  '''invoke a command function. These functions follow the following
  protocol:

  - method of CmdFun class
  - accepts two parameters: self, arglist
  - given the command name is foo, the method name is cmdFoo
  '''
  name = cmd.pop(0)[1:]
  cmdObj.curcmd = name
  cmdObj.errcode = 0

  funname = 'cmd' + name.title()
  fun = getattr(cmdObj, funname, None)
  if fun is not None:
    fun(cmd)
  else:
    fail('Unknown command: ' + cmdObj.curcmd)

def run_shcmd(cmd):
  cmd = cmd[1:]
  sub(cmd, shell=True)

def sub(cmd, **kwargs):
  '''run a command'''
  #NOTE: May fail with OSError
  child = subprocess.Popen(cmd, **kwargs)
  return child.wait()

class Cmd(object):
  errcode = 0
  curcmd = None

  def cmdCd(self, args):
    if len(args) == 1:
      os.chdir(args[0])
    else:
      cmdfail(onearg)

  def cmdDimen(self, args):
    if len(args) > 1:
      cmdfail(manyargs)
      return
    elif args:
      try:
	fd = int(args[0])
      except ValueError:
	cmdfail(expectedint)
	return
    else:
      fd = 0
    show('rows: %d cols: %d' % term_dimen(fd))

  def cmdExit(self, args):
    retcode = 0
    if len(args) > 1:
      cmdfail(manyargs)
      return
    if args:
      try:
	retcode = int(args[0])
      except ValueError:
	cmdfail(expectedint)
	return
    sys.exit(retcode)

  def cmdPwd(self, args):
    if not args:
      show(os.path.realpath('.'))
    else:
      cmdfail(noargs)

  def cmdSet(self, args):
    if not args:
      show(fmt_dict(options))
    else:
      for word in args:
	if '=' in word:
	  key, val = word.split('=')
	  if key in options:
	    options[key] = val
	    if key == 'title':
	      print fmt_title(),
	  else:
	    cmdfail(unknownopt % key)
	else:
	  if word in options:
	    show('%s = %s' % (word, repr(options[word])))
	  else:
	    cmdfail(unknownopt % word)

cmdObj = Cmd()

option_meta = [
    { 'name': 'wrapped',
      'doc': 'program to pass each command line to',
      'default': 'git',
      },
    { 'name': 'prefix',
      'doc' : 'string prepended to each line before sending it to wrapped command',
      'default': '',
      },
    { 'name': 'postfix',
      'doc' : 'string appended to each line before sending it to wrapped command',
      'default': '',
      },
    { 'name': 'PS1',
      'doc' : 'primary prompt. Use %(name)s to insert option name as a string into the prompt string.',
      'default': '%(wrapped)s: ',
      },
    { 'name': 'PS2',
      'doc' : 'secondary prompt. Use %(name)s to insert option name as a string into the prompt string.',
      'default': '. ',
      },
    { 'name': 'title',
      'doc' : 'Sets the title sent to the terminal. Use same format as for PS1',
      'default': '%(wrapped)s',
      }
  ]

options = {}

for opt in option_meta:
  options[opt['name']] = opt['default']


# UI Functions
##############

def get_cmd(prompt=None):
  '''prompt the user for a cmd, and return a shlex of their input'''
  line = None
  while not line:
    line = get_line(prompt)
  while line[-1] == '\\':
    line = line[:-1] + get_line(format_opt_str('PS2'))
  if line[0] == '!':  #Return sh commands as is
    return line
  if line[0] != '%':
    line = ' '.join((options['prefix'], line, options['postfix']))
  return shlex.split(line)

def get_line(prompt=None):
  '''prompt the user for a line'''
  if prompt is None:
    prompt = format_opt_str('PS1')
  return raw_input(prompt)

def fmt_title():
  return '\033k%s\033\\' % format_opt_str('title')

def format_opt_str(opt):
  '''Several options allow Pythonic formatting; this function catches
  formatting errors in such to avoid crashing.
  '''
  try:
    return options[opt] % options
  except:
    return options[opt]

def fmt_dict(d):
  fmts = []
  for key in d:
    fmts.append('%s = %s' % (key, repr(d[key])))

  return fmt_list(fmts)

def fmt_list(l):
  from math import ceil
  scr_w = term_width()
  col_w = 0
  col_padding = '  '
  row_padding = '\n'
  for val in l:
    if len(val) > col_w:
      col_w = len(val)
  cols = scr_w/col_w + len(col_padding)
  rows = int(ceil(float(len(l)) / cols))
  lp = []
  try:
    for r in xrange(rows):
      row = []
      lp.append(row)
      for c in xrange(cols):
	row.append(l[r+c*rows].ljust(col_w))
  except IndexError:
    #Not enough elems to fill last row; oh well.
    pass
  lp = [ col_padding.join(x) for x in lp ]
  return row_padding.join(lp)

def term_height():
  return term_dimen()[0]

def term_width():
  return term_dimen()[1]

def term_dimen(fd=0):
  import termios
  import fcntl
  import struct
  h,w = (25,80)

  '''See man pages tty_ioctl(4) and termios(3) for details
  Note that '_'*4 is a synonym for struct.pack('hhhh', 0,0,0,0) for the
  purposes of fcntl.ioctl. We only need to retreive the first two
  values, however, as the other two have only historic use.
  '''
  try:
    dense = fcntl.ioctl(0, termios.TIOCGWINSZ, '_'*4)
    h,w = struct.unpack('hh', dense)
  except IOError:
    pass
  return h,w

def fail(*msg):
  errcode = 1
  warn(sys.argv[0]+':', *msg)

def cmdfail(*msg):
  warn(cmdObj.curcmd+':', *msg)
  errcode = 1

def warn(*msg):
  msg = ' '.join(msg)
  print >>sys.stderr, msg

def show(*msg):
  msg = ' '.join(msg)
  print msg


# Strings
##########

#NOTE: Please use these to keep user messages uniform

noargs = 'No arguments expected'
expectedargs = 'Expected %d args'
expectedint = 'Expected integer'
onearg = 'Expected one arg'
manyargs = 'Too many args'
fewargs = 'Too few args'
unknownopt = 'Unknown option: %s'

if __name__ == '__main__':
  try:
    main()
  except EOFError:
    print '', #Add newline iff needed
    sys.exit(0)
