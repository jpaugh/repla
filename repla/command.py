from util import *

class CmdBase(object):
  errcode = 0
  curcmd = None

  parent = None
  __children = []

  def __init__(self):
    self.parent = self
    #Initially, each object is at the top of a command hierarchy,
    #but addChild changes the child's parent to be the added-to object

  def __getattr__(self, attr):
    if self.__class__ == self.parent.__class__:
      #Called from top level object; check first child
      if len(self.__children) == 0:
	return None
      index = 0
    else:
      index = self.__findNext()
    child = self.__children[index]

    return getattr(child, attr, None)

  def __findNext(self):
    #Find the index of the next child after this one
    dx = None
    for i,c in enumerate(self.__children):
      if c == self:
	dx = i
	break

    if not dx:
      raise Exception("%s: Cannot find child: %s" % (self.__class__, self))

    dx += 1
    if dx == len(self.__children):
      return None #This is the last child; there is no next index
    return dx

  def addChild(self, child):
    if not isinstance(child, self.__class__):
      raise Exception("%s cannot be added; is not a subclass of %s" %
	  (child, self.__class__))
    self.__children.append(child)
    child.parent = self

  def cmdfail(self, *msg):
    warn(self.parent.curcmd+':', *msg)
    self.parent.errcode = 1

  def show(self, *msg):
    show(*msg)

