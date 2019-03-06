from Katana import NodegraphAPI

ALPHABET=['A','B','C','D','E','F','G','H','I','J','K','L','M','N']

def AddNodeReferenceParam(destNode, paramName, node):
    param = destNode.getParameter(paramName)
    if not param:
        param = destNode.getParameters().createChildString(paramName, '')
    
    param.setExpression('getNode(%r).getNodeName()' % node.getName())

def GetRefNode(gnode, key):
    p = gnode.getParameter('node_'+key)
    if not p:
        return None
    
    return NodegraphAPI.GetNode(p.getValue(0))
    
def WalkProducer(producer, callback, location_types=[]):
   child = producer.getFirstChild()
   while child:
       WalkProducer(child, callback, location_types)
       child = child.getNextSibling()
   if producer.getType() in location_types:
       fullLocation = producer.getFullName()
       callback.append(fullLocation)
