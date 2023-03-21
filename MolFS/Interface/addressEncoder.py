# -*- coding: utf-8 -*-



class DNAAddress:
    
    seqLength=10
    
    ## Symbols
    ## Symbol 0: GG, GC, 
    ## Symbol 1: AA, AT
    S0 = ["GG", "GC"]
    S1 = ["AA", "AT"]
    
    
    def encode(self, address):
        ### Encode an address
        nd = format(address, '#010b')[2:]
        
        nd = self.adjust(nd)
        output = ""
        k = 0
        for c in nd:
            if c == "0":
                output += self.S0[k]
            else:
                output += self.S1[k]
            
            k += 1
            if k == 2:
                k = 0
        
        return output
            
        
    
    def adjust(self, address):
        
        n = len(address)
        
        if n > self.seqLength:
            address = address[ n-self.seqLength : ]
        else:
            for k in range(self.seqLength-n):
                address = "0" + address
        return address
        
