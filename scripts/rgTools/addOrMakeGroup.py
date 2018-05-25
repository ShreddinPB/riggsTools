import maya.cmds as cmds

#v1.0
def addOrMakeGroup(itemsToAdd, groupName):

    theGroup=""
    
    if not isinstance(itemsToAdd, list):
        itemsToAdd = [itemsToAdd]
        
    if cmds.objExists(groupName) == True:
        theGroup = groupName
        for ita in itemsToAdd:
            parents = cmds.listRelatives(ita,p=True)
            
            if parents is None or parents[0] != theGroup:
                #print 'parenting in add or make group'
                cmds.parent(itemsToAdd, theGroup)
        
    else:
        theGroup = cmds.group(em=True,n=groupName)
        
        for ita in itemsToAdd:
            parents = cmds.listRelatives(ita,p=True)
            if parents is None or parents[0] != theGroup:
                #print 'parenting in add or make group 2'
                cmds.parent(itemsToAdd, theGroup)
        
    return theGroup