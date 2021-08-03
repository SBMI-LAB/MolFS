# -*- coding: utf-8 -*-
import os 
import shutil
import pathlib
import datetime
import math

from MolFS.Binary import *

blockSize = 4096 # bytes
blocksPerPool = 1000

fillBlocks = False


class folder:
    # object structure to define folders
    
    
    def __init__(self, name):
        
        self.Name = name
        
        self.folders = []
        
        self.files = []
        
        self.status = ""
        
        self.parent = None
        
        self.blocks = []
        
        self.PoolsPath = ""
        
        self.Index = None
        
        self.mDevice = None
        
    
    def addFile(self, file):
        self.files.append(file)
        self.Index.addFiles(file)

    def addNewFile (self, filename, localpath):
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
            
        for k in self.folders:
            k.readAllFiles(npath)
            
    
    def addNewBlocks(self, file):
        #Add binary content to the blocks
        print("Adding file...")
        content = file.getBinary()
        
        blockNew = True
        
        if len(self.blocks) == 0:
            block = blocks(self)
            block.pool = 1
            block.block = 0
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
            
        
        
        
        print("numblocks: ", numblocks)
        
        
        
        while k < numblocks:
            
            if block.block > blocksPerPool and blockNew :
                block.pool += 1
                block.block = 0
            
            # Extract the binary content
            initp = k*blockSize - prem
            endp = (k+1)*blockSize - prem
            
            if endp > len(content):
                endp = len(content)
            
            extn = content[initp:endp]            
            
            #block.content = extn
            block.addToBlock(extn)
           
            
            self.blocks.append(block)

            file.add_extents(block)  # examine the extents in the file
            #self.blocks.append(block)  #add the used block
            
            if k < numblocks-1:
                block.writeclose()            
            
            
            pool = block.pool
            n = block.block + 1
            


            
            block = blocks(self)  # Create a new object
            
            block.pool = pool
            block.block = n
            
            
            
            k += 1
            
            #print( numblocks,  k , "- block ", n, " pool ", pool)
            
        print("Writen ", k , " blocks" )
        
        
        
    
    def genBlocks(self):
        
        # Check each file for the existing blocks
        print("Creating blocks...")
        for k in self.Index.files:
            if len(k.extents) == 0: ## Not generated
                self.addNewBlocks(k)
            
       
        if len(self.blocks) > 0:
            self.blocks[-1].writeclose()
        
    
    

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
        
        self.extents = []
        
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
        
class extent:
    # definition of the extents of a file
    def __init__(self):        
        self.pool = 1
        self.block_in = 0
        self.offset_in = 0
        self.size = 0
        
        self.block_out = 0
        self.finaloffset = 0
        
        self.blocks = []
    
    def addBlocks(self, block):
        self.blocks.append(block)
    
    def getData(self):
        # Get the data from the blocks
        ## Need access to the blocks
        
        # Pointer in 
        p_in = self.offset_in
        
        #p_outF = p_in + self.size
        p_outF = self.size
        
        p_out = p_outF
        
        for k in range( len(self.blocks) ):
            
            if p_outF > blockSize:
                p_out = blockSize
                p_outF -= blockSize
            else:
                p_out = p_outF
            
            
            if k== 0:
                content = self.blocks[k].getContent()[p_in:p_out]
                p_in = 0
            else:                
                content += self.blocks[k].getContent()[p_in:p_out]
            
        
        
            
        
        return content
        
        

class blocks:
    def __init__(self, FS):
        self.block = -1
        self.pool = -1
        self.available = False
        self.FS = FS
        
        self.file = ""
        
        self.content = None
        
        self.used = 0  # May be used in the future
        
        self.closed = False
        
        self.mDevice = FS.mDevice
        
        self.initFlag = str.encode("--Init--MolFS--")
        
        self.endFlag = str.encode("--MolFS--EOF--")
        
    
    def addToBlock(self, cont):
        if self.content == None:
            self.content = cont
        else:
            self.content += cont
        
        self.used = len(self.content)
    
    def write(self):
        # Check block name
        self.used = len(self.content)
        
        ### Add a signature to the content
        #content2 = self.initFlag + self.content + self.endFlag
        content2 = self.content
        self.file = "Pool_"+str(self.pool)+"_Block_"+str(self.block)
        
        binaryWriteHex(content2,self.FS.PoolsPath+self.file)
        
        
        binaryWrite(content2, self.FS.PoolsPath+self.file + ".bin")
        #self.mDevice.encode(self.FS.PoolsPath+self.file + ".bin", self.FS.PoolsPath+self.file + ".dna")
        
        
        
    def writeclose (self):
        # Close the DataBlock
        
        if self.closed == False:
        
            self.used = len(self.content)
            #diff = blockSize - self.used
            #print(diff)
            
            if self.used < blockSize and fillBlocks :
                self.content += bytes(blockSize-self.used)
                for k in range(blockSize-self.used):
                    self.content.extent(0)
            
            self.used = blockSize
            self.write()
            
            #self.content = [] # delete content to save memory        
            
            self.closed = True  # do not close twice
        
        
    def getContent(self):
        ## Read binary file
        self.file = "Pool_"+str(self.pool)+"_Block_"+str(self.block)
        filename = self.FS.PoolsPath+self.file
        
        if os.path.exists(self.FS.PoolsPath+self.file):
            self.content = HexRead(filename)
            
#            sif = self.content.find(self.initFlag)
#            sef = self.content.find(self.endFlag)
#            if sif != -1:
#                self.content = self.content[sif + len(self.initFlag) :]
#            if sef != -1:
#                self.content = self.content[:sef]
        
        return self.content
    