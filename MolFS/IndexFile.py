# -*- coding: utf-8 -*-

from Folder import *
from File import *
from Extent import *
from Binary import *

import os

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
        
        self.SessionNumber = 0
        
        self.FS = None
        
        
    
    
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
        
        #self.writeline("<MolFS system>")
        #self.incTab()
        
        
        self.recursiveFolder(self.Root)
        
        #self.decTab()
        
        self.writePatches()
        
        #self.writeline("</MolFS>")
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
#        self.incTab()
        
        for inFolder in folder.folders:
            self.recursiveFolder(inFolder)
        
        for file in folder.files:
            self.writeFile(file)
            
            
        
#        self.decTab()
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
        
        #self.writeline("<patches>")
        #self.incTab()
        for patch in self.patches:
            self.writeline("<patch id='"+str(patch.Id)+"' name = '"+patch.Name + "'>")
            k = 0
            for exten in patch.extents:
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
            self.writeline("</patch>")
        #self.decTab()
        #self.writeline("</patches>")
    
    def writeFile(self, file):
        
        self.writeline("<file id = '"+str(file.Id)+"' name = '"+file.Name + "'>")
        #self.incTab()
        
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
        
        
        #self.decTab()
        self.writeline("</file>")
        
    
    def UpdatePool(self):
        self.IndexPool.addNewFile ( self.FSPath + "index.xml", "/tmp/index.xml")
        
        self.IndexPool.initPool = 0
        
        self.IndexPool.lastBlock =  self.SessionNumber
        
        self.IndexPool.setFS(self.FS)
        
        self.IndexPool.genBlocks()
        
        
    def lineparser(self, line):
        line = line.replace("</","end-")
        line = line.replace("<","")
        line = line.replace(">","")
        line = line.replace("\n","")
        
        line2 = line.split(" ")
        
        Base = ""
        
        Base = line2[0]
        
        Param = []
        Values = []
        
        for k in range(1,len(line2)):
            if line2[k] == "=":
                Param.append(line2[k-1])
                Values.append(line2[k+1].replace(",","").replace("'",""))
            elif "=" in line2[k]:
                linen = line2[k].split("=")
                Param.append(linen[0])
                Values.append(linen[-1].replace(",","").replace("'",""))
                
                
            
                
        return Base, Param, Values
            
            
        
    
    def parseIndex(self, pathbin):
        ### Takes the binary output from the pool
        ## And reconstruct the index file
        filename = self.FSPath + "index.xml"
        
        content = binaryRead(pathbin)
        # search for the flags
        initFlag = str.encode( "--Init--MolFS--")
        endFlag =  str.encode("--MolFS--EOF--")
        
        sif = content.find(initFlag)
        sef = content.find(endFlag) - len(endFlag)-10
        if sif > -1:
            content = content[sif + len(initFlag) :]
        if sef > -1:
            content = content[:sef]
            
        binaryWrite(content, filename)
        
        
        
    def reloadIndex(self):
        print("Reading index file")
        filename = self.FSPath + "index.xml"
        
        CurrentFolder = self.Root
        
        Level = 0
        FolderLevel = []
        FolderLevel.append(CurrentFolder)
        
        CurrentFile = None
        FileSize = 0
        
        if os.path.exists(filename):
            print("Index file available")
            indexfile = open(filename,'r')
            Lines = indexfile.readlines()
            
            for line in Lines:
                
                Base, Param, Values = self.lineparser(line)
                
                if Base == "folder":
                    if Param[0] == "name":
                        fname = Values[0].replace("/","")
                        if fname != "":
                            Level += 1
                            nfolder = folder(fname)
                            CurrentFolder.addFolder(nfolder)
#                            CurrentFolder = CurrentFolder.getFolder(fname)
                            CurrentFolder = nfolder
                            FolderLevel.append(CurrentFolder)
                
                if Base == "file":
                    idnumber = 0
                    fname = ""
                    for k in range(len(Param)):
                        if Param[k] == "id":
                            print(Values[k])
                            idnumber = int(Values[k])
                        if Param[k] == "name":
                            fname = Values[k]
                    
                    CurrentFile = files(fname)
                    CurrentFile.Id = idnumber
                    CurrentFile.InternalPath = os.path.join( CurrentFolder.InternalPath, fname)
                    
                    CurrentFolder.addFile(CurrentFile)
                    print("Adding file")
                    FileSize = 0
                    
                if Base == "patch":
                    idnumber = 0
                    fname = ""
                    for k in range(len(Param)):
                        if Param[k] == "id":
                            print(Values[k])
                            idnumber = int(Values[k])
                        if Param[k] == "name":
                            fname = Values[k]
                    
                    CurrentFile = files(fname)
                    CurrentFile.Id = idnumber
                    
                    CurrentFolder.addPatch(CurrentFile, idnumber)
                    CurrentFile.InternalPath = os.path.join( CurrentFolder.InternalPath, fname)
                    print("Adding patch ", fname, idnumber)
                    print(line)
                    FileSize = 0
                    
                if Base == "extent":
                    NExt = extent()
                    NExt.FS = self.FS
                    enumber = 0
                    epool = 0
                    eblockin = 0
                    eoffset = 0
                    eblocks = 0
                    esize = 0
                    
                    for k in range(len(Param)):
                       
                        if Param[k] == "number":
                            enumber = int(Values[k])
                        if Param[k] == "pool":
                            epool = int(Values[k])
                        if Param[k] == "block_in":
                            eblockin = int(Values[k])
                        if Param[k] == "offset":
                            eoffset = int(Values[k])
                        if Param[k] == "blocks":
                            eblocks = int (Values[k])
                        if Param[k] == "size":
                            esize = int(Values[k])
                    
                    NExt.numblocks = eblocks
                    NExt.pool = epool
                    NExt.block_in = eblockin
                    NExt.size = esize
                    NExt.offset_in = eoffset
                    
                    print("Extend params", epool, eblockin, esize)
                    print(line)
                    
                    if CurrentFile != None:
                        CurrentFile.extents.append(NExt)
                        NExt.reloadBlocks(self.Root)
                    
                
                if Base == "end-folder" and Level > 0:
                    # go up one level
                    FolderLevel.pop(-1)
                    CurrentFolder = FolderLevel[-1]
                    Level = Level - 1
                    
                if "decP" in line:
                    ### Decoding parameters for the blocks
                    print(line)
                    nline = line.replace("<decP>","").replace("</decP>","").replace("\n","")
                    npar = nline.split(" ")
                    
                    
                    
                    if len(npar) >= len(self.Root.blocks):
                        print("Block count matches")
                        for k in range(len(self.Root.blocks)):
                            
                            vpar = npar[k]
                            
                            try:
                                vpar=int(vpar)
                            except:
                                ...
                            
                            self.Root.blocks[k].encodeParam = vpar
                            
                            
                    
                    
                    
                    
                        
                            
                            
                        
                    
                
            
        
        
        
        
        
        

