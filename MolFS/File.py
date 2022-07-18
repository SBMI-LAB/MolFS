# -*- coding: utf-8 -*-
import os 
import shutil
import pathlib
import datetime
import math
import zlib

from Extent import *


class files:
    # object structure to define files
    def __init__(self, name):
        
        self.Name = name
        
        self.status = ""
        self.creationDate = ""
        self.ModifyDate = ""
        
        self.LocalFile = ""
        
        self.available = False
        self.modified = False
        self.syncronized = False
        
        self.size = 0 # size in bytes
        
        self.Id = -1 ## Undefined ID
        
        self.localPath = ""
        
        self.InternalPath = ""
        
        self.extents = []
        
    
    def addNewFile(self, filename, localpath):

        shutil.copyfile(filename, localpath )  # create a copy 
        self.LocalFile = filename 
        self.available = True
        self.modified = True # File is modified
        self.ModifyDate = self.checkModified()
        
        self.localPath = localpath
        

    def addPatchFile(self, filename, localpath):

        #shutil.copyfile(filename, localpath )  # create a copy 
        self.LocalFile = filename 
        self.available = True
        self.modified = True # File is modified
        self.ModifyDate = self.checkModified()
        
        self.localPath = filename

    
    
    def dirPrint(self, path):
        print(self.properties(),  path + self.Name )
    
    def checkModified(self):
        if self.LocalFile != "":
            fname = pathlib.Path(self.LocalFile)
            if fname.exists():
                mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
                return mtime
                
    def getBinary(self):
        ## Generate binary data. 
        content = binaryRead(self.LocalFile)        
        return content
        #binaryWriteHex(content, path + Name + ".txt")
        
    def add_extents(self, block, offset = 0):
        # This should check the extension of the block
        if len(self.extents) == 0:
            ext1 = extent()
            ext1.block_in = block.block
            ext1.offset_in = offset # by now
            ext1.pool_in = block.pool
            ext1.size = block.used ## ??
            
            ext1.block_out = block.block
            ext1.finaloffset = block.used
            
            ext1.addBlocks(block)
            
            self.extents.append(ext1)
            
        else:
            # previous
            pext: extent = self.extents[-1]
            
            ## if the block is the same than the previous one, that means
            ## if it is continous!
            if block.block == (pext.block_out + 1) and block.pool == pext.pool and pext.finaloffset == blockSize:
                ## No new extent is required, it just add new data
                pext.block_out = block.block
                pext.finaloffset = block.used
                pext.size += block.used
                pext.addBlocks(block)
               
            else:
                ext1 = extent()
                ext1.block_in = block.block
                ext1.offset_in = 0 # by now
                ext1.pool_in = block.pool
                ext1.size = block.used
                
                ext1.block_out = block.block
                ext1.finaloffset = block.used
                
                ext1.addBlocks(block)
                self.extents.append(ext1)
                
                
    def readFile(self, path):
        npath = path + self.Name
        print(npath)
        
        Added = False
        #content = []
        
        for ext in self.extents:
            if Added == False:
                content = ext.getData()
            else:
                content += ext.getData()
            Added = True
        
        if Added == True:
            binaryWrite(content, npath)    
            
    
    
    def properties(self):
        ## This should look like:
        # Sync: No, Avail: No
        props = "Sync: "
        if self.syncronized:
            props += "Y"
        else: 
            props += "N"
        
        props += ", Avail: "
        if self.available :
            props += "Y"
        else:
            props += "N"
        
        return props
