#实现扁平化
from mythril.disassembler.disassembly import Disassembly
from conversion import convert
from simulation import get_all_jump_address
from confusion import *
from virtual_machine import simulate
from cfg import get_codelist
import sys
from octopus.platforms.ETH.cfg import EthereumCFG
from calculate_gas import* 
def get_instructions(bytecode):
    obj=Disassembly(bytecode)
    instructions=obj.instruction_list
    #print(instructions)
    return instructions

def address_get_index(instructions:list,address):#由地址给出该地址在指令list里的下标
    for i in range(0,len(instructions)):
        if instructions[i]["address"]==address:
            return i

def change_datail(details):#样式分割
    # address:,opcode:,argument
    temp=details.split("\n")
    temp.pop()
    data=[]
    for t in temp:
        dic={}
        dic["address"]=int(eval("0x"+t.split(":")[0]))
        if "PUSH" not in t:
            dic["opcode"]=t.split(":")[1]
            dic["opcode"]=dic["opcode"][1:-1]
        else: #argument 
            s=t.split(":")[1]
            s=s.split(" ")
            dic["opcode"]=s[1]
            dic["argument"]=s[2]
        data.append(dic)
    return data

def get_most_instructions_block(bytecode,instructions):
    cfg = EthereumCFG(bytecode)
    cfg_block={}
    for block in cfg.basicblocks:
        index=str(block).split(" ")
        index=index[1].split("\n")[0]
        data=block.instructions_details()
        data=change_datail(data)
        cfg_block[index]=data
    maxnn=0
    cur_key=""
    for key,value in cfg_block.items():
        if len(value)>maxnn:
            cur_key=key
            maxnn=len(value)
    
    interval=[]
    interval.append(address_get_index(instructions,cfg_block[cur_key][0]["address"]))
    interval.append(address_get_index(instructions,cfg_block[cur_key][-1]["address"]))
    return interval
# 改变插入指令后的块区间地址
def change_interval(interval:list,index:int,tmp:int):
    for i in range(index,len(interval)):
        interval[i][0]+=tmp
        interval[i][1]+=tmp


def flattening(bytecode):
    instructions=get_instructions(bytecode)
    #jump_address=get_all_jump_address(bytecode)
    #找一下有最多指令数的块中 下标区间
    interval=get_most_instructions_block(bytecode,instructions)
    jump_table=get_all_jump_address(bytecode)
    # 把字符串的参数变为数值 方便计算
    for item in instructions:
        if "argument" in item:
            item["argument"]=int(eval(item["argument"]))


    # 在区间做划分 从9到5 看可以被分成几份
    total=interval[1]-interval[0]+1
    t=10#分割块的大小
    # 开始构建每个块的区间
    bg=interval[0]
    block_interval=[]
    for i in range(0,total//5-1):
        block_interval.append([bg+i*t,bg+(i+1)*t-1])
    block_interval.append([block_interval[-1][1]+1,interval[1]])
    
    # 插入控制流程的块
    '''
    JUMPDEST
    PUSH2 
    ADD
    JUMP
    字节码中占据6个字节
    '''
    index=block_interval[1][0]#第二个块之前插入控制指令
    address=instructions[index]["address"]
    change_address(address,6,instructions,jump_table)

    second_block_address=address+12
    control_block_address=address+6

    instructions.insert(index,{'address': address+5, 'opcode': 'JUMP'})
    instructions.insert(index,{'address':address+4,'opcode':'ADD'})
    instructions.insert(index,{'address': address+1, 'opcode': 'PUSH2', 'argument': address+12})
    instructions.insert(index,{'address': address, 'opcode': 'JUMPDEST'})

    change_interval(block_interval,1,4)#往后位移三条指令的位置
    # 处理第一个块
    '''
    PUSH1 0
    PUSH2 中转块
    JUMP 
    6个字节
    '''
    JUMPDEST_ad=instructions[index]["address"]+6

    index=block_interval[0][1]+1 # 在其下一个位置插入
    address=instructions[index]["address"]
    change_address(address,6,instructions,jump_table)
    
    instructions.insert(index,{'address': address+5, 'opcode': 'JUMP'})
    instructions.insert(index,{'address':address+2,'opcode':'PUSH2','argument':JUMPDEST_ad})#插入下一个块的地址
    instructions.insert(index,{'address': address, 'opcode': 'PUSH1', 'argument': 0})

    #跳转表增加地址
    jump_table.append({'type':'normal','where':address+2,'address':address+5,'to_address':JUMPDEST_ad,'opcode':'JUMP'})

    change_interval(block_interval,1,3)
    block_interval[0][1]+=3 #第一个块加3条指令

    for i in range(1,len(block_interval)-1):# 对第二个块到倒数第二个块 首尾加指令
        index=block_interval[i][0]
        address=instructions[index]["address"]
        change_address(address,1,instructions,jump_table)
        instructions.insert(index,{'address': address, 'opcode': 'JUMPDEST'})
        change_interval(block_interval,i+1,1)# 后面块区间位置后移1
        block_interval[i][1]+=1

        '''
        PUSH2 
        PUSH2 
        JUMP 
        占据7个字节
        '''

        # 计算下一个块对于第二个块的偏移量
        index=block_interval[i][1]+1
        address=instructions[index]["address"]
        offset=address-second_block_address+7
        change_address(address,7,instructions,jump_table)
        instructions.insert(index,{'address':address+6,'opcode':'JUMP'})
        instructions.insert(index,{'address':address+3,'opcode':'PUSH2','argument':control_block_address})
        instructions.insert(index,{'address':address,'opcode':'PUSH2','argument':offset})
        block_interval[i][1]+=3
        change_interval(block_interval,i+1,3)

        jump_table.append({'type':'normal','where':address+3,'address':address+6,'to_address':control_block_address,'opcode':'JUMP'})

    # 最后一个块加个JUMPDEST即可
    index=block_interval[-1][0]
    address=instructions[index]["address"]
    change_address(address,1,instructions,jump_table)
    instructions.insert(index,{'address': address, 'opcode': 'JUMPDEST'})
    block_interval[-1][1]+=1

    
    ''''
    for i in range(0,len(block_interval)):
        print(instructions[block_interval[i][0]]["address"],instructions[block_interval[i][1]]["address"])
    '''
    #禁止混淆的地方，防止相对偏移位置出问题,存的是指令集的下标

    forbid=[block_interval[0][1]-5,block_interval[-1][0]+2]

    return [instructions,jump_table,forbid]

if __name__=="__main__":
    bytecode = "60606040526000357c0100000000000000000000000000000000000000000000000000000000900480635fd8c7101461004f578063c0e317fb1461005e578063f8b2cb4f1461006d5761004d565b005b61005c6004805050610099565b005b61006b600480505061013e565b005b610083600480803590602001909190505061017d565b6040518082815260200191505060405180910390f35b3373ffffffffffffffffffffffffffffffffffffffff16611111600060005060003373ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060005054604051809050600060405180830381858888f19350505050151561010657610002565b6000600060005060003373ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600050819055505b565b34600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b565b6000600060005060008373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505490506101b6565b91905056"
    flattening(bytecode)



