# Run the program to run the list of jump addresses
from virtual_machine import simulate
from cfg import get_codelist
def sti(instructions:list)->list:
    t=simulate()
    jump_table=[]
    for data in instructions:
        print(data)
        address=data["address"]
        order=data["opcode"]
        if "PUSH" in order:
            t.PUSH(address,int(eval(data["argument"])))
        elif "MSTORE" in order:
            t.MSTORE()
        elif "MLOAD"== order:
            t.MLOAD(address)
        elif "CALLDATALOAD"==order:
            t.CALLDATALOAD(address)
        elif "CALLER"==order:
            t.CALLER(address)
        elif "SWAP" in order:
            argument=int(order[4:])
            t.SWAP(argument)
        elif "DIV" == order:
            t.DIV(address)
        elif "SUB"==order:
            t.SUB(address)
        elif "ADD" ==order:
            t.ADD(address)
        elif "AND"==order:
            t.AND(address)
        elif "OR"==order:
            t.OR(address)
        elif "DUP" in order:
            argument=int(order[3:])
            t.DUP(address,argument)
        elif "EQ"== order:
            t.EQ(address)
        elif "JUMPI"==order:
            item=t.JUMPI(address)
            jump_table.append(item)
        elif "JUMP"==order:
            item=t.JUMP(address)
            jump_table.append(item)
        elif "POP" ==order:
            t.POP()
        elif "RETURN" ==order:
            t.RETURN()
        elif "CALL"==order:
            t.CALL(address)
        elif "SHA3"==order:
            t.SHA3(address)
        elif "SSTORE"==order:
            t.SSTORE()
        elif "CALLVALUE"==order:
            t.CALLVALUE(address)
        elif "ADDRESS"==order:
            t.ADDRESS(address)
        elif "CODECOPY"==order:
            t.CODECOPY()
        elif "REVERT"==order:
            t.REVERT
        else:
            print("ERROR",order)
            pass
        #print("code:",address,t.stack)
    return jump_table

def check_repeat(item,address_table):
    for index in range(0,len(address_table)):
        if item["where"]==address_table[index]["where"] \
            and item["address"]==address_table[index]["address"]:
            return False
    return True

def get_all_jump_address(bytecode):
    data=get_codelist(bytecode)
    address_table=[]
    for index in range(0,len(data)):
        temp=sti(data[index])
        for i in range(0,len(temp)):
            if check_repeat(temp[i],address_table):
                address_table.append(temp[i])
    for index in range(0,len(address_table)):
        address_table[index]['type']='normal'
    #乱序的跳转表 不过不影响修改
    return address_table


if __name__=="__main__":
    '''
    Here, we need to traverse a feasible path according to the flow chart,
    which cannot be directly run code, so the stack simulation will directly error
    '''
    bytecode = "60606040526000357c0100000000000000000000000000000000000000000000000000000000900480635fd8c7101461004f578063c0e317fb1461005e578063f8b2cb4f1461006d5761004d565b005b61005c6004805050610099565b005b61006b600480505061013e565b005b610083600480803590602001909190505061017d565b6040518082815260200191505060405180910390f35b3373ffffffffffffffffffffffffffffffffffffffff16611111600060005060003373ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060005054604051809050600060405180830381858888f19350505050151561010657610002565b6000600060005060003373ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600050819055505b565b34600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b565b6000600060005060008373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505490506101b6565b91905056"
    print(get_all_jump_address(bytecode))