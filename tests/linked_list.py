class List:
  def __init__(self, x, next):
    self.x = x
    self.next = next
  def cons(self, x):
    return List(x, self)

#def length(list):

l = List(2, None).cons(1).cons(0)

def length(xs):
  return 0 if xs == None else 1 + length(xs.next)

i = length(l)
