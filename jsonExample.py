import json
class consolidated:
	def __init__(self,numberValue):
		self.numberValue = numberValue

class number:
	def __init__(self,value,kuchBhi):
		self.value = value
		self.kuchBhi = kuchBhi

a = number(3,"Kuch Bhi")
print(a.__dict__)
#print(json.dumps(a.__dict__))
b = json.dumps(a.__dict__)
print (b)
#print(str(a.__dict__))
c = consolidated(a.__dict__)
print (c.__dict__)
print (json.dumps(c.__dict__))
