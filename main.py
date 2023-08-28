from mythril.disassembler.disassembly import Disassembly
from conversion import convert
from simulation import get_all_jump_address
from confusion import *
from virtual_machine import simulate
from cfg import get_codelist
from calculate_gas import* 
import sys
from flattening import flattening
def get_instructions(bytecode):
    obj=Disassembly(bytecode)
    instructions=obj.instruction_list
    #print(instructions)
    return instructions
#print(obj.function_name_to_address)

def print_ins(ins):
    file=open("res.txt", "a")
    oldout=sys.stdout
    sys.stdout=file
    for item in instructions:
        if "argument" in item:
            item["argument"]=hex(int(item["argument"]))
        print(item)
    file.close()
    sys.stdout=oldout



if __name__=="__main__":
    bytecode = "60606040526000357c0100000000000000000000000000000000000000000000000000000000900480635fd8c7101461004f578063c0e317fb1461005e578063f8b2cb4f1461006d5761004d565b005b61005c6004805050610099565b005b61006b600480505061013e565b005b610083600480803590602001909190505061017d565b6040518082815260200191505060405180910390f35b3373ffffffffffffffffffffffffffffffffffffffff16611111600060005060003373ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060005054604051809050600060405180830381858888f19350505050151561010657610002565b6000600060005060003373ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600050819055505b565b34600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b565b6000600060005060008373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505490506101b6565b91905056"
    instructions=get_instructions(bytecode)
    jump_table=get_all_jump_address(bytecode)
    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))
    

    confusion_method_5(instructions,jump_table,forbid=[0,1])
    #data=flattening(bytecode)
    #instructions=data[0]
    #jump_table=data[1]
    #forbid=data[2]
    #print(jump_table)
'''
    data=confusion_method_1(instructions,jump_table,forbid)
    instructions=data[0]
    jump_table=data[1]
    forbid=data[2]
    print(forbid)

    data=confusion_method_2(instructions,jump_table,forbid)
    instructions=data[0]
    jump_table=data[1]
    forbid=data[2]
    print(forbid)

    data=confusion_method_3(instructions,jump_table,forbid)
    instructions=data[0]
    jump_table=data[1]
    forbid=data[2]
    print(forbid)

    for item in instructions:
        if "argument" in item:
            item["argument"]=hex(int(item["argument"]))
    temp=convert(instructions)
    print(temp)

    gas=get_gas(instructions)
    print("gas",gas)
    print("\n\n\n\n")
    '''