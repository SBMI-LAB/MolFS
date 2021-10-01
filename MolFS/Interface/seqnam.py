#import subprocess

### Module SeqNAM for MolFS

import os
import sys
import types
from MolFS.Binary import *

sys.path.insert(1,"MolFS/Interface/seqNAM")

from seqNAM.encodeModule import seqNAMencode
from seqNAM.decodeModule import seqNAMdecode
from seqNAM.convert_Format import convertFormat


class MolFSDev: ### class seqnam
    def __init__(self):
        '''
            Startup of the interface
        '''
#        self.nseg = 130
#        self.nseg = 514
        self.nseg = 2050
        self.maxSeg = self.nseg + 20
    
    def encode(self, in_file, out_file):
        '''
            Create a DNA file from the in_file
            These files are datablocks for the MolFS
        '''
#        python3_command = "SeqNAM/Encode.sh " + in_file + " " + out_file  # launch your python2 script using bash
#        process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
#        output, error = process.communicate()  # receive output from the python2 script

        #file_path = os.path.dirname(__file__)
        #print(os.path.abspath(__file__))

        argsn = types.SimpleNamespace()
        argsn.file_in = in_file #"seqNAM/testfile.jpg"
        argsn.out = out_file #"seqNAM/testfile.dna"
        
        argsn.size = 32
        argsn.delta = 0.001
        argsn.c_dist = 0.025
        argsn.rs = 2
        argsn.map = "MolFS/Interface/seqNAM/original_map.txt"
        
        
        argsn.alpha = 0.1
        
        argsn.output_format = "sequence_only"        
        argsn.ensure_decode_ability = True
        
        argsn.verbose = 1
        argsn.stop = None
        argsn.plate_info = "Plate"
        argsn.plate_cells = 384
        argsn.strand_name = "seqNAM01-seq"
        argsn.fwd_primer = "ACATCCAACACTCTACGCCC"
        argsn.bwd_primer = "GTGTGTTGCGGCTCCTATTC"
        argsn.maximum_gc = 0.55
        argsn.minimum_gc = 0.45
        argsn.seed_size = 4
        argsn.config_file = False
        
        seqNAMencode(argsn)
    
    
    def decode(self,in_file, out_file):
        '''
            Decode a DNA file (FastQ) from in_file
        '''

        
        argsn = types.SimpleNamespace()
        argsn.file_in = in_file #"seqNAM/testfile.dna"
        argsn.out = out_file #"seqNAM/testfileOut.jpg"
        
        argsn.size = 32
        argsn.delta = 0.001
        argsn.c_dist = 0.025
        argsn.rs = 2
        argsn.map = "MolFS/Interface/seqNAM/original_map.txt"
        argsn.alpha = 0.1
        
        argsn.output_format = "sequence_only"        
        argsn.ensure_decode_ability = True
        
        argsn.verbose = 1
        argsn.stop = None
        argsn.plate_info = "Plate"
        argsn.plate_cells = 384
        argsn.strand_name = "seqNAM01-seq"
        argsn.fwd_primer = "ACATCCAACACTCTACGCCC"
        argsn.bwd_primer = "GTGTGTTGCGGCTCCTATTC"
        argsn.maximum_gc = 0.55
        argsn.minimum_gc = 0.45
        argsn.seed_size = 4
        argsn.config_file = False
        
        
        
        argsn.file_format = "csv" #"fastq"
        argsn.primer_length = 20
        
        argsn.no_correction=False
        argsn.padding = 0
        
        
        iterations = 0
        nsegs = self.nseg
        searchFlag1 = str.encode("--Init--MolFS--")
        searchFlag2 = str.encode("--MolFS--EOF--")
        while True:
            valid = False
            argsn.num_segments = nsegs
            ## Delete previously decoded files
            if os.path.exists(out_file):
                os.remove(out_file)  
                
            if True:
                seqNAMdecode(argsn)
            
                ## Check file
                if os.path.exists(out_file):
                    cont = binaryRead(out_file)
                    #cont2 = cont[-len(searchFlag):]
                    k1=cont.find(searchFlag1)
                    k2=cont.find(searchFlag2)
                    
                    if k1 != -1 and k2 != -1: 
                        
                        numsize=cont[k2-7:k2-1]
                        try:
                            kn = int(numsize.decode())
                            kn2 = k2-len(searchFlag1)-9
                            if kn == kn2:
                                valid = True
                        except:
                            print("Issues decoding file, attempt:", iterations)
                        
                        #if k2 == len(cont)-len(searchFlag2):
                        #    valid = True
                        #else:
                        #    print("Issues decoding file, attempt:", iterations)
            #except:
            #    None
            
            if valid:
                break;
            else:
                if (nsegs==self.maxSeg):
                    nsegs = 0
                nsegs += 1
                
            iterations += 1
            
            
            
            if iterations > self.maxSeg:
                break;
                
            #break ## just for one case
        
        if valid == False:
            print("Error decoding file ", in_file)
            raise Exception ("File not decoded")
                
        
    
    
    def simulate(self, in_file, out_file):
        '''
            Intermediate command for simulations
        '''
        self.convert_to_fastq(in_file, out_file)
    
    def convert_to_fastq(self,in_file, out_file):
        '''
            Convert a DNA file (created in encode step) to FastQ format
        '''
        convertFormat(in_file, out_file)
    
    
#seq = seqnam()
#seq.encode("tests/testfile.jpg","tests/testfile.dna")
#seq.convert_to_fastq("tests/testfile.dna", "tests/testfile.fastq")
#seq.decode("tests/testfile.fastq", "tests/testfileout.jpg")


