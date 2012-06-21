from ast import *
from tipes import *
from common import *

import sys
import json


# TODO need some way to trace back to the origin of the type error
# for instnace, instead of only reporting  where the types were defined,
# also report where the types were used in a type unsafe way. 


#import argparse

class TypeZero(NodeVisitor):
  def generic_visit(self, node):
    node.type = TUnit() 
    NodeVisitor.generic_visit(self, node)



#class PrintTypes(NodeVisitor):
#  def generic_visit(self, node):
#    print node.

# how to deal with container types and iterators?
#
# for x in xs
#
# generates the constraints:
#
# [xs] <: __iter__:() -> a
# a <: __next__:() -> b
# b <: [x]
#
# if [xs] was a list of Num,
#
# __iter__:()->list_iterator <: __iter__:()->a
# => list_iterator <: a
# __next__:()->Num <: list_iterator
# => () -> Num <: __next__:() -> b
# => Num <: b
#
# polymorphism would be needed to make lists useful, otherwise all lists 
# would have the same type of elements.
#
# Q: how do we introduce polymorphism into a contraint based system?
# A: by quantifying over the constraints generated for a polymorphic expression
#    with the form 'forall a. t \ C' where a is a type variable set, t is a 
#    type, and C is a constraints set
#
#    eg. 'f = lambda x: x.l * 2' might generate 
#    forall [x], a . [x] -> a \ {[x] <: __mul__: Num -> a} <: [f] 
#    using f as in 'f(2)' would generate 
#    
#

class PrettyPrinter(NodeVisitor):
  def __init__(self, html = True):
    self.indentLevel = 0
    self.html = html
  def indent(self):
    return "  " * self.indentLevel
  def newline(self):
    return "</br>"

  def visit_Num(self, node):
    return str(node.n)
  def visit_Str(self, node):
    return "\'{0}\'".format(node.s)
  def visit_Name(self, node):
    return str(node.id)
  def visit_Attribute(self, node):
    return "{0}.{1}".format(self.visit(node.value), str(node.attr))

  def visit_FunctionDef(self, node):
    r = "def {0}({1}):{2}".format(node.name, self.visit(node.args), self.newline())
    self.indentLevel += 1
    for s in node.body:
      r += self.indent() + self.visit(s) + self.newline()
    self.indentLevel -= 1
    return r
  def visit_ClassDef(self, node):
    r = "class {0}:{1}".format(node.name, self.newline())
    self.indentLevel += 1
    for s in node.body:
      r += self.indent() + self.visit(s) + self.newline()
    self.indentLevel -= 1
    return r
  def visit_Assign(self, node):
    return "{0} = {1}".format(self.visit(node.targets[0]), self.visit(node.value))
  def visit_Return(self, node):
    return "return{0}".format( " " + self.visit(node.value) if node.value != None else "")
  def visit_If_Or_While(self, which,  node):
    r = "{0} {1}:\n".format(which, self.visit(node.test))
    self.indentLevel += 1
    for s in node.body:
      r += self.indent() + self.visit(r) + self.newline()
    r += "else :{1}{0}".format(self.visit(node.orelse), self.newline())
    self.indentLevel -= 1
    return r
  def visit_While(self, node):
    return self.visit_If_Or_While(self, "while", node)
  def visit_If(self, node):
    return self.visit_If_Or_While(self, "if", node)
  def visit_Call(self, node):
    return "{0}({1})".format(self.visit(node.func), ", ".join([self.visit(arg) for arg in node.args]))
  op2str = dict()
  op2str["Add"] = "+"
  op2str["Mult"] = "*"
  def visit_Lambda(self, node):
    return "lambda {0}: {1}".format(self.visit(node.args), self.visit(node.body))
  def visit_BinOp(self, node):
    op = self.op2str[type(node.op).__name__]
    return "({0} {1} {2})".format(self.visit(node.left), op, self.visit(node.right))  

  cmp2str = dict()
  cmp2str["Eq"] = "=="
  def visit_Compare(self, node):
    r = self.visit(node.left)
    for op, exp in zip(node.ops, node.comparators):
      op = self.cmp2str[type(op).__name__]
      r += " {0} {1}".format(op, self.visit(exp))
    return r

  def visit_arguments(self, node):
    return ", ".join([self.visit(arg) for arg in node.args])
  def visit_arg(self, node):
    return str(node.arg)#self.visit(node.arg)
  
  
  def visit_Module(self, node):
    r = ""
    for stmt in node.body:
      r += self.visit(stmt) + self.newline()
    return r

  def generic_visit(self, node):
    print("unhandled ast node: {0}".format(type(node).__name__))
    return # NodeVisitor.generic_visit(self, node)

  def visit(self, node):
    if self.html:
      return "<span title=\"{1}\" class=\"{1}\">{0}</span>".format(NodeVisitor.visit(self, node), node.type)
    else:
      return NodeVisitor.visit(self, node)

class TypeInferencer(NodeVisitor):
  def __init__(self):
    self.gen = VarGen()
    self.env = Environment(self.gen) 
    self.cons = Closure([self])

    self.errorOrigins = []
    self.nodeStack = []
    self.envStack = []
    self.nameToType = {}
  def curNode(self):
    return self.nodeStack[len(self.nodeStack) - 1]
  def beginScope(self):
    pass    
  def endScope(self):
    pass

  #
  # each term has an id
  # 
  # This allows terms to have non type variable types.
  # so 2.0 has type Num and id 5, for example.
  # 

  def visit_Num(self, node):
    a = self.gen.fresh()
    # this is a little hacky, but it helps a lot in error reporting...
    n = TNum()
    n.exp = node

    self.cons += n < a
    return a
  def visit_Str(self, node):
    a = self.gen.fresh()

    s = TStr()
    s.exp = node 

    self.cons += s < a 
    return a
  def visit_Name(self, node):
    #self.generic_visit(node)
    print("{0}:{1}".format(node.id, self.env[node.id]))
    self.nameToType[node.id] = self.env[node.id]
    #print("env in name: {0}".format(self.env))
    if hasattr(self.env, "tClass"):
      self.cons += TField(node.id, self.env[node.id]) < self.env.tClass  
    node.type = self.env[node.id]
    node.type.code = node
    return node.type
  def visit_Attribute(self, node):
    te = self.visit(node.value)
    a = self.gen.fresh()
    field = TField(node.attr, a)
    if isinstance(node.ctx, Load):
      self.cons += te < field 
    elif isinstance(node.ctx, Store):
      self.cons += field < te
    else:
      raise Exception("context not handled")
    node.type = a
    return node.type
  def visit_FunctionDef(self, node):
    env = self.env
    #print("entering def, old env: {0}".format(env))
    self.env = self.env.copy()
    del env["return"]
    a = self.visit(node.args)
    #print("modified env: {0}".format(self.env))
    for stmt in node.body:
      self.visit(stmt)
    b = self.env["return"]
    self.env = env

    t = self.env[node.name]     

    #special case if this is a function definition in a class definition.
    if hasattr(env, "tClass"):
      targs = self.cons.upper(a).pop().types #kind of hacky
      tself = targs[0]
      self.cons += env.tClass < tself
      self.cons += tself < env.tClass
      a = TNple(targs[1:])
      if node.name == "__init__":
        self.cons += TFun(a, env.tClass) < env[env.nClass]
      self.cons += TField(node.name, TFun(a, b)) < env.tClass
      #self.cons += t < env.tClass          
    else:
      self.cons += TFun(a , b) < t
    #node.type = t
    #print("newwwww env: {0}".format(self.env))
    return node.type

  def visit_ClassDef(self, node):
    t = self.gen.fresh()
    oldEnv = self.env
    self.env = oldEnv.copy()
    self.env.tClass = t
    self.env.nClass = node.name   
 
    for stmt in node.body:
      self.visit(stmt)
    
    if "__init__" in self.env.keys():
      self.cons += self.env[node.name] < oldEnv[node.name]
    else:
      self.cons += TFun(TNple([]), t) < oldEnv[node.name]
    self.env = oldEnv
    return node.type

  def visit_Return(self, node):
    if node.value != None:
      self.cons += self.visit(node.value) < self.env["return"]
    return node.type
  def visit_If(self, node): 
    return self.visit_IfOrWhile(node)
  def visit_While(self, node):
    return visit_IfOrWhile(self, node)
  def visit_IfOrWhile(self, node):
    tte = self.visit(node.test)
    for stmt in node.body + node.orelse:
      self.visit(stmt)   
    self.cons += tte < TBool()
    return node.type

  # Expressions

  op2str = dict()
  op2str["Add"] = "__add__"
  op2str["Mult"] = "__mul__"

  def visit_BinOp(self, node):
    # left 'op' right
    tl = self.visit(node.left)
    tr = self.visit(node.right)
    a = self.gen.fresh()
    try:
      methodName = self.op2str[type(node.op).__name__]
      self.cons += tl < TField(methodName, TFun(TNple([tr]), a))
    except KeyError:
      raise Exception("operation type not yet supported")
    node.type = a
    return node.type


  def visit_Compare(self, node):
    tl = self.visit(node.left)
    for op, exp in zip(node.ops, node.comparators):
      tr = self.visit(exp)
      #a = self.gen.fresh()
      if isinstance(op, Eq):
        opname = "__eq__"
      else:
        raise Exception("comparison operator not yet supported")
      self.cons += tl < TField(opname, TFun(TNple([tr]), TBool()))
      tl = tr
    node.type = TBool()
    return node.type
  # x < y == z



  def visit_Lambda(self, node):
    env = self.env
    self.env = env.copy()
    tx = self.visit(node.args)
    te = self.visit(node.body)
    a = self.gen.fresh()
    print("DEBUG: {0} -> {1} <: {2}".format(tx, te, a))
    self.cons += TFun(tx, te) < a
    self.env = env
    return a

  def visit_IfExp(self, node):
    tte = self.visit(node.test)
    self.cons += tte < TBool()
    tbe = self.visit(node.body)
    tee = self.visit(node.orelse)
    a = self.gen.fresh()
    self.cons += tbe < a
    self.cons += tee < a
    # basically a decomposition of:
    #   Bool -> a -> a -> a   <   tt -> tb ->  te -> b
    return na
  def visit_Call(self, node):
    te1 = self.visit(node.func)
    te2 = TNple([self.visit(arg) for arg in node.args])
    a = self.gen.fresh()
    self.cons += te1 < TFun(te2, a)
    return a
  def visit_arguments(self, node):
    a = self.gen.fresh()
    t = TNple([self.visit(arg) for arg in node.args])
    self.cons += a < t 
    return a
  def visit_arg(self, node):
    del self.env[node.arg]
    return self.env[node.arg]
  def visit_Assign(self, node):
    # normally assignment lets you unpack n-ples, but for now, single assignment
    te1 = self.visit(node.targets[0])
    te2 = self.visit(node.value)
    self.cons += te2 < te1
    return node.type

  def inconsistent(self, c):
    self.errorOrigins.append((self.curNode(), c))
     
  def visit(self, node):
    self.nodeStack.append(node)
    node.type = NodeVisitor.visit(self, node) or node.type
    self.nodeStack.pop()
    node.type.exp = node # oh imperative languages
    return node.type
  def generic_visit(self, node):
    print("unhandled ast node: {0}".format(type(node).__name__))
    NodeVisitor.generic_visit(self, node)
    return node.type
  #def addConstraint(self, node, c):
  #  try
  #    self.cons += c
  #  except InconsistenConstraint
  #    self.errorOrigins |= {node}

filenames = "bloop.py" if len(sys.argv) < 2 else sys.argv[1:]

for filename in filenames:
  file = open(filename)
  ast = parse(file.read())
  TypeZero().visit(ast)

  plainPrinter = PrettyPrinter(html = False)
  pp = PrettyPrinter(html = True)
  
  ti = TypeInferencer()
  ti.visit(ast)
  cs = ti.cons

  print(cs) 
 
  p = lambda n: plainPrinter.visit(n)
  
  for origin, c in ti.errorOrigins:
    print("""error origin: {0}
    {1} <: {2}""".format(p(origin), p(c.left.exp), p(c.right.exp) ))
  
  f = open(filename+".html", "w")
  print("writing to file {0}".format(f))
  f.write("<html><head>")
  f.write("""<style type=\"text/css\">
    .error.focus { background-color:IndianRed; }
    .error.comparable { background-color:IndianRed; }
    .error { background-color:Red; }
    .inconsistent { background-color:Orange; }
    .focus { background-color:LawnGreen; }
    .comparable { background-color:LimeGreen; }
  </style>""")
  f.write("<script type=\"text/javascript\" src=\"https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js\"></script>")
  
  t2cmp = dict()
  ftvs = cs.ftv()
  
  for ftv in ftvs:
    #print(json.dumps([str(v) for v in cs.comparable(TVar(ftv))]))
    ftv = TVar(ftv)
    t2cmp[str(ftv)] = [str(t) for t in cs.comparable(ftv)]
  
  f.write("<script type=\"text/javascript\">")	
  f.write("m = ")
  f.write(json.dumps(t2cmp))
  f.write(";\n\n")
  
  f.write("e = ")
  f.write(json.dumps([str(origin.type) for origin, c in ti.errorOrigins]))
  f.write(";\n\n")
  
  f.write("p = ")
  f.write(json.dumps([ (str(c.left.exp.type), str(c.right.exp.type)) for o, c in ti.errorOrigins]))
  f.write(";\n\n")
  
  f.write("""
  $(document).ready(function() {
    $(allSelector(e)).addClass("error");
  });
  
  $(document).ready(function() {
    for(i in p)
    {
      $(allSelector(p[i])).addClass("inconsistent");
    }
  });
  
  // extracts the type from a code span
  getType = function(x){
    return $(x).attr("class").split(" ")[0];
  }
  
  // takes a list of classes, and returns a string that is a selector
  // for all of those classes
  allSelector = function(xs){
    if(xs.length < 1){
      return ""
    }
    xs_prime = []
    for(i in xs)
    {
      xs_prime[i] = "." + xs[i]
    }
    return xs_prime.join()
  }
  
  $(document).ready(function(){
    // for a term that has mouse movement, highlight all of the elements with a type that that appears in the map m for the type of that term
    $("span").mousemove(function(event){
      if(this == event.target){
        t = getType(this);
        if(t != "*"){
          $(allSelector(m[t])).addClass("comparable");
          $("." + t).addClass("focus");
        }
      }
    });
    
    $("span").mouseout(function(){
      t = getType(this);
      if(t != "*"){
        $("." + t).removeClass("focus");
        $(allSelector(m[t])).removeClass("comparable");
      }
    });
  });
  </script>
  </head><body>
  """)
  
  f.write("""
  <pre>{0}</pre>
  """.format(pp.visit(ast)))
  
  f.write("</body></html>")

#bleh = {"dog":[1,2,3], "cat":[3,4,5]}

#print(json.dumps(bleh))
##print(cs)

#ftvs = cs.ftv()
#print(ftvs)
#for tv in ftvs:
#  lows = cs.lower(TVar(tv))
##  print(lows)
#  lowStr = ", ".join([str(t) for t in lows])
#  print("lower({0}) is {1}".format(tv, lowStr))
#
#for id, tvar in ti.nameToType.items():
#  lowStr = ", ".join([str(t) for t in cs.lower(tvar)])
#  print("lower({0}) is {1}".format(id, lowStr))


