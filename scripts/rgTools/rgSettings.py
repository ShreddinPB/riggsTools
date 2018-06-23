import maya.cmds as cmds

class rgSettings(object):
    
    def __init__(self):


        #file extensions
        self.ctrlFileExtension = 'ctrlShape'

        #directories
        self.installLocation = __file__.rpartition('\\')[0]+'/' #'C:/Users/jriggs/cloudDrives/Dropbox/riggingToolsetPython/scripts/rtsp/'
        #print 'Installed in: ', self.installLocation
        #temp for now till I have time to figure out a better way to do this.
        self.rigBuildScriptsLocation = 'D:/cloudDrives/DropBox/Dropbox (Personal)/riggingToolsetPython/scripts/rtsp/'
        #self.rigBuildScriptsLocation = 'C:/Users/jriggs/Dropbox (Personal)/riggingToolsetPython/scripts/rtsp/'
        #print '#### INITIALIZING RTSP FROM: ',self.installLocation
        self.autoSetupsDir = self.installLocation+'autoSetups'
        self.controlLocation = self.installLocation+'controlShape/'
        self.ikSystems = self.installLocation+'ikSystems/'

        #naming
        self.theSwitchControl = "theSwitchControl"
        self.pvSpaceAttrName = "poleVectorSpace"
        self.ikSpaceAttrName = "ikSpace"
        self.pvSwitchAttr = 'pvParents'
        self.ikPrefix = "Ik"
        self.fkPrefix = "Fk"
        self.worldSpacePoleVectorsGrp = 'worldSpacePoleVectors_Grp'
        self.worldSpaceIkGrp = 'worldSpaceIk_Grp'
        self.worldSpaceIkDistanceGrp = 'worldSpaceIkDistance_Grp'
        self.ctrlExtension = 'CTRL'
        self.ctrlMadeAttr = 'controlMade'
        
        #meta naming
        self.setupData = 'setupData'
        self.jointsInSystem = 'jointsInSystem'
        self.faceShapes = 'faceShape'
        self.driverValues = 'driverValues'
        self.faceNode = 'face'
        
        #attr names
        self.fkIkAttrName = "fkIk"
        self.ikTrnControlName = "ikTrnControl"
        self.shaperCtrlVis = 'showShaperControls'
        self.mocapConnect = 'mocapConnect'
        self.mocapConnectTo = 'mocapConnectTo'

        #colors
        self.ikCenterColor = 17
        self.ikCenterSecondaryColor = 25
        self.fkCenterColor = 14
        self.fkCenterSecondaryColor = 26

        #rig building
        self.debug = True

        self.doPostNaming = False

        self.downAxis = 'x'
        
        self.allSides = [['Left','Right'], ['left','right'], ['Lf','Rt'], ['l_','r_'], ['Lt','Rt']]

        self.defaultDownAxis = 'x'
        
        #attributes
        self.enums = ['autoSetups', 'ikSystems', 'ikAddOns', 'dynamicSetups', 'deformerSetups', 'muscleSetups', 'poseSetups', 'controlShape', 'proxyShape', 'mocapConstraints', 'flipJointAxis', 'rigJointType', 'buildAxis']
        self.booleans = ['animation', 'deformer', 'ikAttachPoint', 'pvSpaceAttach']
        self.strings = ['setupOptions','poseOptions', 'mocapConOptions', 'deformerOptions', 'reparent', 'visGroup', 'renameCtrl']
        self.mocapConnectOptions = "None:both:translate:rotate:parent"

        #default shapes
        self.pvShape = "snow"
        self.cameraShape = "camera"
        self.shaper = 'spike'
        self.head = 'circle'
        self.neck = 'octagon'
        self.rootOffset = 'squareRoundedCorners'

        #meta
        self.pvAttr = 'thePv'
        self.ctrlAttr = 'ctrls'
        self.ctrlOnObject = self.setupData+'_'+self.ctrlAttr