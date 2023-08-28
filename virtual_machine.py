#Simulate stack of evm virtual machine
from function import *
class simulate:
    '''
    Numbers and parameters are int
    '''
    def __init__(self) -> None:
        self.stack=[]
        # {address:  , value:,opcode:""}
        self.memory=['0' for i in range(1000)]
    
    #The following implements the evm instruction
    def PUSH(self,address:int,argument:int)->None:
        item={}
        item["address"]=address
        item["opcode"]="PUSH"
        item["argument"]=argument
        self.stack.append(item)


    def MSTORE(self)->None:#	Save word to memory
        offset=self.stack.pop()["argument"]
        offset=offset*2
        data=self.stack.pop()["argument"]
        data=to_hex(data)
        l=len(data)
        data=(64-l)*'0'+data   #32 bits are 64 characters
        for i in range(64):
            self.memory[i+offset]=data[i]


    def MLOAD(self,address:int)->None:
        offset=self.stack.pop()["argument"]
        offset=offset*2
        data=self.memory[offset:offset+64]
        #Take out 32 bytes of memory
        data=hexstr_to_int(data)
        #print("MLOAD",data)
        item={}
        item["address"]=address
        item["opcode"]="MLOAD"
        item["argument"]=data
        self.stack.append(item)
        

    #CALLDATALOAD  Do not change the stack
    def CALLDATALOAD(self,address:int):
        offset=self.stack.pop()["argument"]*2
        data=self.memory[offset:offset+64] #Extract 32 bytes (stack top is offset)
        data=hexstr_to_int(data)
        #print("CALLDATALOAD",data)
        item={}
        item["address"]=address
        item["opcode"]="CALLDATALOAD"
        item["argument"]=data
        self.stack.append(item)


    def CALLER(self,address:int): # the 20-byte address of the caller account
        data="0xbe862ad9abfe6f22bcb087716c7d89a26051f74c"
        data=int(eval(data))
        item={}
        item["address"]=address
        item["opcode"]="CALLER"
        item["argument"]=data
        self.stack.append(item)
        #print(data)


    def SWAP(self,argument:int)->None: #Exchange 1st and argument-nd stack items
        argument=argument+1
        self.stack[-1],self.stack[-argument]=self.stack[-argument],self.stack[-1]
    
    def SSTORE(self)->None:
        self.stack.pop()
        self.stack.pop()
    
    def DIV(self,address:int)->None:
        a=self.stack.pop()["argument"]
        b=self.stack.pop()["argument"]
        item={}
        item["address"]=address
        item["opcode"]="DIV"
        item["argument"]=a/b
        self.stack.append(item)

    def SUB(self,address:int)->None:
        a=self.stack[-1]["argument"]
        b=self.stack[-2]["argument"]
        self.stack.pop()
        self.stack.pop()
        
        item={}
        item["address"]=address
        item["opcode"]="SUB"
        item["argument"]=a-b
        self.stack.append(item) # Negative numbers should require complement


    def ADD(self,address:int)->None:
        a=self.stack[-1]["argument"]
        b=self.stack[-2]["argument"]
        self.stack.pop()
        self.stack.pop()
        item={}
        item["address"]=address
        item["opcode"]="ADD"
        item["argument"]=a+b
        self.stack.append(item)
    
    def AND(self,address:int)->None:
        a=self.stack.pop()["argument"]
        b=self.stack.pop()["argument"]
        item={}
        item["address"]=address
        item["opcode"]="AND"
        item["argument"]=a&b
        self.stack.append(item)
    
    def OR(self,address:int)->None:
        a=self.stack.pop()["argument"]
        b=self.stack.pop()["argument"]
        item={}
        item["address"]=address
        item["opcode"]="OR"
        item["argument"]=a|b
        self.stack.append(item)

    def DUP(self,address:int,argument:int)->None:
        data=self.stack[-argument]["argument"]
        item={}
        item["address"]=address
        item["opcode"]="DUP"
        item["argument"]=data
        self.stack.append(item)
    
    def EQ(self,address:int)->None:  #a == b: 1 if the left side is equal to the right side, 0 otherwise.
        a=self.stack[-1]["argument"]
        self.stack.pop()
        b=self.stack[-1]["argument"]
        self.stack.pop()
        res=0
        if a==b:
            res=1
        
        item={}
        item["address"]=address
        item["opcode"]="EQ"
        item["argument"]=res
        self.stack.append(item)
    
    '''
    JUMPI : [counter,b]
    counter: byte offset in the deployed code where execution will continue from. Must be a JUMPDEST instruction.
    b: the program counter will be altered with the new value only if this value is different from 0. 
    Otherwise, the program counter is simply incremented and the next instruction will be executed.
    '''
    def JUMPI(self,address:int)->map:
        counter=self.stack[-2]["argument"]
        b=self.stack[-1]["argument"]
        jump_address_sourse=self.stack[-1]["address"] # Source instruction of the address
        self.stack.pop()
        self.stack.pop()

        jump_item={}
        jump_item["where"]=jump_address_sourse
        jump_item["address"]=address #
        jump_item["to_address"]=b
        jump_item["opcode"]="JUMPI"
        return jump_item


    
    def JUMP(self,address:int)->map:
        temp=self.stack.pop()
        b=temp["argument"]
        jump_address_sourse=temp["address"]

        #print(self.stack)

        jump_item={}
        jump_item["where"]=jump_address_sourse
        jump_item["address"]=address
        jump_item["to_address"]=b
        jump_item["opcode"]="JUMP"
        return jump_item

    def POP(self)->None:
        self.stack.pop()
    
    def RETURN(self)->int:# Return memory value
        offset=self.stack.pop()["argument"]*2
        size=self.stack.pop()["argument"]*2
        data=self.memory[offset:offset+size]
        data=hexstr_to_int(data)
        #print("RETURN",data)
        return data
    
    def CALL(self,address:int)->None:
        for i in range(7):
            self.stack.pop()
        item={}
        item["address"]=address
        item["opcode"]="CALL"
        item["argument"]=0
        self.stack.append(item)
        #print("CALL")
    
    def SHA3(self,address:int)->None:
        self.stack.pop()
        self.stack.pop()
        item={}
        item["address"]=address
        item["opcode"]="SHA3"
        item["argument"]=0
        self.stack.append(item)
        #print("SHA3")
    
    def CALLVALUE(self,address:int)->None:
        item={}
        item["address"]=address
        item["opcode"]="CALLVALUE"
        item["argument"]=0
        self.stack.append(item)
    
    def CODECOPY(self):
        self.stack.pop()
        self.stack.pop()
        self.stack.pop()
    def REVERT(self):
        self.stack.pop()
        self.stack.pop()
    def ADDRESS(self,address):
        item={}
        item["address"]=address
        item["opcode"]="ADDRESS"
        item["argument"]=0
        self.stack.append(item)


if __name__=="__main__":
    t=simulate()

    t.PUSH(0,115341543235797707419527244145998463631733976271937281205136574426583511597056)
    t.PUSH(0,0)
    t.MSTORE()
    print(t.memory)


    '''
    t.stack.append(2)
    t.stack.append(0)
    print(t.RETURN())
    '''