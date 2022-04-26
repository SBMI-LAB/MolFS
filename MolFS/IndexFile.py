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
        
        
        self.FSPath = ""
        
        self.IndexPool = folder("")
        
        self.LastId = 0
        
        
    
    
    def addFiles(self, file):
        self.files.append(file)
        
        file.Id = self.LastId
        
        self.LastId += 1
    
    
    
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
        self.writeline("</MolFS>")
        
        
        
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
        
        
        

