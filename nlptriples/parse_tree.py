import regex as re
def childFriomSplit(s):
    parse=re.findall("(\((?:[^()]+|(?R))*\))",s)
    return parse
def parseSplitter(s):
    parse=re.findall("\((\w+) (\(.*\))*\)",s)
    if parse==[]:
        parse=re.findall("\((\w+) (\w+)\)",s)
        if parse==[]:
            return None,None
        else:
            return parse[0][0],parse[0][1]
    else:
        parse=parse[0]
        return parse[0],childFriomSplit(parse[1])
    
def convToStr(s):
    toStr=re.findall("\(\w+ (\w+)\)",s)
    return " ".join(toStr)
    
class parse_tree():
    class node():
        def __init__(self,st,tag):
            self.child=[]
            self.parent=None
            self.leaf=False
            self.string=convToStr(st)
            self.org_str=st
            self.tag=tag
        def __repr__(self):
            return self.string

    def createNodeRecursive(self,org_str,parent):
        tag,parse=parseSplitter(org_str)
        node=self.node(org_str,tag)
        node.parent=parent
        if parse==None:
            parent.leaf=True
        else:
            if type(parse)==list:
                for child in parse:
                    ch_node=self.createNodeRecursive(child,node)
                    node.child.append(ch_node)
        return node
        
    def __init__(self,s):
        self.root=self.createNodeRecursive(s,None)

