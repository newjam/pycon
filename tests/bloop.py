


# Hacking: the art of exploitation. Ericson
# Skip first chapters, check networking chapter.
#
# Talk to someone at Janrain about internships for 2 lewis and clark students.
# 
# 
# 

class Complex:
  def __init__(self, r, i):
    self.r = r
    self.i = i
  def __add__(self, other):
    r = self.r + other.r
    i = self.i + other.i
    return Complex(r, i)

c1 = Complex(2.0, 1.0)
c2 = Complex("wat", 1.0)

c3 = c1 + c2 

#i = lambda x: x
#x = i(2)
#y = i("hello")
#
#z = x + y
#
#
#a = "hello" + 2

#####################

# Num <: tx

#x = "hello"

# tx <: Num
#x + 2

# Num <: Num

#class A:
#  def __init__(self, x):
#    self.x = x
#  def __add__(self, other):
#    return A(self.x + other.x)
#
#a = A("hello")
#b = A(3)
#a + b



#b = a.x + 2

#2 == 4

#class A:
#  x = 4
#
#x = A()
#
#x.x + "world"

#x = "hello"
#y = x + "world"


#  c = "g"
#  def a(self):
#    self.b = "hi!"
#    2 + self.c
#    return 2

#x = "hello"

#def foo(x):
#  return 2 + x

#foo(x)

#def foo(x, y):
#  return x

#x = foo("hello", 2)

#if x:
#  x
#else:
#  x


#r = Object()
#i = lambda x, y: x
#r.x = 2
#y = i(2, "Bob")

#x = "Hello, World"


