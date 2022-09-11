# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
import os 
import shutil
import pathlib
import datetime
import math
import zlib

from File import *


class folder:
    # object structure to define folders
    
    
    def __init__(self, name):
        
        self.Name = name
        
        self.folders = []
        
        self.files = []
        
        self.patches = []
        
        self.status = ""
        
        self.parent = None
        
        self.blocks = []
        
        self.PoolsPath = ""
        
        self.Index = None
        
        self.mDevice = None
        
        self.initPool = 1
        
        self.Pools = 0
        
        self.lastBlock = -1
        
        self.useZlib = False
        
        self.InternalPath = ""
        
        
    
    
    def setUseZlib (self, value):
        self.useZlib = value
        for block in self.blocks:
            block.useZlib = value
            
    
    
    def addFile(self, file):
        self.files.append(file)
        self.Index.addFiles(file)
        
    

    def addPatchFile(self, filename, localpath, fileID):
        npath = os.path.basename(filename) # cut path
        nfile = files(npath)  
        self.patches.append(nfile)
        
        self.Index.addPatch(nfile, fileID)
        
        nfile.addPatchFile(filename, localpath)
        nfile.InternalPath = self.InternalPath +npath
    

    def addNewFile (self, filename, localpath):
        
        npath = os.path.basename(filename) # cut path
        nfile = files(npath)    # file object
        self.addFile(nfile)
        
        nfile.addNewFile(filename, localpath)
        
        nfile.InternalPath = self.InternalPath +npath
        
        
        


    def addNewFile_old (self, filename, localpath):
        shutil.copyfile(filename, localpath )  # create a copy 
        npath = os.path.basename(filename) # cut path
        
        nfile = files(npath)    # file object
        nfile.LocalFile = filename 
        nfile.available = True
        nfile.modified = True # File is modified
        nfile.ModifyDate = nfile.checkModified()
        self.addFile(nfile)
      

    def addFolder(self, folder):
        self.folders.append(folder) 
        folder.parent = self
        folder.Index = self.Index
        folder.mDevice = self.mDevice
        
        folder.InternalPath = self.InternalPath + "/" + folder.Name + "/"

    def getParent(self):
        if self.parent == None:
            return self
        else:
            return self.parent
        
    
    def getFolder (self, name):
        
        # if folder not found, return the same
        selected = self
        
        for k in self.folders:
            if k.Name == name:
                selected = k
                break
        
        return selected
                
        
        
    
    def createFolder(self, name):
        nfolder = folder(name);
        
        self.addFolder(nfolder)
        
        
        
        return nfolder
    
    def recursivePrint(self, path = ""):
        npath = path + self.Name + "/"
        print(npath)
        
        for k in self.files:
            k.dirPrint(path)
            #print( npath + k )
        
        for k in self.folders:
            k.recursivePrint(npath)
            
    
    def readSession(self, path = ""):
        
        self.readAllFiles(path)
        if self.Name != "":
            npath = path + self.Name + "/"
        else:
            npath = path
            
        for k in self.patches:
            k.readFile(npath)
            
            self.ApplyPatch(k, path)
        
    
    def ApplyPatch(self, patch, path ):
        ### The patch file is associated to another file
        ID = patch.Id
        
        ## Identify the target file
        GlobalIndex = self.Index.GlobalIndex
        
        for file in GlobalIndex.files:
            if file.Id == ID:
                ## Proceeding to patch the file
                print("Patching the file:")
                filepath = path +  file.InternalPath
                patchpath = path + patch.InternalPath 
                
                restorePatch(filepath, patchpath)
        
        
    
    
    def readAllFiles(self, path = ""):
        # Read files recursively
        if self.Name != "":
            npath = path + self.Name + "/"
        else:
            npath = path
        
        os.makedirs(npath, exist_ok = True)
        #print(npath)
        
        for k in self.files:
            k.readFile(npath)
            
        for k in self.patches:
            k.readFile(npath)
            
        for k in self.folders:
            k.readAllFiles(npath)
        
        
            
    
    def addNewBlocks(self, file):
        #Add binary content to the blocks
        print("Adding file...")
        content = file.getBinary()
        
        blockNew = True
        
        if len(self.blocks) == 0:
            block = blocks(self)
            block.useZlib = self.useZlib
            block.pool = self.initPool #1
            block.block = self.lastBlock + 1
        else:
            lblock = self.blocks[-1]
            if lblock.used == blockSize:
                block = blocks(self)
                block.pool = lblock.pool
                block.block = lblock.block + 1
            else:
                block = lblock
                blockNew = False

        
        ## Remaining: Take the rest of the last block
        rem = blockSize - block.used
        prem = block.used
        #rem = block.used
        
        ### Divide the content in the amount of blocks
        numblocks = math.ceil((len(content)-prem)/blockSize)
        
        k = 0
        
        if prem > 0:  
            block.addToBlock( content[0:rem] )
            npol = block.pool
            
            if block.used == blockSize:
                block.writeclose()
                file.add_extents(block, prem)  #the file should report the extent
                block = blocks(self) #new block
                block.pool = npol
                block.block = lblock.block + 1
                blockNew = True
                
                #prem = -prem
                k=1
            else:
                numblocks = 0
                file.add_extents(block, prem)  #the file should report the extent
            
        
        tfile = file.Name
        tblocks = block.block
        
        print("numblocks: ", numblocks)
        
        Reading = True
        if k >= numblocks:
            Reading = False
        
        #while k < numblocks:
        while Reading:
            
            tblocks = block.block
            
            if block.block > blocksPerPool and blockNew :
                block.pool += 1
                block.block = 0
            
            # Extract the binary content
            initp = k*blockSize - prem
            endp = (k+1)*blockSize - prem
            
            if endp >= len(content):
                endp = len(content)
                Reading = False ## Finished!!!
            
            extn = content[initp:endp]            
            
            #block.content = extn
            block.addToBlock(extn)
           
            self.lastBlock = block.block
            self.blocks.append(block)

            file.add_extents(block)  # examine the extents in the file
            #self.blocks.append(block)  #add the used block
            
            #if k < numblocks:            
            #if len(extn) > 0:
                #block.writeclose()    
            block.write()
            #elif endp < len(content): 
            #    k = k - 1
            #if k == numblocks and endp < len(content):
            #    numblocks += 1
                
            
            
            
            pool = block.pool
            n = block.block + 1
            


            
            block = blocks(self)  # Create a new object
            
            block.pool = pool
            block.block = n
            
            
            
            k += 1
            
            #if endp >= len(content):
            #    break
            
            #print( numblocks,  k , "- block ", n, " pool ", pool)
        
        
        print("Writen ", k , " blocks" )
        
        
        
    
    def genBlocks(self):
        
        # Check each file for the existing blocks
        print("Creating blocks...")
        for k in self.Index.files:
            if len(k.extents) == 0: ## Not generated
                self.addNewBlocks(k)
        
        for k in self.Index.patches:
            if len(k.extents) == 0: ## Not generated
                self.addNewBlocks(k)
       
        if len(self.blocks) > 0:
            #self.blocks[-1].writeclose()
            self.blocks[-1].write()
            self.Pools = self.blocks[-1].pool
            
        for block in self.blocks:
            if block.used > 0:
                block.encode()
        