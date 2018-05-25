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
import rgTools.rgSettings as rigset
import rgTools.createMatrixReverse as cmr
import rgTools.attrUtilities as atru

reload(rigset)
reload(rmeta)
reload(cmr)
reload(atru)

class guiLoader(object):

    def __init__(self):
        print 'loaded gui tools'
        self.__meta = rmeta.metaSystem()
        self.__settings = rigset.rgSettings()
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
        self.ui.resetPushButton.clicked.connect(self.resetShape)
        self.ui.cancelPushButton.clicked.connect(self.cancelShapeEdit)
        self.ui.createExressionButton.clicked.connect(self.createNewShape)
        self.ui.updateCtrlsButton.clicked.connect(self.updateNewShapeCtrls)

        self.ui.mirrorShapeButton.clicked.connect(self.mirrorShape)

        self.updateUi()

        

        self.ui.show()

        #cmds.animCurveEditor(pnl=self.ui, p=self.ui.animCurveWidget)

    def updateUi(self):
        print 'updating UI'

        self.facialNodes = self.__meta.findMeta(self.__settings.faceNode)
        if len(self.facialNodes) == 0:
            print 'No facial nodes exist in scene'
        else:
            self.updateShapes()
            self.allFaceCtrls = []
            self.allFaceCtrlShapes = []
            print 'self.faceShapes ', self.faceShapes
            for fs in self.faceShapes:
                ctrls = cmds.listConnections(fs+'.ctrls', s=0, d=1)
                print 'ctrls ', ctrls
                if ctrls is not None:
                    self.allFaceCtrls.extend(ctrls)

            print 'Found all ctrls: ', self.allFaceCtrls

            for ctrl in self.allFaceCtrls:
                self.allFaceCtrlShapes.append(cmds.listRelatives(ctrl,shapes=True)[0])

            print 'Found all ctrl shapes: ', self.allFaceCtrlShapes

    def updateControls(self,selected):

        ctrlString = ''
        if isinstance(selected, basestring):
            ctrlString = selected
        else:
            ctrlString = selected.text()

        print 'adding controls ', ctrlString
        self.ui.controlsListWidget.clear()

        theShape = ctrlString
        if self.nameSpaced:
            theShape = self.nameSpace+':'+theShape

        self.ui.controlsListWidget.addItems(cmds.listConnections(theShape+'.ctrls', s=0,d=1))

        if self.ui.autoActivateCheckBox.isChecked():
            self.startEditShape(ctrlString)

    def editShapeButton(self):
        theShape = self.ui.shapesListWidget.selectedItems()[0].text()
        print theShape
        self.updateControls(theShape)
        self.startEditShape(theShape)

    def loadUiWidget(self, parent=None):
        loader = QtUiTools.QUiLoader()
        currentDir = os.path.dirname(__file__)  
        print 'currentDir file: ', currentDir         
        file = QFile(currentDir+"/faceEditor.ui") 
        uifile = QtCore.QFile(file)
        uifile.open(QtCore.QFile.ReadOnly)
        ui = loader.load(uifile, parent)
        uifile.close()
        return ui

    def updateShapes(self):

        self.faceShapes = self.__meta.findMeta(self.__settings.faceShapes)
        print 'found face shapes: ', self.faceShapes
        self.ui.shapesListWidget.clear()

        self.nameSpaced =True
        self.nameSpace = ':'.join(self.faceShapes[0].split(':')[:-1])
        if self.nameSpace == '':
            self.nameSpaced = False

        for idx, fs in enumerate(self.faceShapes):
            if self.nameSpaced:
                fs = fs.replace(self.nameSpace+':' , '')
            self.ui.shapesListWidget.addItem(fs)
            self.ui.shapesListWidget.item(idx).setBackground(Qt.black)
            self.ui.shapesListWidget.item(idx).setForeground(Qt.lightGray)

    def clickedControl(self, ctrlClicked):

        print 'clicked control ', ctrlClicked.text()
        theCtrl = ctrlClicked.text()

        sdks = cmds.listConnections(theCtrl+'.faceShape_'+self.shapeBeingEdited, s=0, d=1)
        print 'sdks ', theCtrl+'.faceShape_'+self.shapeBeingEdited, sdks
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

        

        isSet = cmds.getAttr(self.facialNodes[0]+'.'+self.shapeBeingEdited)
        if isSet:
            #cmds.setAttr(self.facialNodes[0]+'.'+self.shapeBeingEdited, 0)

            self.ui.shapesListWidget.item(shapeIndex).setBackground(Qt.black)
            self.ui.shapesListWidget.item(shapeIndex).setForeground(Qt.lightGray)

            if self.isEditing:
                self.updateShape()

        else:
            for ad in self.faceShapes:
                #cmds.setAttr(self.facialNodes[0]+'.'+ad, 0)
                print ad
                if self.nameSpaced:
                    ad = ad.replace(self.nameSpace+':' , '')

                adIndex = self.indexFromString(ad)
                self.ui.shapesListWidget.item(adIndex).setBackground(Qt.black)
                self.ui.shapesListWidget.item(adIndex).setForeground(Qt.lightGray)

            self.connected = cmds.listConnections(self.facialNodes[0]+'.'+self.shapeBeingEdited, s=1, d=0, p=1)
            print 'self.connected  ', self.connected , self.facialNodes[0]+'.'+self.shapeBeingEdited
            if self.connected:
                print 'disconnecting'
                cmds.disconnectAttr(self.connected[0], self.facialNodes[0]+'.'+self.shapeBeingEdited)

            cmds.setAttr(self.facialNodes[0]+'.'+self.shapeBeingEdited, 1)

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

            theBuf = cmds.listConnections(ctrl+'.addedBufferGroup', s=1, d=0)[0]
            cmds.xform(theBuf ,ws=True,m=(cmds.xform(ctrlLoc,q=True,ws=True,m=True)))

            for axis in ('tx','ty','tz','rx','ry','rz'):
                animCurve = self.returnAnimCurveOfCtrlFromShape(self.facialNodes[0] , self.shapeBeingEdited, theBuf+'.'+axis)

                newValue = cmds.getAttr(theBuf+'.'+axis)

                if len(animCurve) == 0:
                    sdkMade = cmds.setDrivenKeyframe(theBuf,at = axis, cd = self.facialNodes[0]+'.'+self.shapeBeingEdited, dv = 0 , v = 0)
                    sdkMade = cmds.setDrivenKeyframe(theBuf,at = axis, cd = self.facialNodes[0]+'.'+self.shapeBeingEdited, dv = 0 , v = newValue)#, itt = inTangentTypeAttr, ott = outTangentTypeAttr)

                else:
                    cmds.keyframe(animCurve, e = 1, iub = True, a = True, o = 'move', vc = newValue, index = (1,1))

        #animCurves = cmds.listConnections( self.facialNodes[0]+'.'+self.shapeBeingEdited, s=0, d=1 )
        #for ac in animCurves:
            #cmds.keyframe(ac, e = 1, iub = True, r = True, o = 'over', t = 1)

        #if self.ui.autoHideCheckBox.isChecked():
            #for cis in self.allFaceCtrls:
                #cmds.setAttr(cis+'.v', 1)
        cmds.setAttr(self.facialNodes[0]+'.'+self.shapeBeingEdited, 0)

        if self.ui.autoHideCheckBox.isChecked():
            cmds.viewFit( self.allFaceCtrlShapes )

        if self.isMirrored:
            cmds.delete('wsMatrixReverseNodes')
            self.isMirrored = False
            
        cmds.delete(deleteLocs)

        if self.connected:
                cmds.connectAttr(self.connected[0], self.facialNodes[0]+'.'+self.shapeBeingEdited, f=True)

        self.isEditing = False

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

        print shapeName

        if shapeName in self.faceShapes:
            cmds.error('shape already exists, please choose a new name', shapeName)
        else:
            self.ctrlsInNewShape = []
            for index in xrange(self.ui.newShapeCtrlsWidget.count()):
                 self.ctrlsInNewShape.append(self.ui.newShapeCtrlsWidget.item(index).text())

            print shapeName, self.ctrlsInNewShape, self.facialNodes[0]

            #cmds.addAttr(self.facialNodes[0], ln=shapeName, parent = 'driverValues', at="double", dv = 0) # parent = 'driverValues',
            self.__atu.addToCompoundAttr(self.facialNodes[0], 'driverValues', shapeName)

            #get animation data


            for ctrl in self.ctrlsInNewShape:

                buffGrp = cmds.listConnections(ctrl+'.addedBufferGroup', s=1,d=0 )
                rots = cmds.getAttr(ctrl+'.r' )
                trans = cmds.getAttr(ctrl+'.t' )

                #set 0 keyframe
                cmds.setDrivenKeyframe(buffGrp[0],at = 'tx', cd = self.facialNodes[0]+'.'+shapeName, dv = 0, v = 0)
                cmds.setDrivenKeyframe(buffGrp[0],at = 'ty', cd = self.facialNodes[0]+'.'+shapeName, dv = 0, v = 0)
                cmds.setDrivenKeyframe(buffGrp[0],at = 'tz', cd = self.facialNodes[0]+'.'+shapeName, dv = 0, v = 0)
                cmds.setDrivenKeyframe(buffGrp[0],at = 'rx', cd = self.facialNodes[0]+'.'+shapeName, dv = 0, v = 0)
                cmds.setDrivenKeyframe(buffGrp[0],at = 'ry', cd = self.facialNodes[0]+'.'+shapeName, dv = 0, v = 0)
                cmds.setDrivenKeyframe(buffGrp[0],at = 'rz', cd = self.facialNodes[0]+'.'+shapeName, dv = 0, v = 0)

                print trans
                cmds.setDrivenKeyframe(buffGrp[0],at = 'tx', cd = self.facialNodes[0]+'.'+shapeName, dv = 1, v = trans[0][0])
                cmds.setDrivenKeyframe(buffGrp[0],at = 'ty', cd = self.facialNodes[0]+'.'+shapeName, dv = 1, v = trans[0][1])
                cmds.setDrivenKeyframe(buffGrp[0],at = 'tz', cd = self.facialNodes[0]+'.'+shapeName, dv = 1, v = trans[0][2])
                cmds.setDrivenKeyframe(buffGrp[0],at = 'rx', cd = self.facialNodes[0]+'.'+shapeName, dv = 1, v = rots[0][0])
                cmds.setDrivenKeyframe(buffGrp[0],at = 'ry', cd = self.facialNodes[0]+'.'+shapeName, dv = 1, v = rots[0][1])
                cmds.setDrivenKeyframe(buffGrp[0],at = 'rz', cd = self.facialNodes[0]+'.'+shapeName, dv = 1, v = rots[0][2])

                cmds.setAttr(ctrl+'.tx', 0)
                cmds.setAttr(ctrl+'.ty', 0)
                cmds.setAttr(ctrl+'.tz', 0)
                cmds.setAttr(ctrl+'.rx', 0)
                cmds.setAttr(ctrl+'.ry', 0)
                cmds.setAttr(ctrl+'.rz', 0)


        self.updateNewShapeCtrls()

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