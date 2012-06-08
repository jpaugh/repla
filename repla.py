#!/usr/bin/env python
import os
import sys
import shlex
import subprocess
import readline

def main():
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
  elif cmd[0][0] == '%':
    run_cmdfun(cmd)
  else:
    run_cmd(cmd)

def run_cmd(cmd):
  '''Run the command with args as its arglist. Returns the command's
  returncode.
  '''
  cmd.insert(0, 'git')
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

def sub(cmd):
  '''run a command'''
  #NOTE: May fail with OSError
  child = subprocess.Popen(cmd)
  return child.wait()

class Cmd(object):
  errcode = 0
  curcmd = None

  def cmdCd(self, args):
    if len(args) == 1:
      os.chdir(args[0])
    else:
      cmdfail(onearg)

  def cmdExit(self, args):
    retcode = 0
    if len(args) > 1:
      cmdfail(onearg)
      return
    if args:
      try:
	retcode = int(args[0])
      except ValueError:
	cmdfail('Expected integer')
	return
    sys.exit(retcode)

  def cmdPwd(self, args):
    if not args:
      show(os.path.realpath('.'))
    else:
      cmdfail(noargs)

cmdObj = Cmd()


# UI Functions
##############

def get_cmd(prompt=None):
  '''prompt the user for a cmd, and return a shlex of their input'''
  cmd = shlex.split(get_line(prompt))
  return cmd

def get_line(prompt=None):
  '''prompt the user for a line'''
  if prompt is None:
    prompt = fmt_ps1()
  return raw_input(prompt)

def fmt_ps1():
  '''return a formatted prompt'''
  #TODO: real ps1 handling
  return '$ '

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
onearg = 'Expected one arg'

if __name__ == '__main__':
  try:
    main()
  except EOFError:
    print '', #Add newline iff needed
    sys.exit(0)
