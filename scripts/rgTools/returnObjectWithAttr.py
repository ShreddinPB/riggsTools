"""
a class to find objects in a scene that are tagged with attrs
Author: John Riggs
"""

import maya.cmds as cmds

"""
returns objects with specific attributes 

* returns everything with the attribute not caring about the value
! returns all attributes that only have a value, so it will not return string attributes that are blank

"""
class returnObjectWithAttr(object):
    
    def __init__(self):
        self.__defaultCtrlSize = 1.0

    def all(self,attr,value = "*"):
        return self.__all(attr,value)

    def children(self, theObject,attr,value = "*"):
        
        allAttrs = self.__all(attr,value)
        allChildren = cmds.listRelatives(theObject,ad=True)
        if allChildren is not None:
            return list(set(allAttrs) & set(allChildren))
        else:
            return None

    def __all(self,attr,value = "*"):
        
        jointsToTest = cmds.ls(type=["transform","joint"])
        foundItems = []
        
        for item in jointsToTest:
            if cmds.objExists(item+"."+attr):

                attrType = cmds.attributeQuery(attr,node=item, attributeType=True)

                #if cmds.attributeQuery(attr,node=item, message=True):
                if attrType == 'message':
                    foundItems.append(item)

                if attrType == 'enum':
                    theValue = cmds.getAttr(item+"."+attr,asString=True)
                    if theValue == value or value == "*":
                        foundItems.append(item)

                    if theValue is not None and theValue != '' and theValue != 'none' and value == "!":
                        foundItems.append(item)

                if attrType == 'bool':
                    theValue = cmds.getAttr(item+"."+attr)
                    if value == 'True':
                        value = True
                    if value == 'False':
                        value = False
                    if theValue == value or value == "*":
                        foundItems.append(item)
                    
                if attrType == 'typed':
                    theValue = cmds.getAttr(item+"."+attr)

                    if theValue == value or value == "*":
                        foundItems.append(item)

                    if len(theValue) > 0 and value == '!':
                        foundItems.append(item)

                if attrType == 'long':
                    theValue = cmds.getAttr(item+"."+attr)

                    if theValue == value or value == "*":
                        foundItems.append(item)

                if attrType == 'double':
                    theValue = cmds.getAttr(item+"."+attr)

                    if theValue == value or value == "*":
                        foundItems.append(item)
                    #if len(theValue) > 0 and value == '!':
                        #foundItems.append(item)

        return foundItems