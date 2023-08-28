#防止地址变换时PUSH的指令出问题。在这里修改一下。
#先预处理输出改变PUSH参数的位数 转换为字节码 再混淆
from mythril.disassembler.disassembly import Disassembly
from conversion import convert
from simulation import get_all_jump_address
from main import get_instructions
from confusion import change_address,address_get_index
import sys
def target_txt(instructions):
    from conversion import convert
    file=open("target_bytecode.txt", "a")
    oldout=sys.stdout
    sys.stdout=file
    for item in instructions:
        if "argument" in item:
            item["argument"]=hex(int(item["argument"]))
    res=convert(instructions)
    print(res)
    file.close()
    sys.stdout=oldout

def change_push_argument(bytecode):#这一步把他都变成int类型
    obj=Disassembly(bytecode)
    instructions=obj.instruction_list
    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))
    print("evm")
    jump_table=get_all_jump_address(bytecode)

    #排序，这样从小到大修改
    jump_table.sort(key=lambda x:x['where'],reverse=False)
    #双指针优化 找对应的index下标
    k_argument=[]#扩大参数位的指令在指令集的下标
    j_end=len(jump_table)
    j_p,i_p=0,0
    while j_p<j_end:
        cur_add=jump_table[j_p]['where']
        while instructions[i_p]['address']!=cur_add:
            i_p+=1
            #print(i_p)
        k_argument.append(i_p)
        i_p+=1
        j_p+=1
    for index in k_argument:
        address=instructions[index]["address"]
        argument=instructions[index]["opcode"]
        argument="PUSH"+str(int(argument[4:])+1)
        instructions[index]["opcode"]=argument
        change_address(address+1,1,instructions,jump_table)
    return instructions

if __name__=="__main__":
    bytecode = "60606040526000357c0100000000000000000000000000000000000000000000000000000000900480635fd8c7101461004f578063c0e317fb1461005e578063f8b2cb4f1461006d5761004d565b005b61005c6004805050610099565b005b61006b600480505061013e565b005b610083600480803590602001909190505061017d565b6040518082815260200191505060405180910390f35b3373ffffffffffffffffffffffffffffffffffffffff16611111600060005060003373ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060005054604051809050600060405180830381858888f19350505050151561010657610002565b6000600060005060003373ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600050819055505b565b34600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b565b6000600060005060008373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505490506101b6565b91905056"
    target_txt(change_push_argument(bytecode))



