import rgTools.rgSettings as rigset
import rgTools.returnObjectWithAttr as roa

import maya.cmds as cmds

reload(rigset)
reload(roa)

class mirrorSystem(object):
    
    def __init__(self):
        
        self.__settings = rigset.rgSettings()
        self.__attrFinder = roa.returnObjectWithAttr()

    def returnMirrorPartner(self, obj):

        if not cmds.objExists(obj+'.mirrorPartner'):
            return self.connectMirrorSide(obj)
        else:
            mirrorObj = cmds.listConnections(obj+'.mirrorPartner')
            if len(mirrorObj) > 0:
                return mirrorObj[0]

    def returnMirrorObject(self, obj):

        allSides = [['Left','Right'], ['left','right'], ['Lf','Rt'], ['l_','r_'], ['Lt','Rt']]

        for sides in allSides:
            if sides[0] in obj:
                if cmds.objExists(obj.replace(sides[0], sides[1])):
                    return obj.replace(sides[0], sides[1])
                if obj.startswith(sides[0]):
                    return sides[1]+obj[len(sides[0]):]

        return None

    def connectMirrorSide(self, obj):

        mirrorObject = self.returnMirrorObject(obj)
        if mirrorObject is not None:
            if not cmds.objExists(obj+'.mirrorPartner'):
                cmds.addAttr(obj, ln='mirrorPartner',at="message")
            if not cmds.objExists(mirrorObject+'.mirrorPartner'):
                cmds.addAttr(mirrorObject, ln='mirrorPartner',at="message")

            cmds.connectAttr(obj+'.mirrorPartner', mirrorObject+'.mirrorPartner', f=True)

            return mirrorObject
        else:
            #cmds.error('No mirror partner found', obj, mirrorObject)
            return None

    def addMirrorAttrs(self, fromSide = 'left'):

        allCtrls = self.__attrFinder.all(self.__settings.ctrlMadeAttr, '*')

        for ctrl in allCtrls:
            ctrlSide = self.returnSide(ctrl)

            if ctrlSide == fromSide:
                mirrorCtrl = self.returnMirrorObject(ctrl)
                #print 'mirrorCtrl ', ctrl, mirrorCtrl

                if mirrorCtrl is None:
                    print 'No mirror for, ', ctrl, ', skipping'
                else:
                    if cmds.objExists(mirrorCtrl):
                        
                        self.connectMirrorSide(ctrl)
                        
                        if not cmds.objExists(ctrl+'.mirrorSide'):
                            cmds.addAttr(ctrl, ln='mirrorSide', at="enum", en = "Centre:Left:Right" )
                        if not cmds.objExists(mirrorCtrl+'.mirrorSide'):
                            cmds.addAttr(mirrorCtrl, ln='mirrorSide', at="enum", en = "Centre:Left:Right" )

                        if not cmds.objExists(ctrl+'.side'):
                            cmds.addAttr(ctrl, ln='side', at="enum", en = "Center:Left:Right:None" )
                        if not cmds.objExists(mirrorCtrl+'.side'):
                            cmds.addAttr(mirrorCtrl, ln='side', at="enum", en = "Center:Left:Right:None" )

                        if not cmds.objExists(ctrl+'.mirrorIndex'):
                            cmds.addAttr(ctrl, ln= 'mirrorIndex', at="long")
                        if not cmds.objExists(mirrorCtrl+'.mirrorIndex'):
                            cmds.addAttr(mirrorCtrl, ln= 'mirrorIndex', at="long")

                        if not cmds.objExists(ctrl+'.mirrorAxis'):
                            cmds.addAttr(ctrl, ln= 'mirrorAxis', dt="string")
                        if not cmds.objExists(mirrorCtrl+'.mirrorAxis'):
                            cmds.addAttr(mirrorCtrl, ln= 'mirrorAxis', dt="string")

                        if not cmds.objExists(ctrl+'.mirrorAxisOffset'):
                            cmds.addAttr(ctrl, ln= 'mirrorAxisOffset', dt="string")
                        if not cmds.objExists(mirrorCtrl+'.mirrorAxisOffset'):
                            cmds.addAttr(mirrorCtrl, ln= 'mirrorAxisOffset', dt="string")

                        allMi = self.__attrFinder.all('mirrorIndex', '*')

                        highest = -1
                        for mi in allMi:
                            if cmds.getAttr(mi+'.mirrorIndex') > highest:
                                highest = cmds.getAttr(mi+'.mirrorIndex') 
                        highest +=1 

                        cmds.setAttr(ctrl+'.mirrorIndex', highest)
                        cmds.setAttr(mirrorCtrl+'.mirrorIndex', highest)

                        cmds.setAttr(ctrl+'.mirrorSide', 1)
                        cmds.setAttr(mirrorCtrl+'.mirrorSide', 2)

                        cmds.setAttr(ctrl+'.side', 1)
                        cmds.setAttr(mirrorCtrl+'.side', 2)


    def returnSide(self, obj, threshold = 0.01, axis = 'X'):

            if axis == 'X':
                distFromCenter = cmds.xform(obj,q=True,ws=True,t=True)[0]
                if distFromCenter > threshold:
                    return 'left'

                elif distFromCenter < threshold * -1:
                    return 'right'

                elif distFromCenter >= threshold * -1 and distFromCenter <= threshold:
                    return 'center'
