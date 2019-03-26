import os
from shiboken2 import wrapInstance
import maya.OpenMayaUI as OpenMayaUI
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance 
from PySide2 import QtCore, QtGui, QtUiTools

import maya.cmds as cmds

import rgTools.metaSystem as rmeta
import rgTools.rgSettings as rgset
import rgTools.createMatrixReverse as cmr
import rgTools.attrUtilities as atru

import rgTools.insertBufferGroup as ibg

reload(rgset)
reload(rmeta)
reload(cmr)
reload(atru)

class guiLoader(object):

    def __init__(self):
        print 'loaded gui tools'
        self.__meta = rmeta.metaSystem()
        self.__rgSettings = rgset.rgSettings()
        self.__atu = atru.attrUtilities()

        self.isMirrored = False

    def initUI(self):        
        loader = QUiLoader()        
        currentDir = os.path.dirname(__file__)  
        print 'currentDir file: ', currentDir         
        file = QFile(currentDir+"/faceEditor.ui")     
        print 'Loading file: ', file   
        file.open(QFile.ReadOnly)        
        self.ui = loader.load(file, parentWidget=None)   
        file.close()

        self.ui.actionUpdate_Shape_List.triggered.connect(self.updateShapes)

        self.ui.shapesListWidget.itemActivated.connect(self.updateControls)
        self.ui.controlsListWidget.itemActivated.connect(self.clickedControl)

        self.ui.editShapeButton.clicked.connect(self.editShapeButton)
        self.ui.updatePushButton.clicked.connect(self.updateShape)
        self.ui.addSelectedControlsButton.clicked.connect(self.addSelectedControlsToShapeGui)
        self.ui.resetPushButton.clicked.connect(self.resetShape)
        self.ui.cancelPushButton.clicked.connect(self.cancelShapeEdit)
        self.ui.createExressionButton.clicked.connect(self.createNewShape)
        self.ui.updateCtrlsButton.clicked.connect(self.updateNewShapeCtrls)

        self.ui.mirrorShapeButton.clicked.connect(self.mirrorShape)

        self.ui.loadDriverButton.clicked.connect(self.loadDriverAttr)
        self.ui.createDriverButton.clicked.connect(self.createDriverSdk)

        self.ui.updateMetaNodes.triggered.connect(self.updateMetaNodes)

        self.ui.selectMetaSystem.activated.connect(self.updateUi)
        self.updateUi()
        self.updateMetaNodes()

        self.ui.show()


        #cmds.animCurveEditor(pnl=self.ui, p=self.ui.animCurveWidget)

    def updateUi(self):
        print 'updating UI'

        self.selectedMetaSystem = self.ui.selectMetaSystem.currentText() #self.__meta.findMeta(self.__rgSettings.faceNode)
        #if len(self.facialNodes) == 0:
            #print 'No facial nodes exist in scene'
        #else:
        print 'self.selectedMetaSystem ', self.selectedMetaSystem
        if self.selectedMetaSystem != '':
            self.updateShapes()
            self.allFaceCtrls = []
            self.allFaceCtrlShapes = []
            #print 'self.metaShapes ', self.metaShapes

            if len(self.metaShapes) > 0:
                for fs in self.metaShapes:
                    if cmds.objExists(fs+'.ctrls'):
                        ctrls = cmds.listConnections(fs+'.ctrls', s=0, d=1)
                        #print 'ctrls ', ctrls
                        if ctrls is not None:
                            self.allFaceCtrls.extend(ctrls)

                #print 'Found all ctrls: ', self.allFaceCtrls

            if len(self.allFaceCtrls) > 0:
                for ctrl in self.allFaceCtrls:
                    #print ctrl
                    self.allFaceCtrlShapes.append(cmds.listRelatives(ctrl,shapes=True)[0])

            print 'Found all ctrl shapes: ', self.allFaceCtrlShapes

    def updateMetaNodes(self):

        print 'Updateing meta nodes'
        self.metaNodes = self.__meta.findMeta('face')

        self.ui.selectMetaSystem.clear()
        #self.ui.updateMetaNodes = self.ui.metaModesMenu.addAction('Update')
        #self.ui.updateMetaNodes.triggered.connect(self.updateMetaNodes)

        #if len(self.metaNodes) > 0:
            #self.ui.selectMetaSystem.addItem(self.metaNodes[0])
            #self.ui.metaModesMenu.addAction(self.metaNodes[0], checkable=True, checked = True)

        for mn in self.metaNodes:
            self.ui.selectMetaSystem.addItem(mn, checkable=True)

        self.updateUi()

    def updateControls(self,selected):

        ctrlString = ''
        if isinstance(selected, basestring):
            ctrlString = selected
        else:
            ctrlString = selected.text()

        #print 'adding controls ', ctrlString
        self.ui.controlsListWidget.clear()

        theShape = ctrlString
        if self.nameSpaced:
            theShape = self.nameSpace+':'+theShape

        self.ui.controlsListWidget.addItems(cmds.listConnections(theShape+'.ctrls', s=0,d=1))

        shapeIndex = self.indexFromString(selected.text())

        faceNodeAttr = self.selectedMetaSystem+'.'+selected.text()
        isConnected = cmds.listConnections(faceNodeAttr,s=1,d=0,p=1)
        if isConnected:
            faceNodeAttr = isConnected[0]

        if self.ui.autoActivateCheckBox.isChecked():
            self.startEditShape(ctrlString)

        else:
            if cmds.getAttr(faceNodeAttr):
                cmds.setAttr(faceNodeAttr, 0)
                self.ui.shapesListWidget.item(shapeIndex).setBackground(Qt.black)
                self.ui.shapesListWidget.item(shapeIndex).setForeground(Qt.lightGray)
            else:
                cmds.setAttr(faceNodeAttr, 1)
                self.ui.shapesListWidget.item(shapeIndex).setBackground(Qt.yellow)
                self.ui.shapesListWidget.item(shapeIndex).setForeground(Qt.black)

    def editShapeButton(self):
        theShape = self.ui.shapesListWidget.selectedItems()[0].text()
        #print theShape
        self.updateControls(theShape)
        self.startEditShape(theShape)

    def loadUiWidget(self, parent=None):
        loader = QtUiTools.QUiLoader()
        currentDir = os.path.dirname(__file__)  
        #print 'currentDir file: ', currentDir         
        file = QFile(currentDir+"/faceEditor.ui") 
        uifile = QtCore.QFile(file)
        uifile.open(QtCore.QFile.ReadOnly)
        ui = loader.load(uifile, parent)
        uifile.close()
        return ui

    def updateShapes(self):

        #self.metaShapes = self.__meta.findMeta(self.__rgSettings.sdkShapes)

        if cmds.objExists(self.selectedMetaSystem+'.'+self.__rgSettings.sdkShapes):
            self.metaShapes = cmds.listConnections(self.selectedMetaSystem+'.'+self.__rgSettings.sdkShapes, s=0, d=1)        
            #print 'found face shapes: ', self.metaShapes
            self.ui.shapesListWidget.clear()
            self.ui.allShapesDriverWidget.clear()

            self.nameSpaced =True
            self.nameSpace = ':'.join(self.metaShapes[0].split(':')[:-1])
            if self.nameSpace == '':
                self.nameSpaced = False

            for idx, fs in enumerate(self.metaShapes):
                if self.nameSpaced:
                    fs = fs.replace(self.nameSpace+':' , '')
                self.ui.shapesListWidget.addItem(fs)
                self.ui.shapesListWidget.item(idx).setBackground(Qt.black)
                self.ui.shapesListWidget.item(idx).setForeground(Qt.lightGray)

                self.ui.allShapesDriverWidget.addItem(fs)
                self.ui.allShapesDriverWidget.item(idx).setBackground(Qt.black)
                self.ui.allShapesDriverWidget.item(idx).setForeground(Qt.lightGray)

        else:
            self.metaShapes = []

    def clickedControl(self, ctrlClicked):

        #print 'clicked control ', ctrlClicked.text()
        theCtrl = ctrlClicked.text()

        sdks = cmds.listConnections(theCtrl+'.faceShape_'+self.shapeBeingEdited, s=0, d=1)
        #print 'sdks ', theCtrl+'.faceShape_'+self.shapeBeingEdited, sdks
        self.ui.sdksListWidget.clear()
        self.ui.sdksListWidget.addItems(sdks)


    def startEditShape(self, shapeToEdit):

        self.shapeBeingEdited = shapeToEdit

        if self.nameSpaced:
            self.shapeBeingEdited = self.shapeBeingEdited.replace(self.nameSpace+':' , '')

        self.isEditing = True

        shapeIndex = self.indexFromString(self.shapeBeingEdited)

        self.ctrlsInShape = []
        for index in xrange(self.ui.controlsListWidget.count()):
             self.ctrlsInShape.append(self.ui.controlsListWidget.item(index).text())

        theCtrlsShapes = []
        for css in self.ctrlsInShape:
            theCtrlsShapes.append(cmds.listRelatives(css,shapes=True)[0])

        

        isSet = cmds.getAttr(self.selectedMetaSystem+'.'+self.shapeBeingEdited)
        if isSet:
            #cmds.setAttr(self.selectedMetaSystem+'.'+self.shapeBeingEdited, 0)

            self.ui.shapesListWidget.item(shapeIndex).setBackground(Qt.black)
            self.ui.shapesListWidget.item(shapeIndex).setForeground(Qt.lightGray)

            if self.isEditing:
                self.updateShape()

        else:
            for ad in self.metaShapes:
                #cmds.setAttr(self.selectedMetaSystem+'.'+ad, 0)
                #print ad
                if self.nameSpaced:
                    ad = ad.replace(self.nameSpace+':' , '')

                adIndex = self.indexFromString(ad)
                self.ui.shapesListWidget.item(adIndex).setBackground(Qt.black)
                self.ui.shapesListWidget.item(adIndex).setForeground(Qt.lightGray)

            self.connected = cmds.listConnections(self.selectedMetaSystem+'.'+self.shapeBeingEdited, s=1, d=0, p=1)
            #print 'self.connected  ', self.connected , self.selectedMetaSystem+'.'+self.shapeBeingEdited
            if self.connected:
                #print 'disconnecting'
                cmds.disconnectAttr(self.connected[0], self.selectedMetaSystem+'.'+self.shapeBeingEdited)

            cmds.setAttr(self.selectedMetaSystem+'.'+self.shapeBeingEdited, 1)

            self.ui.shapesListWidget.item(shapeIndex).setBackground(Qt.green)
            self.ui.shapesListWidget.item(shapeIndex).setForeground(Qt.black)

            #if self.ui.autoHideCheckBox.isChecked():
                #for cis in self.allFaceCtrls:
                    #if cis not in self.ctrlsInShape:
                        #cmds.setAttr(cis+'.v', 0)

            #cmds.select(self.ctrlsInShape,r=True)
            if self.ui.autoHideCheckBox.isChecked():
                cmds.viewFit( self.ctrlsInShape )

    def updateShape(self):

        deleteLocs = []
        for ctrl in self.ctrlsInShape:
            ctrlLoc = cmds.spaceLocator(n=ctrl+'_updatedLocation')[0]
            deleteLocs.append(ctrlLoc)
            cmds.xform(ctrlLoc ,ws=True,m=(cmds.xform(ctrl,q=True,ws=True,m=True)))

            cmds.setAttr(ctrl+'.t', 0,0,0,)
            cmds.setAttr(ctrl+'.r', 0,0,0,)

            #make sure the FSDK is in the heirarchy
            fsdk = ctrl+'_FSDK'
            ueTransNode = ctrl+'_unrealTransfer'

            if not cmds.objExists(fsdk):
                if cmds.objExists(ueTransNode):
                    self.buffGrp = ibg.insertBufferGroup(ueTransNode, 'FSDK')
                    self.buffGrp = cmds.rename(self.buffGrp, fsdk)
                else:
                    self.buffGrp = ibg.insertBufferGroup(ctrl, 'FSDK')
                cmds.addAttr(ctrl, ln= 'FsdkBuffer', at="message" )
                cmds.addAttr(self.buffGrp, ln= 'theCtrl', at="message" )
                cmds.connectAttr(fsdk+'.theCtrl', ctrl+'.FsdkBuffer', f=1)
                self.addCtrlToShape(ctrl, self.shapeBeingEdited)
                self.__meta.connectToSystem(self.shapeBeingEdited, ctrl, self.__rgSettings.ctrlAttr, 'sdkCtrl_'+self.shapeBeingEdited)
            else:
                shapeAttrExists = False 
                udAttrs = cmds.listAttr(ctrl, ud=1)
                for ud in udAttrs:
                    if self.shapeBeingEdited in ud:
                        shapeAttrExists = True

                if not shapeAttrExists:
                    self.addCtrlToShape(ctrl, self.shapeBeingEdited)
                    self.__meta.connectToSystem(self.shapeBeingEdited, ctrl, self.__rgSettings.ctrlAttr, 'sdkCtrl_'+self.shapeBeingEdited)

            theBuf = cmds.listConnections(ctrl+'.FsdkBuffer', s=1, d=0)[0]
            cmds.xform(theBuf ,ws=True,m=(cmds.xform(ctrlLoc,q=True,ws=True,m=True)))

            ctrlsAlreadyInShape = cmds.listConnections(self.shapeBeingEdited+'.ctrls', s=0, d=1)
            if ctrl in ctrlsAlreadyInShape:
                for axis in ('tx','ty','tz','rx','ry','rz'):
                    animCurve = self.returnAnimCurveOfCtrlFromShape(self.selectedMetaSystem , self.shapeBeingEdited, theBuf+'.'+axis)

                    newValue = cmds.getAttr(theBuf+'.'+axis)

                    if len(animCurve) == 0:
                        sdkMade = cmds.setDrivenKeyframe(theBuf,at = axis, cd = self.selectedMetaSystem+'.'+self.shapeBeingEdited, dv = 0 , v = 0)
                        sdkMade = cmds.setDrivenKeyframe(theBuf,at = axis, cd = self.selectedMetaSystem+'.'+self.shapeBeingEdited, dv = 0 , v = newValue)#, itt = inTangentTypeAttr, ott = outTangentTypeAttr)

                    else:
                        cmds.keyframe(animCurve, e = 1, iub = True, a = True, o = 'move', vc = newValue, index = (1,1))

                

        #animCurves = cmds.listConnections( self.selectedMetaSystem+'.'+self.shapeBeingEdited, s=0, d=1 )
        #for ac in animCurves:
            #cmds.keyframe(ac, e = 1, iub = True, r = True, o = 'over', t = 1)

        #if self.ui.autoHideCheckBox.isChecked():
            #for cis in self.allFaceCtrls:
                #cmds.setAttr(cis+'.v', 1)
        cmds.setAttr(self.selectedMetaSystem+'.'+self.shapeBeingEdited, 0)

        if self.ui.autoHideCheckBox.isChecked():
            cmds.viewFit( self.allFaceCtrlShapes )

        if self.isMirrored:
            cmds.delete('wsMatrixReverseNodes')
            self.isMirrored = False
            
        cmds.delete(deleteLocs)

        if self.connected:
                cmds.connectAttr(self.connected[0], self.selectedMetaSystem+'.'+self.shapeBeingEdited, f=True)

        self.isEditing = False

    def addSelectedControlsToShapeGui(self):

        if self.isEditing:
            controls = cmds.ls(sl=True)
            controlsInShape = cmds.listConnections(self.shapeBeingEdited+'.ctrls', s=0, d=1)
            for ctrl in controls:
                if ctrl not in controlsInShape:
                    #cmds.connectAttr
                    self.ui.controlsListWidget.addItem(ctrl)

        else:
            cmds.error('Need to be editing a shape')

        self.ctrlsInShape = []
        for index in xrange(self.ui.controlsListWidget.count()):
             self.ctrlsInShape.append(self.ui.controlsListWidget.item(index).text())

    def resetShape(self):

        print 'reset shape'

    def cancelShapeEdit(self):

        print 'cancel shape edit'


    def mirrorShape(self):
        
        print 'Mirroring shape'
        self.isMirrored = True

        leftCtrls = []
        if self.isEditing:

            for ctrl in self.ctrlsInShape:
                if cmds.getAttr(ctrl+'.side') ==  1:
                    leftCtrls.append(ctrl)
        else:
            cmds.error('You are not editing a shape')

        self.locsCreated = []

        if len(leftCtrls) == 0:
            cmds.error('No controls marked on the left side, make sure that the \"side\" attr is set on the controls')
        else:
            for lctrl in leftCtrls:
                rctrl = lctrl[:0] + 'r' + lctrl[1:]
                if cmds.objExists(rctrl):
                    print 'Found ctrl ', rctrl
                    self.locsCreated.append(cmr.createMatrixReverse(lctrl, rctrl, 'X'))

    
    def createNewShape(self):

        shapeName = self.ui.newExpressionTextEdit.toPlainText()

        if shapeName in self.metaShapes:
            cmds.error('shape already exists, please choose a new name', shapeName)
        else:
            self.ctrlsInNewShape = []
            for index in xrange(self.ui.newShapeCtrlsWidget.count()):
                 self.ctrlsInNewShape.append(self.ui.newShapeCtrlsWidget.item(index).text())

            print shapeName, self.ctrlsInNewShape, self.selectedMetaSystem

            #cmds.addAttr(self.selectedMetaSystem, ln=shapeName, parent = 'driverValues', at="double", dv = 0) # parent = 'driverValues',

            #if using compound attr
            self.__atu.addToCompoundAttr(self.selectedMetaSystem, 'driverValues', shapeName)

            #not using compound right now
            #cmds.addAttr(self.selectedMetaSystem, ln=shapeName, at="double", min = 0, dv = 0)
            #cmds.setAttr(self.selectedMetaSystem+'.'+shapeName, 0, e=True, keyable=True)

            print 'Made ', self.selectedMetaSystem, shapeName, cmds.objExists(self.selectedMetaSystem+'.'+shapeName)
            #get animation data


            for ctrl in self.ctrlsInNewShape:
                print 'building sdks'

                self.addCtrlToShape(ctrl, shapeName)
                
        #self.updateNewShapeCtrls()

    def addCtrlToShape(self, ctrl, shapeName):

        rots = cmds.getAttr(ctrl+'.r' )
        trans = cmds.getAttr(ctrl+'.t' )

        #this was '.FsdkBuffer' might need a better way to do this
        if cmds.objExists(ctrl+'.addedBufferGroup'):
            self.buffGrp = cmds.listConnections(ctrl+'.addedBufferGroup', s=1,d=0 )[0]
        else:
            cmds.setAttr(ctrl+'.t', 0,0,0)
            cmds.setAttr(ctrl+'.r', 0,0,0)
            self.buffGrp = ibg.insertBufferGroup(ctrl, 'FSDK')
            #print trans, rots
            cmds.setAttr(ctrl+'.t', trans[0][0],trans[0][1],trans[0][2])
            cmds.setAttr(ctrl+'.r', rots[0][0],rots[0][1],rots[0][2])

        

        #set 0 keyframe
        cmds.setDrivenKeyframe(self.buffGrp,at = 'tx', cd = self.selectedMetaSystem+'.'+shapeName, dv = 0, v = 0)
        cmds.setDrivenKeyframe(self.buffGrp,at = 'ty', cd = self.selectedMetaSystem+'.'+shapeName, dv = 0, v = 0)
        cmds.setDrivenKeyframe(self.buffGrp,at = 'tz', cd = self.selectedMetaSystem+'.'+shapeName, dv = 0, v = 0)
        cmds.setDrivenKeyframe(self.buffGrp,at = 'rx', cd = self.selectedMetaSystem+'.'+shapeName, dv = 0, v = 0)
        cmds.setDrivenKeyframe(self.buffGrp,at = 'ry', cd = self.selectedMetaSystem+'.'+shapeName, dv = 0, v = 0)
        cmds.setDrivenKeyframe(self.buffGrp,at = 'rz', cd = self.selectedMetaSystem+'.'+shapeName, dv = 0, v = 0)

        #print trans
        cmds.setDrivenKeyframe(self.buffGrp,at = 'tx', cd = self.selectedMetaSystem+'.'+shapeName, dv = 1, v = trans[0][0])
        cmds.setDrivenKeyframe(self.buffGrp,at = 'ty', cd = self.selectedMetaSystem+'.'+shapeName, dv = 1, v = trans[0][1])
        cmds.setDrivenKeyframe(self.buffGrp,at = 'tz', cd = self.selectedMetaSystem+'.'+shapeName, dv = 1, v = trans[0][2])
        cmds.setDrivenKeyframe(self.buffGrp,at = 'rx', cd = self.selectedMetaSystem+'.'+shapeName, dv = 1, v = rots[0][0])
        cmds.setDrivenKeyframe(self.buffGrp,at = 'ry', cd = self.selectedMetaSystem+'.'+shapeName, dv = 1, v = rots[0][1])
        cmds.setDrivenKeyframe(self.buffGrp,at = 'rz', cd = self.selectedMetaSystem+'.'+shapeName, dv = 1, v = rots[0][2])

        cmds.setAttr(ctrl+'.tx', 0)
        cmds.setAttr(ctrl+'.ty', 0)
        cmds.setAttr(ctrl+'.tz', 0)
        cmds.setAttr(ctrl+'.rx', 0)
        cmds.setAttr(ctrl+'.ry', 0)
        cmds.setAttr(ctrl+'.rz', 0)

        #print  shapeName, cmds.objExists(shapeName), self.selectedMetaSystem, cmds.objExists(self.selectedMetaSystem)
        if not cmds.objExists(shapeName):
            shapeName = self.__meta.addMetaNode(shapeName,'faceShape')
            print 'shapeName ', shapeName, self.selectedMetaSystem, shapeName, 'shapes', self.__rgSettings.sdkShapes
            self.__meta.connectToSystem(self.selectedMetaSystem, shapeName, self.__rgSettings.sdkShapes, self.__rgSettings.sdkShapes)

        print 'wtf ', shapeName, ctrl, self.__rgSettings.ctrlAttr, 'sdkCtrl_'+shapeName
        self.__meta.connectToSystem(shapeName, ctrl, self.__rgSettings.ctrlAttr, 'sdkCtrl_'+shapeName)

    def updateNewShapeCtrls(self):

        print 'Updating controls'

        self.ui.newShapeCtrlsWidget.clear()

        ctrls = cmds.ls(sl=True)
        self.ui.newShapeCtrlsWidget.addItems(ctrls)

    def indexFromString(self, text):

        indicies = self.ui.shapesListWidget.findItems(text,Qt.MatchExactly)

        if len(indicies) > 0:

            for inx in indicies:
                return self.ui.shapesListWidget.row(inx)


    def returnAnimCurveOfCtrlFromShape(self, faceNode, theShape, theCtrlAndChannel):

        cmds.listConnections(theCtrlAndChannel, s=1,d=0,scn=True)

        fromCtrl = []

        connectionsFromCtrl = cmds.listConnections( theCtrlAndChannel, s=1, d=0 , scn=True)

        if connectionsFromCtrl is None:
            return []
        else:
            if cmds.nodeType(connectionsFromCtrl[0]) == 'blendWeighted':
                fromCtrl = cmds.listConnections( connectionsFromCtrl[0], s=1, d=0 , scn=True)
            else:
                fromCtrl = connectionsFromCtrl
                
            connectionsFromFaceNode = cmds.listConnections( faceNode+'.'+theShape, s=0, d=1 , scn=True)

            theSet = self.intersection(fromCtrl, connectionsFromFaceNode)

            return theSet

    def intersection(self, lst1, lst2):
        return list(set(lst1) & set(lst2))


    def loadDriverAttr(self):

        obj = cmds.ls(sl=True)

        if len(obj) == 0:
            cmds.error('please select an object and a channel in the channel box')
        attrs = self.__atu.getSelectedChannels()

        if len(attrs) == 0:
            #cmds.error('please select an attribute in the channel box')
            print ' No attr selected, will auto generate attr of same name'

            self.ui.driverAttrText.setText(obj[0])

        else:
            self.ui.driverAttrText.setText(obj[0]+'.'+attrs[0])

    def createDriverSdk(self):

        driver = self.ui.driverAttrText.toPlainText()
        theShape = self.ui.allShapesDriverWidget.selectedItems()[0].text()

        splitDrive = driver.split('.')
        if len(splitDrive) == 1:
            cmds.addAttr(driver, ln=theShape, at="double", dv = 0, min = 0, max = 1)
            cmds.setAttr(driver+'.'+theShape,  1, e=True, keyable = True, cb = True)
            driver = driver+'.'+theShape

        driven = self.selectedMetaSystem+'.'+theShape

        driverValue = cmds.getAttr(driver)

        sdkMade = cmds.setDrivenKeyframe(self.selectedMetaSystem,at = theShape, cd = driver, dv = 0 , v = 0)
        sdkMade = cmds.setDrivenKeyframe(self.selectedMetaSystem,at = theShape, cd = driver, dv = driverValue , v = 1)

        cmds.setAttr(driver,  0)

        print driver, driven