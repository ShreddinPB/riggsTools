import maya.cmds as cmds

def returnBlendShapeNode(mesh):
    
    blendNodes = []
    
    historyNodes = cmds.listHistory(mesh)
    
    for hn in historyNodes:
        nodeIs = cmds.nodeType(hn)
        if nodeIs == 'blendShape':
            blendNodes.append(hn)
            
    return blendNodes