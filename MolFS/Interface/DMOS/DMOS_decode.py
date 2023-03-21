# -*- coding: utf-8 -*-
### Decode from a standard DMOS output



from reedsolo import RSCodec, ReedSolomonError
import csv
import numpy as np

# from DMOS_address import *
import os
import subprocess
import math


class DMOSDec:

    LDPC_N = 8*8
    
    binaryBlock = None
    
    binaryStrings = []
    
    addressList = []
    
    domainValues = []
    
    LDPC_Valid = False
    
    outputFile = "DMOS.bin"
    
    def readDMOSFile(self, filename):
        ### Colects the binary information from the DMOS file
        
        file1 = open(filename,'r')        
        Lines = file1.readlines()        
        file1.close()
    
        binText = ""
        
        self.binaryStrings.clear()
        self.addressList.clear()
        self.domainValues.clear()

        for line in Lines:
            
            if 'Domains' in line:
                strLin = line[15:]
                self.addressList.append(strLin)
            
            
            if 'Binary' in line:
                strLin = line[14:-2].replace(", ","") ## Remove the comma and space
                strLin = strLin.replace(" ", "")
                self.domainValues.append(strLin)
                
                binText += strLin
                
                
                if len(binText) >= self.LDPC_N:
                    # print("Length:" , len(binText), self.LDPC_N)    
                    self.binaryStrings.append(binText)
                    binText = ""
        
    
    def decodeLDPC(self, designs="LDPC01"):
        DevPath = "/home/acroper/Documents/NCAT/Research/DMOS/DMOS_System/FECC/LDPC"
        ldpc_path = os.path.join(DevPath,'ProtographLDPC','LDPC-library')
        ldpc_designs = os.path.join(DevPath,'ProtographLDPC','Designs')
        
        extractDir=os.path.join(DevPath, "ProtographLDPC", "LDPC-codes")  
        extract_path = os.path.join(extractDir,"extract")
        
        pchk_file = os.path.join(ldpc_designs, designs+".pchk")
        gen_file = os.path.join(ldpc_designs, designs+".gen")
    
        ldpc_decode_path = os.path.join(ldpc_path, 'decode.py')
        
        
        ### Save the binary strings for decoder
        pathdir = "/tmp/LDPC/"
        
        if not os.path.exists(pathdir):
            os.makedirs(pathdir)
        
        ## Files used by the decoder
        received =os.path.join(pathdir,"received.txt")      ## Encoded message received
        decoded =os.path.join(pathdir,"decoded.txt")        ## Decoded message - after error correction
        recovered =os.path.join(pathdir,"recovered.txt")    ## Recovered binary file
        
        if os.path.isfile(recovered):
            os.remove(recovered)
        
        if os.path.isfile(decoded):
            os.remove(decoded)
        
        
#        print(filename)
        f = open( received , 'w')
        for line in self.binaryStrings:
            f.write(line+"\n")
        f.close()    
        
        
            # first perform the decoding
        process = subprocess.Popen("python3 " + ldpc_decode_path + ' --pchk-file ' + pchk_file + ' --received-file ' + received +
                       '  --output-file ' + decoded + "  --channel bsc --channel-parameters 0.001 --max-iterations 500", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        results = process.stderr.readlines()
        nr = results[0].decode()
        valid = nr[18]
        
        if valid == '1':
            self.LDPC_Valid = True
        else:
            self.LDPC_Valid = False
        
        if "01" not in designs:
            decoded = os.path.join(pathdir,"decoded.txt.unpunctured")
        
        
        subprocess.run( extract_path + " " + gen_file + " " + decoded + " " + recovered,  shell=True)
        
        f = open(recovered,'r')
        mrecovered = f.read().splitlines()
        f.close()
        # mrecovered=mrecovered[0:-1]
        
        return mrecovered 

    def decoFileLDPC(self, filename, designs):
        
        self.readDMOSFile(filename)
        dec = self.decodeLDPC(designs)
        
        # print(dec)
        # Rebuild binary file
        self.binaryBlock = bytearray()
        
        for s in dec:        
            self.binaryBlock += int(s, 2).to_bytes(len(s) // 8, byteorder='big')
        
        
        file2 = open(self.outputFile,'wb')
        file2.write(self.binaryBlock)
        file2.close()
    
    
    def decRawLDPC(self, filename, designs):
        file1 = open(filename,'r')        
        Lines = file1.readlines()        
        file1.close()
    
        binText = ""
        
        self.binaryStrings.clear()
        self.addressList.clear()
        self.domainValues.clear()

        for line in Lines:
            strLin = line.replace(", ","") ## Remove the comma and space
            strLin = strLin.replace(" ", "")
            # strLin = line.replace("\n","") ## Remove the comma and space
            #self.domainValues.append(strLin)
            
            binText += strLin[:-1]
            
            
            if len(binText) >= self.LDPC_N:
                # print("Length:" , len(binText), self.LDPC_N)    
                self.binaryStrings.append(binText)
                binText = ""
                
        
        dec = self.decodeLDPC(designs)
        
        self.binaryBlock = bytearray()
        
        for s in dec:        
            self.binaryBlock += int(s, 2).to_bytes(len(s) // 8, byteorder='big')
        
        
        file2 = open(self.outputFile,'wb')
        file2.write(self.binaryBlock)
        file2.close()
        

    def decRaw2LDPC(self, filename, designs):
        self.binaryStrings.clear()
        self.addressList.clear()
        self.domainValues.clear()
        
        binText = ""
    
        with open(filename, newline='') as f:
            reader = csv.reader(f)
            Kn = list(reader)
            
            for rows in Kn:
                nr = []
                for cols in rows:
                    try:
                        nbit = float(cols)
                        
                        if nbit > 0:
                            binText += "1"
                        else:
                            binText += "0"
                        
                    except:
                        None
                
                
        
        self.binaryStrings.append(binText)        
        
        dec = self.decodeLDPC(designs)
        
        self.binaryBlock = bytearray()
        
        for s in dec:        
            self.binaryBlock += int(s, 2).to_bytes(len(s) // 8, byteorder='big')
        
        
        file2 = open(self.outputFile,'wb')
        file2.write(self.binaryBlock)
        file2.close()
        
    def decRawListLDPC(self, Kn, designs):
        self.binaryStrings.clear()
        self.addressList.clear()
        self.domainValues.clear()
        
        binText = ""
    
#        Kn = list(reader)
        
        for rows in Kn:
            nr = []
            for cols in rows:
                try:
                    nbit = float(cols)
                    
                    if nbit > 0:
                        binText += "1"
                    else:
                        binText += "0"
                    
                except:
                    None
                
                
        
        self.binaryStrings.append(binText)        
        
        dec = self.decodeLDPC(designs)
        
        self.binaryBlock = bytearray()
        
        for s in dec:        
            self.binaryBlock += int(s, 2).to_bytes(len(s) // 8, byteorder='big')
        
        
        file2 = open(self.outputFile,'wb')
        file2.write(self.binaryBlock)
        file2.close()
        
        
        



        
