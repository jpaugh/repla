#!/usr/bin/env python
import sys
import shlex
import subprocess
import readline

def main():
  while True:
    try:
      cmd = get_cmd()
      run_cmd(cmd)
    except KeyboardInterrupt:
      print

def run_cmd(cmd):
  '''Run the command with args as its arglist. Returns the command's
  returncode.
  '''
  cmd.insert(0, 'git')
  return sub(cmd)

def sub(cmd):
  '''run a command'''
  #NOTE: May fail with OSError
  child = subprocess.Popen(cmd)
  return child.wait()

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

if __name__ == '__main__':
  try:
    main()
  except EOFError:
    print '', #Add newline iff needed
    sys.exit(0)
