from octopus.analysis.graph import CFGGraph
from octopus.platforms.ETH.cfg import EthereumCFG
from octopus.core.basicblock import BasicBlock
from octopus.core.edge import Edge
# smart contract bytecode
# create the CFG
def change_datail(details):
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



def get_cfg_block(cfg):# CFGGraph(cfg)
    cfg_block={}
    for block in cfg.basicblocks:
        index=str(block).split(" ")
        index=index[1].split("\n")[0]
        data=block.instructions_details()
        data=change_datail(data)
        cfg_block[index]=data
    return cfg_block #The order of blocks is positive
        

def get_cfg_edge(cfg):
    cfg_edge={}
    for temp in cfg.edges:
        edge=temp.as_dict()
        fro=edge["from"]
        to=edge["to"]
        if fro in cfg_edge:
            cfg_edge[fro].append(to)
        else:
            cfg_edge[fro]=[]
            cfg_edge[fro].append(to)
    return cfg_edge


#res store all dfs sequences
def dfs(cur,nodes_set,cfg_edge,seq,res):
    if cur not in cfg_edge.keys():
        res.append(seq.copy())
        return 
    for next in cfg_edge[cur]:
        if next not in nodes_set:
            nodes_set.add(next)
            seq.append(next)
            dfs(next,nodes_set,cfg_edge,seq,res)
            seq.pop()

def get_all_dfs(cfg):
    cfg_edge=get_cfg_edge(cfg)
    cfg_block=get_cfg_block(cfg)
    nodes=list(cfg_block.keys())
    #产生所有DFS遍历序列
    nodes_set=set()
    nodes_set.add(nodes[0])
    res=[]
    dfs(nodes[0],nodes_set,cfg_edge,[nodes[0]],res)
    return res


def get_codelist(bytecode_hex):
    #print(bytecode_hex)
    cfg = EthereumCFG(bytecode_hex)
    res=get_all_dfs(cfg)
    cfg_block=get_cfg_block(cfg)
    data=[]
    #print(type(res))
    for index in range(0,len(res)):
        code=[]
        for i in  range(0,len(res[index])):
            code+=cfg_block[res[index][i]]
        data.append(code)
    return data #Get all branch codes

if __name__=="__main__":
    bytecode_hex = "60606040526000357c0100000000000000000000000000000000000000000000000000000000900480635fd8c7101461004f578063c0e317fb1461005e578063f8b2cb4f1461006d5761004d565b005b61005c6004805050610099565b005b61006b600480505061013e565b005b610083600480803590602001909190505061017d565b6040518082815260200191505060405180910390f35b3373ffffffffffffffffffffffffffffffffffffffff16611111600060005060003373ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060005054604051809050600060405180830381858888f19350505050151561010657610002565b6000600060005060003373ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600050819055505b565b34600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b565b6000600060005060008373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505490506101b6565b91905056"
    cfg = EthereumCFG(bytecode_hex)
    print(get_cfg_edge(cfg))