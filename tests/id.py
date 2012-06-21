
# The system doesn't handle polymorphism.

id = lambda x: x

x = id(2)
y = id("hello")

# 'x + 2' will be reported as creating an inconsistency, because the parameter
# to 'id' (that is, 'x'), is used as both a Num and a Str
z = x + 2

# It's important to note tat we actually would lose some information if
# if were polymorphic: types won't be traced inside of polymorphic expression.


