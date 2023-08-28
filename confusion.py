import random
# Various obfuscation methods are implemented here
#  list {{'address': 0, 'opcode': 'PUSH1', 'argument': '0x60'}}
'''
插入混淆指令后更改地址
向后偏移起始地址后的指令
插入前的偏移地址
'''
def change_address(start:int,offset:int,instructions:list,jump_table:list):
    #修改跳转表的信息
    for index in range(0,len(jump_table)):
        if jump_table[index]['type']=='normal':
            if jump_table[index]["to_address"]>=start:#修改给出跳转地址指令的参数
                where=jump_table[index]["where"]

                where_index=address_get_index(instructions,where)
                instructions[where_index]["argument"]+=offset
                jump_table[index]["to_address"]+=offset

            if jump_table[index]["where"]>=start:
                jump_table[index]["where"]+=offset

            if jump_table[index]["address"]>=start:
                jump_table[index]["address"]+=offset

        elif jump_table[index]['type']=='memory':#一定是push进去的数字
            if jump_table[index]['to_address']>=start:
                where=jump_table[index]['where']
                where_index=address_get_index(instructions,where)

                instructions[where_index]['argument']+=offset
                jump_table[index]['to_address']+=offset

        elif jump_table[index]['type']=='sub':
            if jump_table[index]['to_address']>=start:
                where=jump_table[index]['low_address']
                where_index=address_get_index(instructions,where)

                instructions[where_index]['argument']-=offset
                jump_table[index]['to_address']+=offset
                jump_table[index]['low_argument']-=offset


    for order in instructions:
        if order['address']>=start:
            order['address']+=offset
    return [instructions,jump_table]

def address_get_index(instructions:list,address):#由地址给出该地址在指令list里的下标
    #instructions的顺序是增序，二分解决
    l,r=0,len(instructions)-1
    while l<r:
        mid=(l+r)//2
        t=instructions[mid]["address"]
        #print(t,mid) 
        if t <address:
            l=mid+1
        elif t>address:
            r=mid-1
        else:
            return mid
    if instructions[l]['address']==address:
        return l
    else:
        exit("address get index error")

'''

confusion_method_1
#insert JUMPDEST
插入通过在字节码中插入PUSH5(65) 6080604052 POP(50)
偏移量为6
'''
def confusion_method_1(instructions:list,jump_table:list,forbid:list):
    features=[]#这里存放的是地址，不是下标
    for index in range(0,len(instructions)):
        opcode=instructions[index]["opcode"]
        if opcode=="JUMPDEST":
            features.append(instructions[index]["address"]+1)
        if opcode=="JUMP" or opcode=="JUMPI":
            features.append(instructions[index]["address"])
    random.shuffle(features)
    for i in range(0,(len(features)+1)//2):#混淆一半的地址
        index=address_get_index(instructions,features[i])#先找位置再偏移
        if index>=forbid[0] and index<= forbid[1]:
            continue

        #print(features[i])
        #print(len(instructions))
        temp=change_address(features[i],7,instructions,jump_table)
        instructions=temp[0]
        jump_table=temp[1]

        #记录特征指令下标的也需要修改位置。

        instructions.insert(index,{'address': features[i]+6, 'opcode': 'POP'})#16进制转换10 6080604052
        instructions.insert(index,{'address': features[i], 'opcode': 'PUSH5', 'argument': 414470651986})
        
        change=features[i]
        for j in range(i+1,len(features)):#修改
            if features[j]>change:
                features[j]+=7
        #在前面插入 所以forbid里的前后区间做修改
        if index< forbid[0]:
            forbid[0]+=2
            forbid[1]+=2

        
    return [instructions,jump_table,forbid]

'''
插入jumpdest 创造较多基本块
随机找几个语句的下标,获取地址

'''

def confusion_method_2(instructions:list,jump_table:list,forbid:list):
    le=len(instructions)
    for i in range(0,min(10,le//5)):
        index=random.randint(0,le)#获取到下标，得到地址
        if index>=forbid[0] and index<= forbid[1]:
            continue
        address=instructions[index]["address"]

        temp=change_address(address,1,instructions,jump_table)
        instructions=temp[0]
        jump_table=temp[1]
        
        instructions.insert(index,{'address':address,'opcode':'JUMPDEST'})
        if index< forbid[0]:
            forbid[0]+=1
            forbid[1]+=1
    return [instructions,jump_table,forbid]


'''
寻找函数模式匹配，中间插入混淆指令打破函数匹配

'''

def confusion_method_3(instructions:list,jump_table:list,forbid:list):
    le=len(instructions)
    def check(index:int,instructions:list):#当index为DUP1时检查后面是否为函数模式
        if index+4>=len(instructions):
            return False
        if instructions[index+1]["opcode"]=="PUSH4" and \
            instructions[index+2]["opcode"]=="EQ" and\
            "PUSH" in instructions[index+3]["opcode"] and\
            instructions[index+4]["opcode"]=="JUMPI":
            return True
        return False
    
    functions=[] #放函数选择器里PUSH4的下标
    for i in range(0,le):
        if instructions[i]["opcode"]=="DUP1":
            if check(i,instructions):
                functions.append(instructions[i+1]["address"])
    
    for i in range(0,len(functions)//2):#控制混淆的比例
        index=address_get_index(instructions,functions[i])#先找位置再偏移
        if index>=forbid[0] and index<= forbid[1]:
            continue
        print(functions[i])
        #print(len(instructions))
        temp=change_address(functions[i],7,instructions,jump_table)
        instructions=temp[0]
        jump_table=temp[1]

        instructions.insert(index,{'address': functions[i]+6, 'opcode': 'POP'})#16进制转换10 6080604052
        instructions.insert(index,{'address': functions[i], 'opcode': 'PUSH5', 'argument': 414470651986})
        
        change=functions[i]
        for j in range(i+1,len(functions)):#修改
            if functions[j]>change:
                functions[j]+=7
        if index< forbid[0]:
            forbid[0]+=2
            forbid[1]+=2

    return [instructions,jump_table,forbid]



'''
将转移地址变为算术组合
捕捉到哪个指令送操作数进去的
#跳转表不存在该信息了，就删除被混淆的跳转表的项
'''


def confusion_method_4(instructions:list,jump_table:list,forbid:list):
    le=len(jump_table)
    def get_confusion_num(n:int):
        be=random.randint(eval("0xF000000011"),eval("0xFFFFFFFF00"))
        en=be+n
        return [be,en]
    for i in range(0,le):
        if random.random()<0.2:
            where=jump_table[i]["where"]
            #print(where)#改写操作数 开始混淆
            index=address_get_index(instructions,where)
            if index>=forbid[0] and index<= forbid[1]:
                continue

            #先扩空间确定to_address
            temp=change_address(where+1,10,instructions,jump_table)#后面的指令改变地址 本指令改参数
            instructions=temp[0]
            jump_table=temp[1]
            #print("4 ",where)
            #print(jump_table)
            num=get_confusion_num(jump_table[i]["to_address"])

            instructions[index]["opcode"]="PUSH5"
            instructions[index]["argument"]=num[0]
            instructions.insert(index+1,{'address':where+12,'opcode':"SUB"})
            instructions.insert(index+1,{'address':where+6,'opcode':'PUSH5','argument':num[1]})

            jump_table[i]={'type':'sub','low_address':where,'low_agument':num[0],'to_address':jump_table[i]["to_address"]}
            #print(jump_table)
            #print(instructions)
            if index< forbid[0]:
                forbid[0]+=2
                forbid[1]+=2
            
    return  [instructions,jump_table,forbid]





def confusion_method_5(instructions:list,jump_table:list,forbid:list):
#内存混淆 插入指令过多使用比例不能过大。
    le=len(jump_table)
    rand_int=random.randint(0,le-1)
    where=jump_table[rand_int]['where']#要混淆的push指令送入的跳转地址
    index=address_get_index(instructions,where)
    if index>forbid[0] and index< forbid[1]:
        return [instructions,jump_table,forbid]
    to_address=jump_table[rand_int]['to_address']
    del jump_table[rand_int]
    if to_address>where:
        to_address+=13

    change_address(where,13,instructions,jump_table)
    #print(where)
    next_where=instructions[index+1]['address']-1-13
    instructions.insert(index+1,{'address':next_where+13,'opcode':'MSTORE'})
    instructions.insert(index+1,{'address':next_where+11,'opcode':'PUSH1','argument':0})
    instructions.insert(index+1,{'address':next_where+10,'opcode':'SWAP1'})
    instructions.insert(index+1,{'address':next_where+9,'opcode':'MLOAD'})
    instructions.insert(index+1,{'address':next_where+7,'opcode':'PUSH1','argument':0})
    instructions.insert(index+1,{'address':next_where+6,'opcode':'MSTORE'})
    instructions.insert(index+1,{'address':next_where+4,'opcode':'PUSH1','argument':0})
    #print("address",instructions[index]['address'])
    instructions[index]['address']+=3-13
    instructions[index]['argument']=to_address
    instructions.insert(index,{'address':where+2,'opcode':'MLOAD'})
    instructions.insert(index,{'address':where+0,'opcode':'PUSH1','argument':0})
    #print(instructions)
    jump_table.append({'type':'memory','to_address':to_address,'where':where+3})
    #print(jump_table)
    if index< forbid[0]:
        forbid[0]+=2
        forbid[1]+=2
    return [instructions,jump_table,forbid]




if __name__=="__main__":
    data=[{'address': 51, 'opcode': 'DUP1'},
{'address': 52, 'opcode': 'PUSH4', 'argument': '0xc0e317fb'},
{'address': 57, 'opcode': 'EQ'},
{'address': 58, 'opcode': 'PUSH2', 'argument': '0x005e'},
{'address': 61, 'opcode': 'JUMPI'}]
    print(address_get_index(data,61))
    '''temp=confusion_method_3(data,[],[])
    data=temp[0]
    for i in range(0,len(data)):
        if "argument" in data[i]:
            data[i]["argument"]=hex(eval(data[i]["argument"]))
    print(data)
    '''
        
