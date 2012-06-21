
from common import *
import tipes

#class InconsistenConstraint(Exception):
#  def __init__(self, c):
#    self.c = c

class Closure(Typish):
  def __init__(self, subscribers = []):
    self.constraints = set()
    self.subscribers = subscribers
  def __str__(self):
    return ", ".join(map(str, self.constraints))
  def ftv(self):
    ftvs = set()
    for c in self.constraints:
      ftvs |= c.ftv()
    return ftvs
  def apply(self, sub):
    clsr = Closure()
    clsr.constraints = [c.apply(sub) for c in self.constraints]
    return clsr

  def setCurrentTerm(term):
    self.currentTerm = term

  # return all type variables y such that x <: y or y <: x
  def comparable(self, x):
    over  = [c.right for c in self.constraints if c.left == x and c.right.isVar() ]
    under = [c.left for c in self.constraints if c.right == x and c.left.isVar()]
    return over + under

  def upper(self, t):
    return {c.right for c in self.constraints if c.left == t and not c.right.isVar()} 

  def lower(self, t):
    return {c.left for c in self.constraints if c.right == t and not c.left.isVar()}
  #  ls = {c.left for c in self.constraints if c.right == t and not c.left.isVar()}
  #  tvs = set()
  #  for l in ls:
  #    tvs |= l.ftv()
  #      # Substitution
  #  sub = tipes.Substitution({tv:self.lower(tv) for tv in tvs})
  #  return {sub(l) for l in ls}

  def addMany(self, cs):
    for c in cs:
      self.add(c)
    return self
  def add(self, c,):
    if c in self.constraints:
      return self
    # add constraint and all derived constraints to the clsoure.
    # since this is the only way to modify the constraints, this maintains
    # the closure property
    decompositives = c.decompose()
    if decompositives:
      #print("DEBUG: decompositives")
      self.addMany(decompositives)
      #self.constraints.add(c)
    else:
      transitives = c.transitive(self.constraints)
      if not c.consistent():
        print("inconsistent constraint: {0}".format(c))
        for sub in self.subscribers:
          sub.inconsistent(c) 
        #raise InconsistentConstraint(c)
      self.constraints.add(c)
      self.addMany(transitives)
    return self
    
  def __or__(self, other):
    c = Closure()
    c.constraints = self.constraints
    c.addMany(other.constraints)
    return c
  def __add__(self, c):
    self.add(c)
    return self

#  def solve(self, gen, debug):
#    sub = Substitution({})
#    while not all([isinstance(c, CSubtype) for c in self.constraints]):
#      if debug:
#        print("constraints")
#        for x in self.constraints:
#          print("  {0}".format(x))
#        input("wait") 
#      c = self.constraints.pop(0) 
#      if debug:
#        print("current constraint is {0}".format(c))
#      s, newCs = c.solve(self.constraints, gen)
#      sub = sub >> s
#      self.constraints = [c.apply(s) for c in newCs]
#    return sub

    #print("solving constraint {0}".format(c))
    #print("{0}:[{1}]".format(c, ", ".join([str(x) for x in constraints])))
    
#    constraints = [ constraints[i + 1] for i in range(len(constraints) - 1)]
    #print("active Vars = {0}".format(activeVars))
    #print(s)
    #print("after append: [{0}]".format(", ".join([str(x) for x in constraints])))
    #input("before application of sub: {0}".format(s))
    #input("wait")



class Constraint:
  # solve returns a substitution, and new constraints to add to the end of the constraints
  def solve(self, activeVars, gen):
    raise Exception("not implemented")
  def apply(self, sub):  
    raise Exception("not implemented")
  def activeVars(self):
    return self.left.ftv() | self.right.ftv()
  def ftv(self):
    return self.left.ftv() | self.right.ftv()

  def decompose(self):
    return {}
  def transitive(self, cs):
    return {}

  #def canDecompose(self):
  #  return isinstance(self.left, TFun) and isinstance(self.right, TFun)

class CArity2(Constraint):
  def __init__(self, left, right, op, con):
    self.left = left
    self.right = right
    self.op = op
    self.con = con
  def apply(self, sub):
    return self.con(self.left.apply(sub), self.right.apply(sub))
  def __str__(self):
    return "{0} {1} {2}".format(self.left, self.op, self.right) 
  def solve(self, activeVars, gen):
    return Substitution({}), [self]
    #raise Exception("not implemented")


# the only constraint
class CSubtype(CArity2):
  def __init__(self, l, r):
    CArity2.__init__(self,  l, r, "<:", CSubtype)
  def decompose(self):
    if self.left.sameType(self.right):
      return self.left.decompose(self.right) 
    elif self.left.isPrim and self.right.isField:
      if self.right.name in self.left.fields:
        return {self.left.fields[self.right.name] < self.right.t}
    return set()

  def transitive(self, cs):
    ncs = set()
    if self.right.isVar():
      ncs |= {self.left < c.right for c in cs if c.left == self.right}
    if self.left.isVar():
      ncs |= {c.left < self.right for c in cs if c.right == self.left}
    return ncs
  def consistent(self):
    return True if self.left.isVar() or self.right.isVar() else type(self.left) == type(self.right)
  def solve(self, cs, gen):
    return Substitution({}), cs + [self] 
#    if isinstance(self.right, TVar):
#      newCs = []
#      flag = False
#      for c in cs:
#        if isinstance(c.right, TVar) and c.right.name == self.right.name:
#          newCs.append(CEqual(c.left, self.left))
#          newCs.append(self)
#          flag = True
#        else: 
#          newCs.append(c)
#      if flag:  
#        return Substitution({}), newCs
#      else:
#        return Substitution({self.right.name:self.left}), newCs
#    else:
#      print("ONLY primitive subtype solving so far!")
#      return Substitution({}), cs + [self]
#      #if isinstance(self.right)
 
  def __eq__(self, other):
    return self.left == other.left and self.right == other.right if type(other) == type(self) else False
  def __hash__(self):
    return hash(self.left) ^ hash(self.right)

def activeVars(cs):
  actives = set()
  for c in cs:
    actives |= c.activeVars()
  return actives
#  return reduce(lambda x, y: x | y, [ x.activeVars() for x in cs], set())
 

