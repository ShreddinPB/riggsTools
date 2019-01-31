"""
a class to manipulate attrs, save and load also
Author: John Riggs
"""
import rgTools.fileUtils as fu

import maya.cmds as cmds
import maya.mel as mel

import xml.dom.minidom as xd

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class attrUtilities(object):
    
    def __init__(self):

        self.__futil = fu.fileUtils()

    def transfer(self, fromObj, toObj, attr):

        '''
        A way to transfer attrs from one object to the other
        @param fromObj: Really?
        @param toObj: Derp
        @param attr: the attr to transfer
        '''

        if cmds.objExists(fromObj) and cmds.objExists(toObj):
            if cmds.objExists(fromObj+'.'+attr):
                if cmds.objExists(toObj+'.'+attr):
                    cmds.setAttr(toObj+'.'+attr, cmds.getAttr(fromObj+'.'+attr))
                else:

                    attrType = cmds.attributeQuery(attr, node = fromObj,at=True)

                    if attrType == 'bool':
                        cmds.addAttr(toObj, ln = attr, at='bool')
                        cmds.setAttr(toObj+'.'+attr, cmds.getAttr(fromObj+'.'+attr), e = True, keyable = True)

                    elif attrType == 'typed':
                        cmds.addAttr(toObj, ln= attr, dt="string")
                        cmds.setAttr(toObj+'.'+attr, cmds.getAttr(fromObj+'.'+attr), type="string")

                    elif attrType == 'float':
                        cmds.addAttr(toObj, ln= attr, dt="double")
                        cmds.setAttr(toObj+'.'+attr, cmds.getAttr(fromObj+'.'+attr), type="double")

                    elif attrType == 'enum':
                        cmds.addAttr(toObj, ln=attr, at="enum", en = cmds.attributeQuery(attr, node = fromObj,le=True)[0])
                        cmds.setAttr(toObj+'.'+attr, cmds.getAttr(fromObj+'.'+attr))

    #I THINK THESE WERE MOVED TO RIGGINGATTRUTILS
    """
    def transferRiggingattrs(self, fromObject, toObject):

        attrs = ['autoSetups', 'ikSystems', 'dynamicSetups', 'muscleSetups', 'poseSetups', 'mocapConstraints', 'animation', 'deformer', 'reverseJointAxis', 'setupOptions','poseOptions']
        for attr in attrs:
            self.transfer(fromObject, toObject, attr)

    def addOrUpdateRiggingattrs(self, theObjects):

        if isinstance(theObjects, str):
            theObjects = [theObjects]

        for theObject in theObjects:
            #loop thru enums and build all from directory structure
            enumsAre = ['autoSetups', 'ikSystems', 'dynamicSetups', 'muscleSetups', 'poseSetups', 'mocapConstraints']
            currentAttr = 'none'
            #add auto setup enum
            for eas in enumsAre:
                if cmds.objExists(theObject+'.'+eas):
                    currentAttr = cmds.getAttr(theObject+'.'+eas, asString = True)
                    cmds.deleteAttr(theObject, at =eas)

                cmds.addAttr(theObject, ln=eas, at="enum", en = "none:" + ":".join(self.__futil.returnSystem(eas)))
                #cmds.setAttr(theObject+'.'+eas, currentAttr)
                #print 'one', ":".join(self.__futil.returnSystem(eas))
                self.setEnumAttrWithString(theObject, eas, currentAttr)

            #add control shape enum
            shapeAttr = 'none'
            
            if cmds.objExists(theObject+'.controlShape'):
                shapeAttr = cmds.getAttr(theObject+'.controlShape', asString = True)
                cmds.deleteAttr(theObject, at ='controlShape')

            cmds.addAttr(theObject, ln="controlShape", at="enum", en = "none:" + ":".join(self.__futil.returnCtrlShapes()))
            #print 'two'
            self.setEnumAttrWithString(theObject,'controlShape', shapeAttr)
            #booleans

            boolAttr = 0
            for bl in ['animation', 'deformer', 'reverseJointAxis']:

                if cmds.objExists(theObject + '.' + bl):
                    boolAttr = cmds.getAttr(theObject+'.'+bl)
                    cmds.deleteAttr(theObject, at = bl)
                    
                cmds.addAttr(theObject, ln = bl, at='bool')
                cmds.setAttr(theObject+'.'+bl, boolAttr, e = True, keyable = True)

            stringDefault = ''
            for st in ['setupOptions','poseOptions']:

                if cmds.objExists(theObject + '.' + st):
                    stringDefault = cmds.getAttr(theObject+'.'+st)
                    cmds.deleteAttr(theObject, at = st)

                cmds.addAttr(theObject, ln= st, dt="string")
                if stringDefault is not None:
                    cmds.setAttr(theObject+'.'+st, stringDefault, type="string")

    """
    def addOrUpdateAttr(self, theObject, theAttr, theValue, attrType):

        '''
        A quick way to add or update an attr
        @param theObject: Really?
        @param theAttr: the attr to add or update
        @param theValue: The Value to set
        @param attrType: the type of attr
        '''

        if attrType == 'typed':
            if not cmds.objExists(theObject+'.'+theAttr):
                if cmds.objExists(theObject):
                    cmds.addAttr(theObject, ln= theAttr, dt="string")
                else:
                    cmds.error('no object named '+theObject)

            cmds.setAttr(theObject+'.'+theAttr, theValue, type="string")

        elif attrType == 'float':
            if not cmds.objExists(theObject+'.'+theAttr):
                if cmds.objExists(theObject):
                    cmds.addAttr(theObject, ln= theAttr)
                else:
                    cmds.error('no object named '+theObject)

            cmds.setAttr(theObject+'.'+theAttr, float(theValue), e = True, keyable = True)

        elif attrType == 'double':
            if not cmds.objExists(theObject+'.'+theAttr):
                if cmds.objExists(theObject):
                    cmds.addAttr(theObject, ln= theAttr, type = 'double')
                else:
                    cmds.error('no object named '+theObject)

            cmds.setAttr(theObject+'.'+theAttr, float(theValue), e = True, keyable = True)

        elif attrType == 'doubleLinear':
            if not cmds.objExists(theObject+'.'+theAttr):
                if cmds.objExists(theObject):
                    cmds.addAttr(theObject, ln= theAttr, type = 'doubleLinear')
                else:
                    cmds.error('no object named '+theObject)

            cmds.setAttr(theObject+'.'+theAttr, float(theValue), e = True, keyable = True)

        elif attrType == 'bool':
            if not cmds.objExists(theObject+'.'+theAttr):
                if cmds.objExists(theObject):
                    cmds.addAttr(theObject, ln= theAttr, at="bool")
                else:
                    cmds.error('no object named '+theObject)

            if theValue == "True":
                theValue = 1.0

            else:
                theValue = 0.0

            cmds.setAttr(theObject+'.'+theAttr, theValue, e = True, keyable = True)


    def delConnection(self, destName):

        '''
        A quick way to delete a connection
        @param destName: destination attr to delete connection from
        '''
        
        if cmds.connectionInfo(destName, isDestination = True):
        
            destination = cmds.connectionInfo(destName, getExactDestination = True)

            srcConn = cmds.listConnections( destination, s=True, d=False, type = 'character')

            cmds.delete(destination, icn = True)

    def saveAttrsToFile(self, objects, fileName, attrs = []): #attrs = [],

        '''
        Save attribute settings to a file so rig rebuilds the same exact way
        @param objects: objects to save info from
        @param fileName: the file to save as
        @param attrs: if nothing is passed then it saves all used defined attrs
        '''
        print 'Saving attrs for: ', objects

        doc = xd.Document()
        root = doc.createElement("objects")
        doc.appendChild(root)

        booleans = []
        numerics = []
        strings = []
        enums = []
        doubles = []
        doubleLinears = []

        if isinstance(objects, str):
            objects = [objects]

        for obj in objects:

            objElement = doc.createElement(obj)
            root.appendChild(objElement)

            if attrs is None:
                attrs = cmds.listAttr(obj,w=True, userDefined = True)
            elif len(attrs) == 0:
                attrs = cmds.listAttr(obj,w=True, userDefined = True)

            if attrs:
                for attr in attrs:

                    if cmds.objExists(obj+'.'+attr):
                        attrType = cmds.attributeQuery(attr, node = obj, attributeType = True)
                        if attrType == "float":
                            numerics.append(attr)

                        if attrType == "double":
                            doubles.append(attr)

                        if attrType == "doubleLinear":
                            doubleLinears.append(attr) 

                        if attrType == "bool":
                            booleans.append(attr)

                        if attrType == "typed":
                            strings.append(attr)

                        if attrType == "enum":
                            enums.append(attr)

            if len(numerics) > 0:
                numberElement = doc.createElement("float")
                objElement.appendChild(numberElement)

                for attr in numerics:
                    numberElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr)))

            if len(doubles) > 0:
                numberElement = doc.createElement("double")
                objElement.appendChild(numberElement)

                for attr in doubles:
                    numberElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr)))

            if len(doubleLinears) > 0:
                numberElement = doc.createElement("doubleLinear")
                objElement.appendChild(numberElement)

                for attr in doubleLinears:
                    numberElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr)))

            if len(booleans) > 0:
                booleansElement = doc.createElement("bool")
                objElement.appendChild(booleansElement)

                for attr in booleans:
                    if cmds.objExists(obj+'.'+attr):
                        booleansElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr)))

            if len(strings) > 0:
                typedElement = doc.createElement("typed")
                objElement.appendChild(typedElement)

                for attr in strings:
                    if cmds.objExists(obj+'.'+attr):                    
                        typedElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr)))

            if len(enums) > 0:

                enumsElement = doc.createElement("enum")
                objElement.appendChild(enumsElement)

                for attr in enums:
                    enumValuesElement = doc.createElement(attr)
                    enumsElement.appendChild(enumValuesElement)
                    enumsElement.setAttribute(attr, str(cmds.attributeQuery(attr, node = obj, le = True)))

                enumSettingsElement = doc.createElement("enumSettings")
                objElement.appendChild(enumSettingsElement)

                for attr in enums:
                    value = cmds.getAttr(obj+'.'+attr)
                    enumSettingsElement.setAttribute(attr, str(value))

            booleans = []
            numerics = []
            strings = []
            enums = []

        print 'Saving Rig Description as: '
        print fileName
        
        f = open(fileName, 'w')

        f.write(doc.toprettyxml())

        f.close()


    def loadattrsFromFile(self, fileName, makeDefault = True): 

        '''
        load attribute settings from a file so rig rebuilds the same exact way
        @param fileName: the file to load from
        @param makeDefault: set the newly loaded attr as the default value
        '''

        attrsFile = xd.parse(fileName)

        theObjects = attrsFile.getElementsByTagName('objects')

        objectNodes = theObjects[0].childNodes
            
        for obj in objectNodes:
            if obj.nodeName != '#text':
                #if self.debug: print obj.nodeName
                attrTypeNodes = obj.childNodes
                for attrType in attrTypeNodes:
                    if attrType.nodeName != '#text':
                        #if self.debug: print attrType.nodeName
                        attrItems = attrType.attributes.items()
                        for attr in attrItems:
                            if cmds.objExists(obj.nodeName):
                                if attrType.nodeName == 'enumSettings':
                                    cmds.setAttr(obj.nodeName+'.'+attr[0], int(attr[1]))
                                else:
                                    self.addOrUpdateAttr(obj.nodeName, attr[0], attr[1], attrType.nodeName)
                            else:
                                log.warning('Skipping, Object not found :\n%s' % obj.nodeName)


    def saveChannelSettings(self, objects, fileName, attrs = []):

        '''
        save channel settings from a file so rig rebuilds the same exact way
        @param objects: objects to save info from
        @param fileName: the file to save as
        @param attrs: if nothing is passed then it saves all basic transformation attrs ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        '''

        #quick test to make sure we pass an array
        if isinstance(objects, str):
            objects = [objects]

        if len(attrs) == 0:
            attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']

        #make the file
        doc = xd.Document()
        root = doc.createElement("controls")
        doc.appendChild(root)

        for obj in objects:

            objName = obj.split(':')
            objElement = doc.createElement(objName[-1])

            namespace = ''

            if len(objName) >1:
                del(objName[-1])
                namespace = '.'.join(objName)

            root.appendChild(objElement)

            locksElement = doc.createElement("locked")
            objElement.appendChild(locksElement)

            unLocksElement = doc.createElement("unLocked")
            objElement.appendChild(unLocksElement)

            keyableElement = doc.createElement("keyable")
            objElement.appendChild(keyableElement)

            nonKeyableElement = doc.createElement("nonKeyable")
            objElement.appendChild(nonKeyableElement)

            channelBoxElement = doc.createElement("channelBox")
            objElement.appendChild(channelBoxElement)

            nameSpaceElement = doc.createElement("nameSpace")
            objElement.appendChild(nameSpaceElement)

            nameSpaceElement.setAttribute('nameSpace', namespace)
            
            for attr in attrs:
                if cmds.getAttr(obj+'.'+attr, l=True):
                    locksElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr, l=True)))
                else:
                    unLocksElement.setAttribute(attr, 'False')

                if cmds.getAttr(obj+'.'+attr, k=True):
                    keyableElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr, k=True)))
                else:
                    nonKeyableElement.setAttribute(attr, 'False')

                if cmds.getAttr(obj+'.'+attr, cb=True):
                    channelBoxElement.setAttribute(attr, str(cmds.getAttr(obj+'.'+attr, cb=True)))
                else:
                    channelBoxElement.setAttribute(attr, 'False')


        f = open(fileName, 'w')

        f.write(doc.toprettyxml())

        f.close()



    def loadChannelSettings(self, fileName):

        '''
        load attribute settings from a file so rig rebuilds the same exact way
        @param fileName: the file to load from
        '''

        attrsFile = xd.parse(fileName)

        theObjects = attrsFile.getElementsByTagName('controls')

        objectNodes = theObjects[0].childNodes

        #if self.debug: print objectNodes
            
        for obj in objectNodes:
            if obj.nodeName != '#text':
                channelSetting = obj.childNodes
                for cs in channelSetting:
                    if cs.nodeName != '#text':
                        attrItems = cs.attributes.items()
                        if cmds.objExists(obj.nodeName):
                            if cs.nodeName == 'locked':
                                for ai in attrItems:
                                    cmds.setAttr(obj.nodeName+'.'+str(ai[0]), l = True)

                            if cs.nodeName == 'unLocked':
                                for ai in attrItems:
                                    cmds.setAttr(obj.nodeName+'.'+str(ai[0]), l = False)

                            if cs.nodeName == 'keyable':
                                for ai in attrItems:
                                    cmds.setAttr(obj.nodeName+'.'+str(ai[0]), k = True)

                            if cs.nodeName == 'nonKeyable':
                                for ai in attrItems:
                                    cmds.setAttr(obj.nodeName+'.'+str(ai[0]), k = False)

                        else:
                            log.warning('Skipping, Object not found :\n%s' % obj.nodeName)

    
    #started as a general idea, but maight have to be too specific to work with anything except the neckline fixer
    def transferAllIncomingConnections(self, fromObj, toObj):

        '''
        transfers all incoming connections from one node to another
        @param fromObj: Really?
        @param toObj: Derp
        '''

        if cmds.objectType(fromObj) == 'transform':
            fromObj = cmds.listRelatives(fromObj,s=True)[0]

        if cmds.objectType(toObj) == 'transform':
            toObj = cmds.listRelatives(toObj,s=True)[0]

        sources = cmds.listConnections(fromObj, s=True, p=True)
        for sc in sources:
            destinations = cmds.listConnections(sc, d=True, p=True)
            for dest in destinations:
                if fromObj in dest:
                    if 'dagSetMembers' not in sc:
                        if cmds.objectType(sc) != 'skinCluster':

                            cmds.connectAttr(sc, dest.replace(fromObj, toObj), f=True)

    def isNumber(self, s):

        '''
        returns if its a number
        @param s: the variable to test
        '''

        try:
            float(s)
            return True
        except ValueError:
            return False


    def setEnumAttrWithString(self, node,attr,value):
        #print node,attr,value
        enumString=cmds.attributeQuery(attr,node=node, listEnum=1)[0]
        #print 'enumString', enumString
        enumList=enumString.split(":")
        #print enumList
        if value in enumList:
            index=enumList.index(value)
            cmds.setAttr(node+"."+attr,index)
        else:
            print(node+"."+attr+' does not contain the value ', value)


    """
    adds an attr to a compound attribute
    need to add more options for recreating the attrs with more data
    """
    def addToCompoundAttr(self, node, compoundAttr, newAttr):
    
        if not cmds.objExists(node+'.'+compoundAttr):
            cmds.addAttr(node,longName=compoundAttr, numberOfChildren = 1, attributeType = 'compound')
            if not cmds.objExists(node+'.'+newAttr):
                cmds.addAttr(node, ln=newAttr, parent = compoundAttr, at="double", dv = 0)
            else:
                incoming = cmds.listConnections(node+'.'+newAttr, s=1, d=0, p=1)
                outgoing = cmds.listConnections(node+'.'+newAttr, s=0, d=1, p=1)
                cmds.deleteAttr(node+'.'+newAttr)
                cmds.addAttr(node, ln=newAttr, parent = compoundAttr, at="double", dv = 0)

                if incoming is not None:
                    for inc in incoming:
                        cmds.connectAttr(inc, node+'.'+newAttr, f=1)
                        
                if outgoing is not None:
                    for outc in outgoing:
                        cmds.connectAttr(node+'.'+newAttr, outc, f=1)

        else:
            numberOfChildren = cmds.addAttr(node+'.'+compoundAttr, q=1, nc=1)
            childAttrs = cmds.attributeQuery(compoundAttr,n=node, lc=1)
            
            childCons = dict()
            for ca in childAttrs:
                incoming = cmds.listConnections(node+'.'+ca, s=1, d=0, p=1)
                outgoing = cmds.listConnections(node+'.'+ca, s=0, d=1, p=1)
                childCons[ca] = incoming,outgoing
            
            cmds.deleteAttr(node+'.'+compoundAttr)
            
            numberOfChildren +=1
            
            cmds.addAttr(node,longName=compoundAttr, numberOfChildren = numberOfChildren, attributeType = 'compound')
            
            for shape in childCons.keys():
                cmds.addAttr(node, ln=shape, parent = compoundAttr, at="double", dv = 0)
                
            if not cmds.objExists(node+'.'+newAttr):
                cmds.addAttr(node, ln=newAttr, parent = compoundAttr, at="double", dv = 0)
            else:
                incoming = cmds.listConnections(node+'.'+newAttr, s=1, d=0, p=1)
                outgoing = cmds.listConnections(node+'.'+newAttr, s=0, d=1, p=1)
                cmds.deleteAttr(node+'.'+newAttr)
                cmds.addAttr(node, ln=newAttr, parent = compoundAttr, at="double", dv = 0)

                if incoming is not None:
                    for inc in incoming:
                        cmds.connectAttr(inc, node+'.'+newAttr, f=1)
                        
                if outgoing is not None:
                    for outc in outgoing:
                        cmds.connectAttr(node+'.'+newAttr, outc, f=1)
            
            for shape in childCons.keys():
                inCon = childCons.get(shape)[0]
                outCon = childCons.get(shape)[1]
            
                if inCon is not None:
                    for inc in inCon:
                        cmds.connectAttr(inc, node+'.'+shape, f=1)
                        
                if outCon is not None:
                    for outc in outCon:
                        cmds.connectAttr(node+'.'+shape, outc, f=1)


    def getSelectedChannels(self):
        channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;') #fetch maya's main channelbox
        attrs = cmds.channelBox(channelBox, q=True, sma=True)
        if not attrs:
            return []
        return attrs