name = "convertmac"

# MAC Address - colon
def mac2colon(string1):
    return ':'.join(str(string1).replace('.','').replace(':','').replace('-','').upper()[i:i+2] for i in range(0,12,2))

# MAC Address - dot
def mac2dot(string1):
    return '.'.join(str(string1).replace('.','').replace(':','').replace('-','').upper()[i:i+4] for i in range(0,12,4))

# MAC Address - hyphen
def mac2hyphen(string1):
    return '-'.join(str(string1).replace('.','').replace(':','').replace('-','').upper()[i:i+2] for i in range(0,12,2))
