import sys

def show(*msg):
  msg = ' '.join(msg)
  print msg

def warn(*msg):
  msg = ' '.join(msg)
  print >>sys.stderr, msg
