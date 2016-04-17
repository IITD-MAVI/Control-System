import json

class number:
	def __init__(self,value,kuchBhi):
		self.value = value
		self.kuchBhi = kuchBhi

a = number(3,"Kuch Bhi")
print(a.__dict__)
print(json.dumps(a.__dict__))
b = json.dumps(a.__dict__)
print (b.__class__)
