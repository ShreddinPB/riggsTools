import maya.cmds as cmds
#from rgTools.moveIt import *
from rgTools.addOrMakeGroup import *

def createMatrixReverse(fromJoint, toJoint, axis = "X"):
    
    decomMat = cmds.createNode("decomposeMatrix", n = "dm_"+fromJoint+"_to_"+toJoint)
    revNode = cmds.createNode("multiplyDivide", n = "rev_"+fromJoint+"_to_"+toJoint)
    revNodeRot = cmds.createNode("multiplyDivide", n = "revRot_"+fromJoint+"_to_"+toJoint)
    
    locName = "loc_"+fromJoint+"_to_"+toJoint
    offsetLocName = "loc_"+fromJoint+"_to_"+toJoint+'_offset'

    if cmds.objExists(locName):
        cmds.delete(locName)
    wsLoc = cmds.spaceLocator(n=locName)
    wsOffsetLoc = cmds.spaceLocator(n=offsetLocName)
    cmds.parent(wsOffsetLoc, wsLoc)

    if cmds.objExists(toJoint+'.mirrorAxisOffset'):
        mirrorAxisOffset = cmds.getAttr(toJoint+'.mirrorAxisOffset')
        if mirrorAxisOffset is not None:
            mirrorAxisOffsetSplit = mirrorAxisOffset.split(',')
            for mao in mirrorAxisOffsetSplit:
                maoSplit = mao.split(';')
                if len(maoSplit) == 2:
                    cmds.setAttr(wsOffsetLoc[0]+'.'+maoSplit[0], float(maoSplit[1]))
    #cmds.setAttr(wsLoc[0]+".v", 0)
    addOrMakeGroup(wsLoc, "wsMatrixReverseNodes")
    
    #moveIt(wsLoc,toJoint,False)
    cmds.xform(wsLoc ,ws=True,m=(cmds.xform(toJoint,q=True,ws=True,m=True)))
    
    cmds.connectAttr(fromJoint+".worldMatrix",decomMat+".inputMatrix",f=True)
    
    #do Translations X
    cmds.connectAttr(decomMat+".outputTranslate.outputTranslateX",revNode+".input1.input1X",f=True)
    cmds.connectAttr(revNode+".outputX",wsLoc[0]+".translateX",f=True)
    cmds.setAttr(revNode+".input2X", -1)
    
    #do rotations X
    cmds.connectAttr(decomMat+".outputRotate.outputRotateX",revNodeRot+".input1.input1X",f=True)
    cmds.connectAttr(revNodeRot+".outputX",wsLoc[0]+".rotateX",f=True)

    mirrorAxis = ''
    if cmds.objExists(toJoint+'.mirrorAxis'):
        mirrorAxis = cmds.getAttr(toJoint+'.mirrorAxis')

    mirrorValue = -1

    if mirrorAxis == '':
        mirrorValue = -1
    else:
        if mirrorAxis is not None:
            mirrorSplit = mirrorAxis.split(',')
            if 'rotateX' in mirrorSplit:
                mirrorValue = 1

    cmds.setAttr(revNodeRot+".input2X", mirrorValue)

    #do rotations Y
    cmds.connectAttr(decomMat+".outputRotate.outputRotateY",revNodeRot+".input1.input1Y",f=True)
    cmds.connectAttr(revNodeRot+".outputY",wsLoc[0]+".rotateY",f=True)

    mirrorValue = -1
    if mirrorAxis == '':
        mirrorValue = -1
    else:
        if mirrorAxis is not None:
            mirrorSplit = mirrorAxis.split(',')
            if 'rotateY' in mirrorSplit:
                mirrorValue = 1

    cmds.setAttr(revNodeRot+".input2Y", mirrorValue)
    
    #do rotations Z
    cmds.connectAttr(decomMat+".outputRotate.outputRotateZ",revNodeRot+".input1.input1Z",f=True)
    cmds.connectAttr(revNodeRot+".outputZ",wsLoc[0]+".rotateZ",f=True)

    mirrorValue = -1
    if mirrorAxis == '':
        mirrorValue = -1
    else:
        if mirrorAxis is not None:
            mirrorSplit = mirrorAxis.split(',')
            if 'rotateZ' in mirrorSplit:
                mirrorValue = 1

    cmds.setAttr(revNodeRot+".input2Z", mirrorValue)
    
    cmds.connectAttr(decomMat+".outputTranslate.outputTranslateY",wsLoc[0]+".translateY",f=True)
    cmds.connectAttr(decomMat+".outputTranslate.outputTranslateZ",wsLoc[0]+".translateZ",f=True)
        
    #cmds.connectAttr(decomMat+".outputRotate.outputRotateX",wsLoc[0]+".rotateX",f=True)
    
    #moveIt(toJoint, wsLoc,True)
    print 'working on '+toJoint
    cmds.xform(toJoint ,ws=True,m=(cmds.xform(wsOffsetLoc,q=True,ws=True,m=True)))
    cmds.pointConstraint(wsOffsetLoc,toJoint,o=[0,0,0],w=1)
    cmds.orientConstraint(wsOffsetLoc,toJoint,o=[0,0,0],w=1)
    
    return wsLoc
    
def createReverseForAll(items, newPrefix, axis):
    
    for item in items:
        newSide = item.split("_")
        newSide[0] = newPrefix
        newItem = "_".join(newSide)
        
        createMatrixReverse(item,newItem,axis)