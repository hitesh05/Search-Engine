import re

s = "hitesh== external links== me i u"
data = re.split(r'==\s*external links\s*==', s)
print(data)
