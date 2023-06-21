###
# MolFS dummy device
# 
# Use this as starting point to define a custom
# Molecular device

import os
import sys
import types

from Binary import *
from basicEncoder import *
from Interface.addressEncoder import *



class MolFSDev: ### class for the molecular device
    
    UseFastQ = True
    
    DoubleStep = False
    
    LocalFolder = os.path.dirname(os.path.abspath(__file__))
    
    
    def __init__(self):
        '''
            Startup of the interface
        '''

        self.DoubleStep = False
        
        self.ValidDecode = False
        
        self.encodeParam = 0
        self.decodeParam = 0
        
        self.Address = 0
        
        self.Block = 0
        self.Pool = 0
        
        self.Redundancy = 0
        
        self.MaxIterations = 0
          
    
    def encode(self, in_file, out_file):
        '''
            Create a DNA file from the in_file
            These files are datablocks for the MolFS
            
            in_file : a binary file
            out_file: DNA encoded file 
            
            We recommend to create one starting sequence
            that encodes the Pool and Block numbers, to use
            it as barcode to easily identification.
            
            Below it is just one example
        '''
       
        dA = DNAAddress()
        nAddress = (self.Pool+1)*200 + (self.Block+1)*3
        primer = dA.encode(nAddress)
        
        be = basicEncoder()
        
        be.Primer = primer
        
        be.encode(in_file, out_file)
        
        
        




    
    def decode(self,in_file, out_file):
        '''
            Decode a DNA file (possible FastQ) from in_file
            
            in_file: Input file with DNA sequences
            out_file: Binary decoded file
            
            We recommend to create one starting sequence
            that encodes the Pool and Block numbers, to use
            it as barcode to easily identification.
            
            Below it is just one example
        '''
        self.ValidDecode = False
        
        dA = DNAAddress()
        nAddress = (self.Pool+1)*100 + (self.Block+1)
        primer = dA.encode(nAddress)
        
        ## Add your decoding code
        ## It must generate a binary file if successful
        
        be = basicEncoder()
        
        be.Primer = primer
        
        be.decode(in_file, out_file)
        
        ## Write valid verification code
        
#        if (Encoding_Valid):
#            self.ValidDecode = True
        self.ValidDecode = True
        
        # If not valid, must return False
        return True
    
    
    def FilterSequence(self, sequence):
        ### Filters the sequence for the expected primers
        
        return sequence
    
    def ClassifySequence(self, sequence):
        '''
        Reads a sequence and returns the pool/block it would belong
        
        Review the below code, and adapt it with the same 
        equation of nAddress of above code.
        
        This is an example function that is not optimized
        
        If the error rate is high, it is recommended using
        Smith-Waterman for alignment first
        
        '''
        
        oSeq = sequence
        
        cPool = -1
        cBlock = -1
        
        
        dA = DNAAddress()
        
        for Pool in range(2):
            for Block in range(5):
                nAddress = (Pool+1)*200 + (Block+1)*3
                sAddress = dA.encode(nAddress)
                
                if sAddress in sequence:
                    cPool = Pool
                    cBlock = Block
                    
                    self.Pool = Pool
                    self.Block = Block
                    
                    oSeq = self.FilterSequence(sequence)
                    
                    return cPool, cBlock, oSeq
        
        
        
        return cPool, cBlock, oSeq
    
    
    def ClassifySequence_SW(self, sequence):
        # With Smith Waterman
        # Reads a sequence
        # and returns the pool/block it would belong
        
        oSeq = sequence
        
        cPool = -1
        cBlock = -1
        
        
        dA = DNAAddress()
        
        for Pool in range(3):
            for Block in range(5):
                nAddress = (Pool+1)*200 + (Block+1)*3
                sAddress = dA.encode(nAddress)
                
                Pos = self.searchSeq(sequence, sAddress)
                
                if Pos >= 0:
                    cPool = Pool
                    cBlock = Block
                    
                    self.Pool = Pool
                    self.Block = Block
                    
                    oSeq = self.FilterSequence(sequence)
                    
                    return cPool, cBlock, oSeq
        
        
        
        return cPool, cBlock, oSeq  
    
    def getPrimerPair(self, cPool, cBlock):
        
        self.Pool = cPool
        self.Block = cBlock
        
        dA = DNAAddress()
        nAddress = (cPool+1)*200 + (cBlock+1)*3
        sAddress = dA.encode(nAddress)
        
        prime, term = self.getPrimer()
        
        termn = self.seqrcomplement(term)
        
        firstP = prime + sAddress
        lastP = termn
        
        return firstP, lastP
    
    
    def exportSequences(self, in_file):
        # Reads a block file
        # and returns the plain list of sequences
        
        seqFile = open(in_file,'r')
        Lists = seqFile.readlines()
#        Lists = Lists[1:]
        
        return Lists