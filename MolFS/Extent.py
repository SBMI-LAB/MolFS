# -*- coding: utf-8 -*-
import os 
import shutil
import pathlib
import datetime
import math
import zlib

from Block import *

        
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
        
        self.numblocks = 0
        
        self.FS = None
    
    def addBlocks(self, block):
        self.blocks.append(block)
        self.numblocks += 1
    
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
            
            
            if len(self.blocks[k].getContent()[p_in:p_out]) == 0:
                print("Error here")
            
            if k== 0:
                content = self.blocks[k].getContent()[p_in:p_out]
                p_in = 0
            else:                
                content += self.blocks[k].getContent()[p_in:p_out]
            
        
        
            
        
        return content
    
    
    def searchBlocks(self, Root, pool, block):
        
        passed = False

        for nblock in Root.blocks:
            if nblock.pool == pool and nblock.block == block:
                passed = True
                return nblock
        
        if passed == False:
            nblock = blocks(self.FS)
            nblock.pool = pool
            nblock.block = block
            
            Root.blocks.append(nblock)
            return nblock
            
                
                
    
    
    def reloadBlocks(self, Root):
        # Recreates the block structure and points to the target file
        # It is not THAT simple!
        print("Reloading blocks")
        tsize = blockSize
        
        
        self.block_out = self.block_in + self.numblocks
        print("Pool", self.pool, "Block", self.block_in)
        # print("Range of blocks:", self.block_in, self.block_out)
        
        
        for k in range(self.block_in,self.block_out):
            
            nblock = self.searchBlocks(Root, self.pool, k)
            
            self.blocks.append(nblock)
            print("Adding block ", self.pool, k)
            
            
            
            
        
        
            
            
            
        
        
        
       