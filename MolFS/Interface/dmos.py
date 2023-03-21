#import subprocess

### Module SeqNAM for MolFS

import os
import sys
import types
from MolFS.Binary import *

sys.path.insert(1,"MolFS/Interface/DMOS")

from DMOS.DMOS_encode import DMOSEnc
from DMOS.DMOS_decode import DMOSDec


class MolFSDev: ### class dmos
    
    UseFastQ = True
    
    DoubleStep = True
    ## It will require the DMOS decoder prior to 
    ## the binary conversion
    
    Address = 0
    
    StrandAddress = 0
    
    Parameters = ""
    
    
#    encoder = "LDPC256_03"
#    msgSize = 16*8
#    codeSize = 256


    
    #encoder = "LDPC_512_PR"
    #msgSize = 48*8  ##  384
    #codeSize = 512

    encoder = "LDPC_768_PR"
    msgSize = 72*8  ##  576
    codeSize = 768

    # encoder = "LDPC_4096_PR"
    # msgSize = 384*8  ## 3072
    # codeSize = 4096

    
    
    
    def __init__(self):
        '''
            Startup of the interface
        '''
        self.encodeParam = 1
        self.decodeParam = 1
        self.Block = 0
        self.Pool = 0

    
    def encode(self, in_file, out_file):
        '''
            Create a DNA file from the in_file
            These files are datablocks for the MolFS
        '''
        
        dmod = DMOSEnc()
        
        dmod.Address = self.Address
        
        
        # encoder = "LDPC256B_01"
        # dmod.LDPC_N = 18*8  ### 18 bytes per codeword
        

        
        # encoder = "LDPC256_03"
        # dmod.LDPC_N = 16*8  ### 16 bytes per codeword        
        
#        encoder = "LDPC03"
#        dmod.LDPC_N = 480  ### 16 bytes per codeword     
        
        
        dmod.LDPC_N = self.msgSize
      
        
        dmod.outputFile =  out_file
        dmod.encodeFile_LDPC_DMOS(in_file, self.encoder)
    
        self.Address = dmod.Address
    
    
    def decode(self,in_file, out_file):
        '''
            Decode a DNA file from in_file
        '''

        decod = DMOSDec()
        
        
        # encoder = "LDPC256B_01"        
        # decod.LDPC_N = 256  ### 256 bits per codeword
                    

        # encoder = "LDPC256_03"        
        # decod.LDPC_N = 256  ### 256 bits per codeword
        
#        encoder = "LDPC03"
#        decod.LDPC_N = 512  ### 256 bits per codeword
        
        decod.LDPC_N = self.codeSize
        
        decod.outputFile = out_file
        decod.decoFileLDPC(in_file, self.encoder)        
                
                
        
    
    
    def simulate(self, in_file, out_file):
        '''
            Intermediate command for simulations
        '''
        None
    
    def convert_to_fastq(self,in_file, out_file):
        '''
            Convert a DNA file (created in encode step) to FastQ format
        '''
        None
    
    
#seq = seqnam()
#seq.encode("tests/testfile.jpg","tests/testfile.dna")
#seq.convert_to_fastq("tests/testfile.dna", "tests/testfile.fastq")
#seq.decode("tests/testfile.fastq", "tests/testfileout.jpg")


