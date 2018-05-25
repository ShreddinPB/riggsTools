import maya.cmds as cmds

def deleteAttachedConstraints(theObject):
    
    connected = cmds.listConnections(theObject,s=True,d=False)
    if connected != None:
        pruned = sorted(set(connected))
        for cn in pruned:
            if cmds.objExists(cn):
                doDelete = False
                if cmds.objectType(cn) == "pointConstraint":
                    doDelete = True
                    
                if cmds.objectType(cn) == "orientConstraint":
                    doDelete = True
                    
                if cmds.objectType(cn) == "aimConstraint":
                    doDelete = True
                
                if doDelete:
                    cmds.delete(cn)