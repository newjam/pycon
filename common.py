def isVarType(var):
  return isinstance(var, str) or isinstance(var, int) or isinstance(var, Rec)

class Typish:
  def ftv(self):
    raise Exception("not implemented")
  def apply(self, subs):
    raise Exception("not implemented")

# mapping from variables that appear in expressions to type schemes
class Environment(Typish):
  def __init__(self, gen):
    self.gen = gen
    self.m = dict()
  def __getitem__(self, t):
    if t in self.m:
      return self.m[t]
    else:
      self.m[t] = self.gen.fresh()
      return self.m[t]
  def __delitem__(self, t):
    if t in self.m:
      del self.m[t]
  def keys(self):
    return self.m.keys()
  def copy(self):
    n = Environment(self.gen)
    n.m = self.m.copy()
    return n
  def ftv(self):
    return reduce( lambda x, y: x|y , [t.ftv() for t in self.values()], set([]))
  def apply(self, sub):
    return Environment([(v, t.apply(sub)) for v, t in self.items()])
  def __str__(self):
    words = ["{0}:{1}".format(x, y) for x, y in self.m.items()]
    inside = ", ".join(words)
    return "[{0}]".format(inside)

from common import *

class Typish:
  def ftv(self):
    raise Exception("not implemented")
  def apply(self, subs):
    raise Exception("not implemented")



