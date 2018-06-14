"""
A Class to make dealing with files easier, aimed at our tools
Autho: John Riggs
"""
import rgTools.rgSettings as rigset
reload(rigset)

import os
import glob
from os import path
import maya.cmds as cmds

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class fileUtils(object):
    
    def __init__(self):
        self.__settings = rigset.rgSettings()
        #resources_dir = path.join(path.dirname(__file__), 'resources')
        #self.__controlLocation = path.join(path.dirname(__file__), 'ctrlShapes')
        self.__controlLocation = self.__settings.controlLocation
        self.__ikScriptsLocation = self.__settings.ikSystems #path.join(path.dirname(__file__), 'ikSystem')
        self.__ikAutoSetupsLocation = self.__settings.autoSetupsDir #path.join(path.dirname(__file__), 'autoSetup')
        self.__rootLocation =  self.__settings.installLocation #path.join(path.dirname(__file__))
        self.__riggingLocation =  self.__settings.rigBuildScriptsLocation #path.join(path.dirname(__file__))

    def checkOrMakeDirectory(self, theDir):

        d=os.path.dirname(theDir)
        if not os.path.exists(d):
            os.makedirs(d)

        return d


    def returnNewestDir(self, basePath):
    
        result = []
        for d in os.listdir(basePath):
            bd = os.path.join(basePath, d)
            if os.path.isdir(bd): result.append(bd)
        return max(result,key=os.path.getmtime)

    
    def returnFiles(self, directory, extension = []):

        #test for string and make array if it is
        if type(extension) is str:
            extension = [extension]

        allFiles = []

        try:
            for file in os.listdir(directory):
                for ext in extension:
                    if file.endswith("."+ext):
                        allFiles.append(file)
        except:
            pass

        return allFiles

    #this returns all files in the directory and sub directories
    def returnAllFiles(self, directory, extension = []):

        if type(extension) is str:
            extension = [extension]

        allFiles = []
        for path, subdirs, files in os.walk(directory):
            for name in files:
                for ext in extension:
                    if name.endswith(ext):
                        allFiles.append(os.path.join(path, name))

        return allFiles

    def returnNewestVersion(self, directory, extension = []):
        '''
        returns the file with the newest version number
        @param directory: the directory
        @param extension: the file extension to be checked
        '''
        print directory
        if os.path.isdir(directory):
            if os.listdir(directory) == []:
                return None
            else:
                return max(self.returnFiles(directory, extension))
        else:
            cmds.warning('No directory ', directory)

    def returnNewestDate(self, directory, extension):
        '''
        returns the file with the newest date
        @param directory: the directory
        @param extension: the file extension to be checked
        '''
        theDir = directory+'/*.'+extension
        if not os.path.isdir(directory):
            os.makedirs(directory)

        if os.listdir(directory) == []:
            return None
        else:
            return max(glob.iglob(theDir), key=os.path.getctime)


    def bumpFileVersion(self, directory, extension):
        
        newestFile = self.returnNewestDate(directory, extension)
        print 'newestFile ', newestFile
        if newestFile is None:
            newName = directory+'/'+directory.split('/')[:-4][-1]+'_'+directory.split('/')[-1]+'.01.ma'
            cmds.warning('No files in that directory returning a new name: ', newName)

            return newName

        else:
            splited = newestFile.split('.')
            #print 'splited '+str(len(splited))
            if len(splited) == 2:
                return splited[0]+'.01.'+splited[1]
            splited[-2] = str(int(splited[-2])+1)
            return '.'.join(splited)

    def returnCtrlShapes(self):

        shapes = self.returnFiles(self.__controlLocation, ['ctrlShape'])
        return [x.partition('.')[0] for x in shapes]

    def returnSystem(self, theType):

        returnSystems = []
        theSystems = []
        print self.__riggingLocation+'/'+theType
        if theType != 'controlShape':
            if theType == 'ikAddOns':
                theSystems = self.returnFiles(self.__riggingLocation+'/ikSystems/'+theType, ['py'])
            else:
                theSystems = self.returnFiles(self.__riggingLocation+'/'+theType, ['py'])
        else:
            theSystems = self.returnFiles(self.__riggingLocation+'/'+theType, ['ctrlShape'])

        for ts in theSystems:
            if ts.startswith('__') is not True:
                #add methods search here
                returnSystems.append(ts.partition('.')[0])

        return returnSystems

    def returnSubdirectories(self, dir):
        if os.path.exists(dir):
            return [name for name in os.listdir(dir)
                    if os.path.isdir(os.path.join(dir, name))]

    def returnInfsFromWeightsFile(self, filename):

        try:
            fRead = open(filename,'rb')
        except IOError:
           raise statusError('file '+ `filename` +'does not exist')

        jntFound = 0
        for line in fRead:
            if line.find('# Joint list') != -1: jntFound = 1; break;
        if jntFound == 0: cmds.error("No file or Invalid format")
        # make a list of joint chain
        jntList = fRead.next().split()
        for line in fRead:
            if line.find('# Joint list ends') != -1:  break

        return jntList

    def returnVertCountFromWeightsFile(self, filename):

        try:
            fRead = open(filename,'rb')
        except IOError:
           raise statusError('file '+ `filename` +'does not exist')

        vertsFound = 0
        for line in fRead:
            if line.startswith('['):
                vertsFound += 1
                
        return vertsFound
        
    def replaceInFile(self, fileIn, old, replaceWith):

        f = open(fileIn,'r')
        filedata = f.read()
        f.close()

        newdata = filedata.replace(old, replaceWith)

        f = open(fileIn,'w')
        f.write(newdata)
        f.close()
