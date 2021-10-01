# -*- coding: utf-8 -*-
"""
Encode digital data to DMOS
"""


class DMOSEnc:


    outputFile = "/tmp/DMOS.txt"
    
    
    def Hex2MD(self, data):
        """
        data is 2 bytes in binary
        16 bits
        """
        s = []
        
        for byten in data:
            nd = format(byten, '#010b')
            ns = nd[2:]                        
            for nbit in ns:
                if nbit == '1':
                    s.append(1)
                else:
                    s.append(0)
        
        ## Prepare the output file ##
        
        f = open(self.outputFile, "w")
        
        k = 0
        for nbit in s:
            if nbit == 1:
                strng = "Add Mutation " + str(k)+"\n"
                f.write(strng)
                print(strng)
            k += 1
        f.close()
        print(s)
            
        ## End basic 16 bit encode    
        
        
            
            
            
                        
            
                    
dmod = DMOSEnc()
k1 = [0,6]
dmod.Hex2MD(k1)        

