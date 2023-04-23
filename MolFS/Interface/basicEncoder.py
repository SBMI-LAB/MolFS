# -*- coding: utf-8 -*-

from Binary import *

class basicEncoder:
    
    '''
    This is just an example to encode
    a binary file to DNA. 
    '''
    
    ## Symbols
    ## Symbol 0: GG, GC, 
    ## Symbol 1: AA, AT
    S0 = ["GG", "GC"]
    S1 = ["AA", "AT"]
    
    BpS = 16 # bytes per strand
    
    Primer = ""   
    
    
    def encode(self, inputFile, outputFile):
        ### Encode the file to DNA
        # Replace this with the method you desire
        # Put at first the primer given externally
        
        count = 0
        
        contents = binaryRead(inputFile)
        
        dna = open(outputFile, 'w')
        # Contents is now a byte array
        line = ""
        
        for nbyte in contents: 
            
            if count == 0:
                line = self.Primer # each line starts with primer
#                line = ""
                
            nd = format(nbyte, '#010b')
            ns = nd[2:]  
#            print(byten, ns)                      
            for nbit in ns:
                if nbit == '1':
                    line += self.S1[0]
                else:
                    line += self.S0[0]
            
            count += 1
            if count == self.BpS:
                count = 0
                dna.write(line + "\n")
                
        
        if count > 0 :
            dna.write(line + "\n")
            
        dna.close()
        
    
    
    def stringToBytes(self, s):
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')
    
    def decode(self, inputFile, outputFile):
        # reads the contents (sequences) from the file
        # This example does not follows a fastq format
        
        # Remember, the primer could be present
        # and needs to be removed during decoding
        
        count = 0
        
        seqFile = open(inputFile, 'r')
        
        binFile = open(outputFile, 'wb')
        
        sequences = seqFile.readlines()
        
        binlist = ""
        

        for seq in sequences:
            cseq = seq[len(self.Primer):]
#            cseq = seq
            n = int(len(cseq)/2) # we need two nt per bit
            
            
            for k in range(n):
                dnbit = cseq[k*2:k*2+2]
                
                if dnbit in self.S0:
                    binlist += "0"
   
                    
                elif dnbit in self.S1:
                    binlist += "1"
                
        ## Convert binlist to binary        
        
        bytelist = self.stringToBytes(binlist)
        binFile.write(bytelist)
        binFile.close()
        
            
        
        


        
