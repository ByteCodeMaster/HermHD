
#Convert decimal to hexadecimal, remove prefix
def to_hex(data:int)->str:
    data=str(hex(data))
    data=data[2:]
    return data

# Hexadecimal string to decimal
def hexstr_to_int(data:list)->int:
    data="".join(data) #Take out 32 bytes of memory
    data="0x"+data
    data=eval(data)
    data=int(data)
    return data






