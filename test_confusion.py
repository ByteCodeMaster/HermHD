from change_push_argument import change_push_argument
from conversion import convert
import sys
from simulation import get_all_jump_address
from calculate_gas import* 
from confusion import *
from mythril.disassembler.disassembly import Disassembly
from flattening import flattening
gas_list=[]
def in_file(data,filename):
    file=open(filename, "a")
    oldout=sys.stdout
    sys.stdout=file
    print(data)#输出数据
    file.close()
    sys.stdout=oldout

def get_big_byte(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    instructions=change_push_argument(lines[0])
    for item in instructions:
        if "argument" in item:
            item["argument"]=hex(int(item["argument"]))
    gas_list.append(get_gas(instructions))
    res=convert(instructions)
    return res

def get_instructions(bytecode):
    obj=Disassembly(bytecode)
    instructions=obj.instruction_list
    #print(instructions)
    return instructions
#print(obj.function_name_to_address)

def in_gas(gaslist,filename):
    file=open(filename, "a")
    oldout=sys.stdout
    sys.stdout=file
    for i in range(0,len(gaslist)):
        print(str(i)+"-gas:"+str(gaslist[i]))
    file.close()
    sys.stdout=oldout

if __name__=="__main__":
    num=3
    path="/home/hzk/Desktop/test_confusion/res/"+str(num)+"/"
    bytecode=get_big_byte("/home/hzk/Desktop/test_confusion/bytecode/"+str(num)+".txt")
    in_file(bytecode,path+str(num)+'-k.txt')
    print(bytecode)
    
    instructions=get_instructions(bytecode)
    jump_table=get_all_jump_address(bytecode)

    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))
    
    data=confusion_method_1(instructions,jump_table,[100000,10000])
    in_file(convert(data[0]),path+str(num)+'-1c.txt')
    gas_list.append(get_gas(data[0]))
   


    instructions=get_instructions(bytecode)
    jump_table=get_all_jump_address(bytecode)

    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))
    
    data=confusion_method_2(instructions,jump_table,[100000,10000])
    in_file(convert(data[0]),path+str(num)+'-2c.txt')
    gas_list.append(get_gas(data[0]))
    

    instructions=get_instructions(bytecode)
    jump_table=get_all_jump_address(bytecode)

    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))
    
    data=confusion_method_3(instructions,jump_table,[100000,10000])
    in_file(convert(data[0]),path+str(num)+'-3c.txt')
    gas_list.append(get_gas(data[0]))
    

    instructions=get_instructions(bytecode)
    jump_table=get_all_jump_address(bytecode)

    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))
    
    data=confusion_method_4(instructions,jump_table,[100000,10000])
    in_file(convert(data[0]),path+str(num)+'-4c.txt')
    gas_list.append(get_gas(data[0]))
   

    instructions=get_instructions(bytecode)
    jump_table=get_all_jump_address(bytecode)

    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))
    
    data=confusion_method_5(instructions,jump_table,[100000,10000])
    in_file(convert(data[0]),path+str(num)+'-5c.txt')
    gas_list.append(get_gas(data[0]))
    


    data=flattening(bytecode)
    in_file(convert(data[0]),path+str(num)+'-6c.txt')
    print(len(data[0]))
    gas_list.append(get_gas(data[0]))
    #print(gas_list)

    def tol(byte):
        data=flattening(bytecode)
        instructions=data[0]
        jump_table=data[1]
        forbid=data[2]
        
        data=confusion_method_1(instructions,jump_table,forbid)
        instructions=data[0]
        jump_table=data[1]
        forbid=data[2]


        data=confusion_method_2(instructions,jump_table,forbid)
        instructions=data[0]
        jump_table=data[1]
        forbid=data[2]

        data=confusion_method_3(instructions,jump_table,forbid)
        instructions=data[0]
        jump_table=data[1]
        forbid=data[2]

        gas_list.append(get_gas(data[0]))
        in_file(convert(data[0]),path+str(num)+'-7c.txt')
        print(gas_list)
    
    tol(bytecode)
    in_gas(gas_list,path+str(num)+"-gas.txt")


