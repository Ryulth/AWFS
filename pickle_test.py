from datetime import datetime
import pickle
 
class A(object):
    
    te=1
    def __init__(self, simple):
 
        self.simple = simple        
 
    def __eq__(self, other):
 
        if not hasattr(other, 'simple'):
 
            return False
 
        return self.simple == other.simple
 
    def __ne__(self, other):
 
        if not hasattr(other, 'simple'):
 
            return True
 
        return self.simple != other.simple
 
 
simple = dict(int_list=[1, 2, 3],
 
              text='string',
 
              number=3.44,
 
              boolean=True,
 
              none=None)
complex = dict(a=A(simple), when=datetime(2016, 3, 7))
print(complex)
x=pickle.dumps(complex, protocol=pickle.HIGHEST_PROTOCOL)

print(x)
z=x.decode('latin1')
print(z)
z2=z.encode('latin1')
print(z2)

y=pickle.loads(z2)
print(y['a'])
