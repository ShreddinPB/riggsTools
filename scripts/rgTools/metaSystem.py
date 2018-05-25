import rgTools.rgSettings as rigset

import maya.cmds as cmds

reload(rigset)

class metaSystem(object):
    
    def __init__(self):
        
        self.__settings = rigset.rgSettings()

    def connectToSystem(self, setupDataNode, objectToConnect, attrToConnectTo, objectAttr = 'setupData', multiAttr = False):

        if cmds.objExists(setupDataNode):

            if cmds.objExists(setupDataNode+"."+attrToConnectTo) is False:
                cmds.addAttr(setupDataNode, ln= attrToConnectTo, at="message" )
            #print 'attemptoing ', objectToConnect
            if cmds.objExists(objectToConnect+"."+objectAttr) is False:
                cmds.addAttr(objectToConnect, ln= objectAttr, at="message" , multi = multiAttr )
            alreadyConnected = cmds.listConnections(objectToConnect+'.'+objectAttr,s=1,d=0)
            if alreadyConnected is None:
                cmds.connectAttr(setupDataNode+'.'+attrToConnectTo, objectToConnect+'.'+objectAttr, f=True)
            else:
                if setupDataNode not in alreadyConnected:
                    cmds.connectAttr(setupDataNode+'.'+attrToConnectTo, objectToConnect+'.'+objectAttr, f=True)

        else:
            cmds.error('setupData node does not exist')

    def addSystemTag(self, setupDataNode, tagName = None):

        cmds.addAttr(setupDataNode, ln= 'system', dt="string" )
        if tagName is not None:
            cmds.setAttr(setupDataNode+".system", tagName, type="string")

    def addMetaNode(self, name = None, system = 'root'):

        setupDataName = 'setupData'

        if name is not None:
            setupDataName = name + '_setupData'
            if system == 'faceShape':
                setupDataName = name

        setupDataNode = cmds.createNode('network',  n = setupDataName)
        cmds.addAttr(setupDataNode, ln= self.__settings.setupData, dt="string" )
        #cmds.setAttr(setupDataNode+"."+self.__settings.setupData, system, type="string")

        self.addSystemTag(setupDataNode, system)

        return setupDataNode

    def returnMeta(self, node, root = False):

        setupDataNode = cmds.listConnections(node+'.'+self.__settings.setupData , s=1, d=0)

        if len(setupDataNode) > 0:
            return setupDataNode[0]
        else:
            return None
            

    def findMeta(self, system = 'root'):

        returnNodes = []
        networkNodes = cmds.ls(type='network')

        for node in networkNodes:
            if cmds.objExists(node+'.system'):
                if cmds.getAttr(node+'.system') == system:
                    returnNodes.append(node)

        return returnNodes