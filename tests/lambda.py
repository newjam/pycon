# illustrates why polymorphism is needed in this system.
# not all constraints all shwn, but the important ones are!

# f:a->b
f = lambda x: x * 2

# a <: String
f("hello")
# a <: Num
x = f(2)
# Num <: a
# which creates a contradiction
x + 2




# a <: String
# a <: Num
# 
# Num <: Num
# Num <: String

# tx <: __add__: Num -> a

# could add __call__

