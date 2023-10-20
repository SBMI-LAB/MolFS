#import subprocess

### Module SeqNAM for MolFS

# Requirements: tqdm

###

import os
import sys
import types

#import swalign
from Binary import *

sys.path.insert(1,"MolFS/Interface/seqNAM")
sys.path.insert(1,"Interface/seqNAM")

from Interface.addressEncoder import *

from Interface.seqNAM.encodeModule import seqNAMencode
from Interface.seqNAM.decodeModule import seqNAMdecode
from Interface.seqNAM.convert_Format import convertFormat


class MolFSDev: ### class seqnam
    
    UseFastQ = True
    
    DoubleStep = False
    
    LocalFolder = os.path.dirname(os.path.abspath(__file__))
    
    
    def __init__(self):
        '''
            Startup of the interface
        '''
#        self.nseg = 130
#        self.nseg = 514

        self.DoubleStep = False
        
        self.ValidDecode = False

        self.nseg = 2050
        self.maxSeg = self.nseg + 20
        
        self.encodeParam = 1
        self.decodeParam = 1
        
        self.Address = 0
        
        self.Block = 0
        self.Pool = 0
        
        self.Redundancy = 1
        
        self.MaxIterations = 0
        
        
        #self.ForwardTag  = "ATCACGAGGCCCTTTCGTCTTCA"  
        #self.ForwardTag  = "ATCACGAGGCCCTTTCGTCTTCAAGAATTC"  
        self.ForwardTag  = "ATCACGAGGCCCTTTCGTC"
        #self.BackwardTag = "TGAAGACGAAAGGGCCTCGTGAT"
        #self.BackwardTag = "TGATAAACTACCGCATTAAAGCTTATCGATGAGT"  # Terminator
        self.BackwardTag =  "TGATAAACTACCGCATTAAAGCTTATCG"  # Terminator
        # Forward and Backward tags are used for
        # nanopore compatibility
        
    def getPrimer(self):
#        initiators = ["GCCCAATACGCAAACCGC", "CCATCGCCCTGATAGACG", "CCACGAATCCGATGTAACTA", "GTGTACGAATATACCACATACCA", "CAAAAAACCCCTCAAGACC", "GGACCAGGAACTAATCAG", "AGACGGGCCAGAACAAAC", "GGACCAGGAACTAATCAG", "CTCACACTCTACTCAACAA", "ATCACGAGGCCCTTTCGTC"]
#        terminators = ["TGACCTGATAGCCTTTGTAGAT", "GATGGCGTTCCTATTGGTT", "GCCTTGTCATCATCAGTTCCA", "GCCTTGTCATCATCAGTTCCA", "CTCTCTCTTATCTCACCTTAATATAG", "TAGTTACATCACAGAATCCG", "GTTTGTTCTGGCCCGTCT", "TAGTTACATCACAGAATCCG", "TTTCCTTGGGTTTGTTCT", "CGATAAGCTTTAATGCGGTAGTTTATCA"]
        initiators = ["GCCCAATACGCAAACCGC","CCATCGCCCTGATAGACG","CCACGAATCCGATGTAACTA","GTGTATTGCCGTTGCTGTC","CAAAAAACCCCTCAAGACC","GGACCAGGAACTAATCAG","AGACGGGCCAGAACAAAC","CAATACTGCTACCTCACGCTCTA","GAACGAGAGTAGTAGTCCT","ATCACGAGGCCCTTTCGTC"]
        terminators = ["TGACCTGATAGCCTTTGTAGAT","GATGGCGTTCCTATTGGTT","GCCTTGTCATCATCAGTTCCA","TCGTCTTGAACTGATGGTG","CTCTCTCTTATCTCACCTTAATATAG","TAGTTACATCACAGAATCCG","GTTTGTTCTGGCCCGTCT","ACAGTTCCAGGTGATAGTTAGAGG","GGTTGTTCAGAGGCTTAG","GCTTTAATGCGGTAGTTTATCA"]
        
        pos = 0
        
        if self.Pool == 0:
            pos = self.Block*2
        else:
            pos = self.Block*2+1
        
        if pos >= len(initiators):
            pos = 0
        
        prime = initiators[pos]
        term  = self.seqrcomplement(terminators[pos])  #seqnam automatically transforms
        #term = terminators[pos]
        
        return prime, term
        
        
        
    def seqrcomplement(self,seq):
        outseq =''
        for nt in seq:
            if nt == 'A':
                outseq = 'T' + outseq
            if nt == 'T':
                outseq = 'A' + outseq
            if nt == 'C':
                outseq = 'G' + outseq
            if nt == 'G':
                outseq = 'C' + outseq
        
        return outseq
    
    
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
        
        dA = DNAAddress()
        
        nAddress = (self.Pool+1)*200 + (self.Block+1)*3
        
        primer = dA.encode(nAddress)
        
        prime, term = self.getPrimer()
        self.ForwardTag = prime
        self.BackwardTag = term
        

        argsn = types.SimpleNamespace()
        argsn.file_in = in_file #"seqNAM/testfile.jpg"
        argsn.out = out_file #"seqNAM/testfile.dna"
        
        argsn.size = 32
        argsn.delta = 0.001
        argsn.c_dist = 0.025
        argsn.rs = 2
#        argsn.map = "MolFS/Interface/seqNAM/original_map.txt"
        argsn.map = os.path.join(self.LocalFolder, "seqNAM/original_map.txt")
        
        
        argsn.alpha = self.Redundancy  ## Redundancy
        
        argsn.output_format = "sequence_only"        
        argsn.ensure_decode_ability = True
        
        argsn.verbose = 1
        argsn.stop = None
        argsn.plate_info = "Plate"
        argsn.plate_cells = 384
        argsn.strand_name = "seqNAM01-seq"
#        argsn.fwd_primer = "ACATCCAACACTCTACGCCC"
        

        argsn.fwd_primer = self.ForwardTag + primer
        #argsn.bwd_primer = "GTGTGTTGCGGCTCCTATTC"
        #argsn.bwd_primer = "GTGTGTTGCGGCTCCTATTC"+ self.ForwardTag
        #argsn.bwd_primer = primer
        argsn.bwd_primer = self.BackwardTag
        argsn.maximum_gc = 0.55
        argsn.minimum_gc = 0.45
        argsn.seed_size = 4
        argsn.config_file = False
        
        encodeInfo = seqNAMencode(argsn)
        
        print("Total segments: ",  encodeInfo["total_number_of_segment"])
        self.encodeParam = encodeInfo["total_number_of_segment"]
    
    def decode(self,in_file, out_file):
        '''
            Decode a DNA file (FastQ) from in_file
        '''
        dA = DNAAddress()
        nAddress = (self.Pool+1)*100 + (self.Block+1)
        primer = dA.encode(nAddress)
        
        prime, term = self.getPrimer()
        self.ForwardTag = prime
        self.BackwardTag = term
        
        #print(self.Pool, self.Block, term, out_file)
        
        argsn = types.SimpleNamespace()
        argsn.file_in = in_file #"seqNAM/testfile.dna"
        argsn.out = out_file #"seqNAM/testfileOut.jpg"
        
        argsn.size = 32
        argsn.delta = 0.001
        argsn.c_dist = 0.025
        argsn.rs = 2
#        argsn.map = "MolFS/Interface/seqNAM/original_map.txt"
        argsn.map = os.path.join(self.LocalFolder, "seqNAM/original_map.txt")
        argsn.alpha = 0.1
        
        argsn.output_format = "sequence_only"        
        argsn.ensure_decode_ability = True
        
        argsn.verbose = 1
        argsn.stop = None
        argsn.plate_info = "Plate"
        argsn.plate_cells = 384
        argsn.strand_name = "seqNAM01-seq"
#        argsn.fwd_primer = "ACATCCAACACTCTACGCCC"
        argsn.fwd_primer = self.ForwardTag + primer
        #argsn.bwd_primer = "GTGTGTTGCGGCTCCTATTC"
        #argsn.bwd_primer = primer
        argsn.bwd_primer = self.BackwardTag
        argsn.maximum_gc = 0.55
        argsn.minimum_gc = 0.45
        argsn.seed_size = 4
        argsn.config_file = False
        
        
        
        argsn.file_format = "csv" #"fastq"
        #argsn.primer_length = 20 
        argsn.primer_length = 20 + len(self.ForwardTag)
        
        argsn.no_correction=False
        argsn.padding = 0
        
        
        iterations = 0
        
        
        
        nsegs = self.nseg
        nsegs = self.decodeParam
        
        searchFlag1 = str.encode("--Init--MolFS--")
        searchFlag2 = str.encode("--MolFS--EOF--")
        
        
        
        while True:
            valid = False
            argsn.num_segments = nsegs
            ## Delete previously decoded files
#            if os.path.exists(out_file):
#                os.remove(out_file)  
                
            if True:
                print("Attemp decode using",nsegs, "segments")
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
                self.ValidDecode = True
                break;
            else:
                if (nsegs==self.maxSeg):
                    nsegs = 0
                nsegs += 1
                
#                break
                
            iterations += 1
            
            
            
            if iterations > self.MaxIterations:
#                print("Max iterations: ", iterations)
                break;
                
            #break ## just for one case
        
        if valid == False:
            self.ValidDecode = False
            print("Error decoding file ", in_file)
            #raise Exception ("File not decoded")
        return valid
                
        
    
    
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
        
        
    def exportSequences(self, in_file):
        # Reads a block file
        # and returns the plain list of sequences
        
        seqFile = open(in_file,'r')
        Lists = seqFile.readlines()
        Lists = Lists[1:]
        
        return Lists
        

    def FilterSequence(self, sequence):
        ### Filters the sequence for the expected primers
        
        Failed = 0
        
        prime, term = self.getPrimer()
        
        term = self.seqrcomplement(term)
        
        posP = 0
        posT = len(sequence) - 1
        
        if prime in sequence:
            posP = sequence.index(prime)
        else:
            Failed += 10
        
        if term in sequence:
            posT = sequence.index(term) + len(term)
        else:
            Failed += 2
        
        if Failed > 0:
#            sequence = "---" + str(Failed) + ": " + sequence
            sequence = ""
        else:
            sequence = sequence[posP:posT]
        
        
        ### Size analysis
        rawSize = 248
        
        nSize = len(sequence) - len(prime) - len(term)
        
#        if rawSize != nSize: ## Only exact size passes
#            sequence = ""
        
        
        
        return sequence
        

    def searchSeq(self, template, seq):
    
        pos = -1
        scoring = swalign.NucleotideScoringMatrix(2,-1)
        sw = swalign.LocalAlignment(scoring)  # you can also choose gap penalties, etc...
        alignment = sw.align(template, seq)
        
        
        ## Evaluation
        aM = alignment.matches
        aU = alignment.mismatches
        
        Sc = aM/(aM+aU)  ### relation between matches and mismatches
        
        if Sc > 0.8:
            pos = alignment.q_pos
        
        return pos        
    
    
    def ClassifySequence(self, sequence):
        # Reads a sequence
        # and returns the pool/block it would belong
        
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
    
    
    def ProcessFastQFolder(self, fastqfolder, workpath):
        # Receives a fastqfolder to preprocess
        # returns a processed fastqfolder 
        # If there is not preprocessing here,
        # it will return the same folder
        # MolFS suggests a workpath, but it is not 
        # mandatory
        # SeqNAM uses a SeqNAMFilter to
        # preprocess the sequences

        FastQFolder = fastqfolder
        WorkPath = workpath
        
        #AppPath = "/home/acroper/Documents/NCAT/Research/DMOS/SeqNAMFilter/build-SeqNAMFilter-Desktop-Debug/"
        AppPath =  os.path.dirname(os.path.realpath(__file__)) + "/SeqNAMFilter/build-SeqNAMFilter-Desktop-Debug/"
        
        
        cmd = os.path.join(AppPath , "SeqNAMFilter" )
        cmd += " -f " + FastQFolder 
        cmd += " -w " + WorkPath
        
        cmdS = cmd.split()
        
        cwd = os.getcwd()
        os.chdir(AppPath)
        subprocess.Popen( cmdS )
        os.chdir(cwd)
        
        return WorkPath
    
    def PreProcessFastQ(self, fastqfolder, workpath):
        # Receives a fastqfolder to preprocess
        # returns a processed fastqfolder 
        # If there is not preprocessing here,
        # it will return the same folder
        # MolFS suggests a workpath, but it is not 
        # mandatory

        # SeqNAM uses a SeqNAMFilter to
        # preprocess the sequences
        
        FastQFolder = fastqfolder
        WorkPath = workpath
        
        AppPath = "/home/acroper/Documents/NCAT/Research/DMOS/SeqNAMFilter/build-SeqNAMFilter-Desktop-Debug/"
        
        cmd = os.path.join(AppPath , "SeqNAMFilter" )
        cmd += " -f " + FastQFolder + " -w " + WorkPath
        
        cmdS = cmd.split()
        
        cwd = os.getcwd()
        os.chdir(AppPath)
        print(cmdS)
        process = None
        process = subprocess.Popen( cmdS , stdout=subprocess.PIPE)
        os.chdir(cwd)
        
        return process
        
        
    
    
    
#seq = seqnam()
#seq.encode("tests/testfile.jpg","tests/testfile.dna")
#seq.convert_to_fastq("tests/testfile.dna", "tests/testfile.fastq")
#seq.decode("tests/testfile.fastq", "tests/testfileout.jpg")


