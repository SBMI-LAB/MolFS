# -*- coding: utf-8 -*-

# from MolFS.FileObjects import *
from MolFS.Folder import *
from MolFS.File import *

class IndexFile:
    
    def __init__(self, name):
        
        self.Name = name
        
        self.Root = folder("")
        
        self.Root.Index = self
        
        self.files = []
        
        self.patches = []
        
        self.FSPath = ""
        
        self.IndexPool = folder("")
        
        self.LastId = 0
        
        self.GlobalIndex = None
        
        
    
    
    def addFiles(self, file):
        self.files.append(file)
        
        file.Id = self.LastId
        
        self.LastId += 1
        
        if self.GlobalIndex != None:
            self.GlobalIndex.addFiles(file)
    
    
    def addPatch(self, file, ID):
        
        self.patches.append(file)
        
        file.Id = ID
        
        if self.GlobalIndex != None:
            self.GlobalIndex.addPatch(file, ID)
    
    
    def readFS(self):
        # Read the existing file system
        ... 
        
        
    def saveFS(self):
        # Save the existing file system
        ...
        
    def genDataBlocks(self):
        # Generate the datablocks
        ...
        
    def genIndexFile(self):
        
        filename = self.FSPath + "index.xml"
        self.f = open(filename, "w")
        
        self.tabs = ""
        
        self.writeline("<MolFS system>")
        self.incTab()
        
        
        self.recursiveFolder(self.Root)
        
        self.decTab()
        
        self.writePatches()
        
        self.writeline("</MolFS>")
        self.decParam()
        
        
        
        self.f.close()
        
        self.UpdatePool()
        
    
    def writeline(self, linea):
        
        linea2 = self.tabs + linea + "\n"
        self.f.write( linea2 )
    
    def incTab(self):
        self.tabs = self.tabs + "    "
        

    def decTab( self ):
        
        if len(self.tabs) > 4:
            self.tabs = self.tabs[:-4]
        else:
            self.tabs = ""
        
    
    
    def recursiveFolder(self, folder):
        
        self.writeline("<folder name = '" + folder.Name + "/'>")
        self.incTab()
        
        for inFolder in folder.folders:
            self.recursiveFolder(inFolder)
        
        for file in folder.files:
            self.writeFile(file)
            
            
        
        self.decTab()
        self.writeline("</folder>")
        
    
    def decParam(self):
#        self.writeline("<decP>")
        deP = "<decP>"
        np = len(self.Root.blocks)
        for block in self.Root.blocks:
            nt = block.encodeParam
            if type(nt) == str:
                deP += nt
            else:
                deP += str(nt)
            deP += " "
        
        deP +="</decP>"
        
        self.writeline(deP)
    
    
    def writePatches(self):
        
        if len(self.patches) == 0:
            return
        
        self.writeline("<patches>")
        self.incTab()
        for patch in self.patches:
            self.writeline("<patch id='"+str(patch.Id)+"' name = '"+patch.Name + "'>")
        self.decTab()
        self.writeline("</patches>")
    
    def writeFile(self, file):
        
        self.writeline("<file id = '"+str(file.Id)+"' name = '"+file.Name + "'>")
        self.incTab()
        
        k = 0
        for exten in file.extents:
            pool = exten.pool
            blockin = exten.block_in
            
            offsetin = exten.offset_in
            
            blocks = exten.numblocks
            
            size = exten.size
            
            texto = "<extent number = "+str(k)
            texto += ", pool = " + str(pool)
            texto += ", block_in = " + str(blockin)
            texto += ", offset = " + str(offsetin)
            texto += ", blocks = " + str(blocks)
            texto += ", size = " + str(size)
            texto += " ></extent>"
            
            
            self.writeline(texto)
            k+= 1
        
        
        self.decTab()
        self.writeline("</file>")
        
    
    def UpdatePool(self):
        self.IndexPool.addNewFile ( self.FSPath + "index.xml", "/tmp/index.xml")
        
        self.IndexPool.initPool = 0
        
        self.IndexPool.genBlocks()
        
        
        

