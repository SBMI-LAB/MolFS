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
        
       