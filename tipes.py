from common import *

from constraints import *

class Type(Typish):
  isPrim = False
  isField = False
  isVar = False
  def sameType(self, other):
    return type(self) == type(other)
  def isVar(self):
    return False
  def bind(self, s, gen):
    if s.name in self.ftv():
      raise TypeError("occurs check failed")
    else:
    #return Substitution({s:self.apply(Substitution({s:TInf()}))})
      return Substitution({s.name:self})

  def __lshift__(self, other):
    return CSubtype(self, other)

  def instantiate(self):
    raise Exception("not implemented")
 
  def __eq__(self, other):
    raise Exception("not implemented")

  def normalize(self):
    vars = self.ftv()
    gen = VarGen()
    s = Substitution({v:gen.fresh() for v in vars})
    return self.apply(s)
  def generalize(self, env):
    raise Exception("wtf this should't be called")
    return TScheme(self.ftv() - env.ftv(), self)
  def generalize2(self, cs, env): 
    return TScheme2((self.ftv() | cs.ftv()) - env.ftv(), cs, self)

#     TScheme :: TScheme [(String | Int)] Type
#class TScheme(Type):
#  def __init__(self, vars, t):
#    if not isinstance(t, Type):
#      raise Exception("Attempting to initiate type scheme with non type term: {0}".format(type(t)))
#    if not all([isVarType(var) for var in vars]):
#      raise Exception("Attempting to quantify with non variables")
#    self.vars = set(vars)
#    self.type = t
#    #print("SCHEME created:{0}".format(self))
#  def instantiate(self, gen):
#    print("DEBUG: attempting to instantiate STYLE # 1!!: {0}".format(self))
#    s = Substitution({v:gen.fresh() for v in self.vars})
#    return self.type.apply(s)
#  def __str__(self):
#    return "for all {0}. {1}".format(", ".join(map(str,self.vars)), str(self.type))
#  def ftv(self):
#    return self.type.ftv() - self.vars
#  def apply(self, sub):
#    return TScheme(self.vars, self.type.apply(sub))
#  def __eq__(self, other):
#    return self.vars == other.vars and self.type == other.type if type(self) == type(other) else False
#
#class TScheme2(Type):
#  def __init__(self, vars, cs, t):
#    if not isinstance(t, Type):
#      raise Exception("Attempting to initiate type scheme with non type term: {0}".format(type(t)))
#    if not all([isVarType(var) for var in vars]):
#      raise Exception("Attempting to quantify with non variables")
#    self.vars = set(vars)
#    self.cs = cs
#    self.type = t
#    #print("SCHEME created:{0}".format(self))
#  def instantiate(self, gen):
#    print("DEBUG: attempting to instantiate STYLE # 2!!: {0}".format(self))
#    s = Substitution({v:gen.fresh() for v in self.vars})
#    return self.type.apply(s), self.cs.apply(s)
#  def __str__(self):
#    f = lambda xs: ", ".join(map(str,xs))
#    return "for all {0}. {1} => {2}".format(f(self.vars), self.cs, self.type)
#  def ftv(self):
#    return (self.type.ftv() | self.cs.ftv()) - self.vars
#  def apply(self, sub):
#    return TScheme2(self.vars, self.cs.apply(sub),self.type.apply(sub))
#  def __eq__(self, other):
#    return self.vars == other.vars and self.type == other.type if type(self) == type(other) else False

class TUnit(Type):
  def ftv(self):
    return set()
  def apply(self, sub):
    return self
  def decompose(self, other):
    return set()
  def __str__(self):
    return "*"
  def __eq__(self, other):
    return type(self) == type(other)
  def __hash__(self):
    return hash(str(self)) 

class TNple(Type):
  def __init__(self, types):
    self.types = types
  def sameType(self, other):
    return type(self) == type(other) and len(self.types) == len(other.types)
  def ftv(self):
    return set()
  def apply(self, sub):
    return TNple([t.apply(sub) for t in self.types])
  def decompose(self, other):
    return {x << y for x, y in zip(self.types, other.types)}
  def __str__(self):
    return "({0})".format(", ".join([str(t) for t in self.types])) 
  def __eq__(self, other):
    return self.sameType(other) and all([x == y for x, y in zip(self.types, other.types)])
  def __hash__(self):
    return hash(str(self)) 

 

class TField(Type):
  isField = True
  def __init__(self, name, t):
    self.name = name
    self.t = t
#  def sameType(self, other):
#    return type(self) == type(other) and self.name == other.name
  def ftv(self):
    return self.t.ftv()
  def apply(self, sub):
    return TField(self.name, self.t.apply(sub))
  def decompose(self, other):
    return {CSubtype(self.t, other.t)} if self.name == other.name else set()
  def __str__(self):
    return "{0}:{1}".format(self.name, self.t)
  def __eq__(self, other):
    return self.name == other.name and self.t == other.t if type(self) == type(other) else False
  def __hash__(self):
    return hash(self.name) ^ hash(self.t) 

class TVar(Type):
  def __init__(self, var):
    if not isVarType(var):
      raise Exception("must initiate variable with valid identifier type")
    self.name = var
  def isVar(self):
    return True
  def decompose(self, other):
    return set()
  def ftv(self):
    return {self.name}
  def apply(self, subs):
    return subs[self.name] if self.name in subs else self
  def bind(self, s, gen):
    return Substitution({}) if self.name == s else Substitution({s.name:self})
  def __str__(self):
    return "t{0}".format(self.name) if isinstance(self.name, int) else self.name
  def __eq__(self, other):
    return self.name == other.name if type(self) == type(other) else False
  def __hash__(self):
    return self.name.__hash__()
  def __lt__(self, other):
    #print("is {0} < {1}?".format(self, other))
    return self << other in self.constraints

class TLR(Type):
  def ftv(self):
    return self.t0.ftv() | self.t1.ftv()
  def apply(self, subs):
    t0 = self.t0.apply(subs)
    t1 = self.t1.apply(subs)
    return self.con(t0, t1)
  def __str__(self):
    return "({0} {1} {2})".format(self.t0, self.mid, self.t1)
  def __eq__(self, other):
    return self.t0 == other.t0 and self.t1 == other.t1 and self.mid == other.mid if type(self) == type(other) else False
  def __hash__(self):
    return hash(self.t0) ^ hash(self.t1) ^ hash(self.mid)

#  def __eq__(self, other):
#    return self.left == other.left and self.right == other.right if type(self) == type(other) else False

class TFun(TLR):
  def __init__(self, t0, t1):
    self.t0 = t0
    self.t1 = t1
    self.mid = "->"
    self.con = TFun
  def decompose(self, other):
    return {CSubtype(other.t0, self.t0), CSubtype(self.t1, other.t1)}

class TPair(TLR):
  def __init__(self, t0, t1):
    self.t0 = t0
    self.t1 = t1
    self.mid = ","
    self.con = TPair



class TLit(Type):
  isPrim = True
  def apply(self, subs):
    return self
  def ftv(self):
    return set()
  def decompose(self, other):
    return set()
  def __eq__(self, other):
    return type(self) == type(other)
  def __hash__(self):
    return hash(str(self))


class TInt(TLit):
  def __str__(self):
    return "Int"

class TBool(TLit):
  def __str__(self):
    return "Bool"
class TNum(TLit):
  def __init__(self):
    self.fields = dict()
    self.fields["__add__"] = TFun(TNple([self]), self)
    self.fields["__sub__"] = TFun(TNple([self]), self)
    self.fields["__mul__"] = TFun(TNple([self]), self)
    self.fields["__eq__"] = TFun(TNple([self]), TBool())
  def __str__(self):
    return "Num"
class TStr(TLit):
  def __init__(self):
    self.fields = dict()
    self.fields["__add__"] = TFun(TNple([self]), self)
    self.fields["__mul__"] = TFun(TNple([TNum()]), self)
    self.fields["__eq__"] = TFun(TNple([self]), TBool())
  def __str__(self):
    return "String"

class SetOfTypes(Type, set):
  def apply(self, sub):
    raise Exception("You're Crazy")
    return SetOfTypes([t.apply(sub) for t in self])
  def ftv(self):
    return self


class VarGen:
  def __init__(self, var = 0):
    self.var = var
  def freshInt(self):
    t = self.var
    self.var += 1
    return t
  def fresh(self):
    return TVar(self.freshInt())
  def freshRec(self):
    return Rec(self.freshInt())

class Substitution(dict):
  def __init__(self, d):
    if not all([isVarType(v) for v in d.keys()]):
      raise Exception("all vars in substituion must be valid var types.")
#    if not all([isinstance(t, Type) for t in d.values()]):
       
    for t in d.values():
      if not isinstance(t, Type):
        raise Exception("all types in substition must be valid types: {0}".format(t))
    for k, v in d.items():
      self[k] = v

  def map(self, f):
    for k, v in self.items():
      x[k] = f(v)
  # subsitution composition
  def compose(left, right):
    # apply the right subs to each val of the left
    x = Substitution({k:t.apply(right) for k, t in left.items()})
    # merge the right into the left
    x.update(right)
    return x
  def __rshift__(self, other):
     return self.compose(other)
  def __str__(self):
    words = ["{0}/{1}".format(TVar(x), y) for x, y in self.items()]
    inside = ", ".join(words)
    return "[{0}]".format(inside)

  def __call__(self, t):
    return t.apply(self)

