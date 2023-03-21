# -*- coding: utf-8 -*-
import os 
import shutil
import pathlib
import datetime
import math
import zlib


from multiprocessing import Process

from Binary import *

#blockSize = 4096 # bytes
# blockSize = 65536 # bytes
blockSize = 3072*2*8 # bytes
# blockSize = 16 # bytes
blocksPerPool = 50

fillBlocks = False

useZlib = True

useBlockFlags = False

## alter block size if use BlockFlags
if useBlockFlags:
    FlagSize=len("--Init--MolFS--[0000][0000000]--MolFS--EOF--") ## Standard flag
    blockSize -= FlagSize





class blocks:
    def __init__(self, FS):
        self.block = -1
        self.pool = -1
        self.available = False
        self.FS = FS
        
        self.file = ""
        
        self.encodeParam = 0
        
        self.content = None
        
        self.used = 0  # May be used in the future
        
        self.closed = False
        
        self.mDevice = FS.mDevice
        
        self.initFlag = str.encode("--Init--MolFS--")
        
        self.endFlag = str.encode("--MolFS--EOF--")
        
        self.Address = 0
        
        self.Cached = False
        
        self.useZlib = False
        
        self.rBlockSize = 3072*8   ## real Block size info. 
        
        self.blockSize = self.rBlockSize  ## Block size used. Recalculated if used flags
        
        self.useBlockFlags = True
        
        
        
    
    def setFlags(self):
        self.useBlockFlags = True
        FlagSize=len("--Init--MolFS--[0000][0000000]--MolFS--EOF--") ## Standard flag
        self.blockSize =   self.rBlockSize - FlagSize
        
    def unsetFlags(self):
        self.useBlockFlags = False
        self.blockSize = self.rBlockSize
        print("\n\n Unsetting flags \n\n")
    
    
    def addToBlock(self, cont):
        if self.content == None:
            self.content = cont
        else:
            self.content += cont
        
        self.used = len(self.content)
    
    def checkFolder (self):
        ## Checks if Pools folder is present
        self.PoolFolder = self.FS.PoolsPath + str(self.pool) + "/"
        os.makedirs(self.PoolFolder, exist_ok = True)
    
    def write(self):
        # Check block name
        self.checkFolder()
        
        self.used = len(self.content)
        
        nameflag = str.encode("["+str(self.pool)+"_"+str(self.block)+"]")
        
        if self.useZlib:
            contentZ = zlib.compress(self.content)
            sizeflag = str.encode( "["+str(len(contentZ) ).zfill(7) +"]"  )
        else:
            sizeflag = str.encode( "["+str(self.used ).zfill(7) +"]"  )
        
        
        
        ### Add a signature to the content
#        content2 = self.initFlag + self.content +sizeflag+ self.endFlag
        
        
        ## ZLib
        
        
        if self.useBlockFlags:
            if self.useZlib:
                content2 = self.initFlag + contentZ +sizeflag+ self.endFlag + nameflag
            else:
                content2 = self.initFlag + self.content +sizeflag+ self.endFlag + nameflag
        else:
            if self.useZlib:
                content2 = contentZ
            else:
                content2 = self.content
        
        
        self.file = "Pool_"+str(self.pool)+"_Block_"+str(self.block)
        
#        binaryWriteHex(content2,self.PoolFolder +self.file)
        
        binaryWrite(content2, self.PoolFolder +self.file + ".bin")
        
        #self.mDevice.encode(self.PoolFolder +self.file + ".bin", self.PoolFolder+self.file + ".dna")
        
    def encode(self):
        if self.block == 0:
            self.mDevice.setAddress(0)
        
        self.mDevice.Block = self.block
        self.mDevice.Pool = self.pool
            
        self.mDevice.encode(self.PoolFolder +self.file + ".bin", self.PoolFolder+self.file + ".dna")
        
        self.encodeParam = self.mDevice.encodeParam[0]
        
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
        
        if self.Cached == False:
            self.content = []
            
            self.checkFolder()
            
            self.file = "Pool_"+str(self.pool)+"_Block_"+str(self.block)
            #filename = self.FS.PoolsPath+self.file
            filename = self.PoolFolder+self.file
            
            readfile = filename + ".dna"
            
            self.useZlib = self.FS.UseZLib
            
            if not os.path.exists(readfile):
                readfile = self.FS.CurrentSession.CachePath + self.file + ".fastq"
            
            
            
            #if os.path.exists(self.PoolFolder+self.file+".bin"):
            if os.path.exists(readfile):
                #self.content = HexRead(filename)
                self.mDevice.setDecodeParam(self.encodeParam)
                self.mDevice.Block = self.block
                self.mDevice.Pool = self.pool
#                self.mDevice.decode(filename+".dna", filename+".dec.bin")
                self.mDevice.decode(readfile, filename+".dec.bin")
                self.content = binaryRead(filename+".dec.bin")
                
                sif = self.content.find(self.initFlag)
                sef = self.content.find(self.endFlag) - len(self.endFlag)-10
                if sif > -1:
                    self.content = self.content[sif + len(self.initFlag) :]
                if sef > -1:
                    self.content = self.content[:sef]
                
                if self.useZlib :
                    self.tryGetCompress()
                    # self.content = zlib.decompress(self.content)
            
            self.Cached = False
        
        return self.content
    
    
    def tryGetCompress(self):
        attempts = 10
        success = False
        
        content = self.content
        
        for k in range(attempts):
            
            try:
                print("Step ", k+1 , " uncompressing")
                restored = zlib.decompress(content)
                success = True
                
                
            except:
                content = content[:-1]
                success = False
                
            
            if success:
                self.content = restored
                break;
        
        if not success:
            print("Error decompressing")
            
            
        
    
    
    def countStrands(self):
        """
        Statistical function to count the amount of strands in the output files
        """
        self.file = "Pool_"+str(self.pool)+"_Block_"+str(self.block)
        filename = self.PoolFolder+self.file + ".dna"
        
        lines = 0
        
        size = self.used
        
        if os.path.exists(filename): 
            with open(filename) as foo:
                lines = len(foo.readlines())
                foo.close()
        
        return lines, size       
    