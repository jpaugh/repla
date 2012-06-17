
from repla.command import CmdBase

class test_cmd(CmdBase):
  def cmdTest(self, args):
    self.show('Hi!')

  def cmdHello(self, args):
    self.show('Hello, world!')
