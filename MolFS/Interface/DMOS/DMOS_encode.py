# -*- coding: utf-8 -*-
"""
Encode digital data to DMOS
"""
from reedsolo import RSCodec, ReedSolomonError

import numpy as np

# from DMOS_address import *
import os
import subprocess
import math
import xlrd


class DMOSEnc:


    outputFile = "DMOS_LDPC_Hex.txt"
    
    Address = 0
    
    FileOut = None
    
    RS_ECS = 8
    
    LDPC_N = 8*8

    TemplateIDs = []

    def __init__(self):
        
        self.getTemplateIDs()

    def getTemplateIDs(self):
        workbook = xlrd.open_workbook( os.path.dirname(os.path.abspath(__file__)) + "/Library/NewTemplates.xls")

        sh = workbook.sheet_by_name("Templates")
        for rownum in range(1,sh.nrows):
            row_valaues = sh.row_values(rownum)
            self.TemplateIDs.append(row_valaues[2])        

    def encodeAddress(self,number):
        ## Generate an address by shuffling the order of mutational domains
        bnumber=format(number, '#044b')[2:]
                       
        base = 16
        numbers = []
        for k in range(0,base):
            numbers.append(k)
        n=base
        Nm = number
        S= []
        perNum = ""
        for i in range(1,n+1):
            j = math.floor( Nm / math.factorial(n-i) )
            
            # Kn =  math.remainder(Nm, math.factorial (n-i))
            Kn =  Nm % math.factorial (n-i)
#            print (i, j, n-i, math.factorial(n-i), Kn, Nm)
            if j > 0:
                perNum += hex(numbers[j])[2:]
                numbers.remove(numbers[j])
#                Nm =  abs(math.remainder(Nm, math.factorial (n-i)))
#                Nm =  math.remainder(Nm, math.factorial (n-i))
                Nm = Nm % math.factorial (n-i)
            else:
                perNum += hex(numbers[j])[2:]
                numbers.remove(numbers[j])
        
#        print(bnumber)        
        return perNum
    
    
    
    def Hex2MD(self, data):
        """
        data is 2 bytes in binary
        16 bits
        Converts the 2 bytes into human readable commands for DMOS
        """
        s = []
        h = []
        
        for byten in data:
            nd = format(byten, '#010b')
            ns = nd[2:]  
#            print(byten, ns)                      
            for nbit in ns:
                if nbit == '1':
                    s.append(1)
                else:
                    s.append(0)
        
        self.FileOut.write("HEX:"+format(data[0],'02X')+format(data[1],'02X')+"\n")
        ## Prepare the output file ##
        #self.FileOut.write("Integer:      ["+ str(data[0]) + "][" + str(data[1])  + "]\n")
        # self.FileOut.write("ASCII symbol: [" + chr(data[0]) + "][" + chr(data[1]) + "]\n")
        #self.FileOut.write("Hex symbol: [" + format(data[0],'02X') + "][" + format(data[1],'02X') + "]\n")
        self.FileOut.write("Binary data: " + str(s) + "\n")
        
  
        # k = 0
        # for nbit in s:
        #     if nbit == 1:
        #         strng = "Add Mutation " + str(k+1)+"\n"
        #         self.FileOut.write(strng)

        #     k += 1

            
        ## End basic 16 bit encode   
            
    def adjust(self,text):
        """
        Adjust the length of an input text to the 8 byte constrain for Reed Solomon
        """
        n = len(text)
        
        adj = ""
        
        if n <= 8:
            for k in range(8-n):
                adj += " "
        
        text = text +  adj.encode()
        return text
        
        
    def encodeRS(self, data):
        """
        Basic Reed-Solomon encoder
        Encodes the input data (8 bytes) and generates 8 bytes of parity
        Capable of correct up to 4 bytes in error
        """
        rsc = RSCodec(self.RS_ECS)
        r = rsc.encode(data)
        
        return list(r)
    
    
    
    def writeAddress(self, strAddress):
        """
        Write in a human readable the address generated
        """
        #self.FileOut.write("DMOS word "+str(self.Address+1)+" \nDomains order: " + strAddress+ "\n")
        self.FileOut.write("DMOS word "+str(self.Address+1)+ "\n")
        if (len(self.TemplateIDs) > self.Address):
            self.FileOut.write("Template_ID: " + self.TemplateIDs[self.Address] + "\n")
        
    
    def write_DMOS(self, data):
        
        """
        Splits the data into groups
        of 2 bytes and send the output
        """
        
        
        n = math.ceil(len(data)/2)
        
        for k in range(n):
            grp = list(data[2*k:2*k+2])  ## 2 bytes
            
            strAddress = self.encodeAddress(self.Address)  # Get address
            self.writeAddress(strAddress) # Write address
            self.Hex2MD(grp)  # Write groups
            
            self.Address += 1
            
            self.FileOut.write("\n")

    
    def encodeFileRS(self, filename, address=0):
        """
        Encode the contents of a file using Reed-Solomon 1D Layer
        """ 
        self.FileOut = open(self.outputFile, "w")
        
        
        self.Address = address
        
        f = open(filename, 'rb')  # Read binary file
        content = f.read()
        f.close()
        
        ### Create groups of 8 bytes
        
        n = math.ceil(len(content)/8)
        
        for k in range(n):
#            grp = content[8*k:8*k+8]
            grp = self.adjust(content[8*k:8*k+8])
            # print(grp)
            
            ncode = self.encodeRS(grp)
            
            self.write_DMOS(ncode)
            
        
        self.FileOut.close()  
        
    
    def encodePlainRS(self, filename, address=0):
        """
        Encode the contents of a file using Reed-Solomon 1D Layer
        """ 
        self.FileOut = open(self.outputFile, "w")
        
        
        self.Address = address
        
        f = open(filename, 'rb')  # Read binary file
        content = f.read()
        f.close()
        
        ### Create groups of 8 bytes
        
        n = math.ceil(len(content)/8)
        
            
        ncode = self.encodeRS(content)
        
        self.write_DMOS(ncode)
            
        
        self.FileOut.close()    
    
    def encodeRS2D(self, filename):
        """
        Encode the contents of a file using Reed-Solomon 2D Layer
        This function returns the encoded data
        That can be used to be writen in a file
        """ 
        Encoded = []
        
            
        f = open(filename, 'rb')  # Read binary file
        content = f.read()
        f.close()
   
        
        ### Create groups of 8 bytes
        
        n = math.ceil(len(content)/8)
        
        words = []
        
        for k in range(n):
            ## Adjust to 16 bytes
            grp = self.adjust(content[8*k:8*k+8] )
            # print(grp)
            ncode = self.encodeRS(grp)        
            words.append(ncode) 
            
            Encoded.append(ncode)
      
        
            """
            Creating encode based on the already encoded words
            DMOS has 2 bytes
            [A B]
            Encode using 16 bits
            
            We need to build a matrix 8x16
            
            Then populate with the binary values row by row
            and then create the vectors from the columns
        
            """
    
            mdata = np.zeros((8,16))        
            grp = ncode
            ## join list
            L = grp
            ## Populate the matrix
            pos = 0
            k1=0
    #        print("Words:", len(grp[0]))
            for word in L:
    #            print(pos)
                nd = format(word, '#010b')
                ns = nd[2:]                        
                for nbit in ns:
                    if nbit == '1':
                        mdata[pos][k1] = 1
                    else:
                        mdata[pos][k1] = 0
                    k1 += 1
                
                if k1 == 16:
                    pos += 1
                    k1 = 0
            
            """
            Matrix generated
            """
    #        print("Matrix")
    #        print(mdata)
            
            ### Build characters from the columns of the matrix
            colData = []
            
            for c in range(16):
                colword = ""
                for r in range(8):
                    colword += str(mdata[r][c])[0]
                
                colData.append( int(colword, base=2) )
            
            ###
            """
            colData has the bits as bytes from the columns
            Now is ready to be encoded as RS
            Be aware, as data and redundancy [D][R] are
            generated, we only will add the redundancy part
            
            """
            R = []
            if len(colData )== 16:
                
                ncode1 = self.encodeRS(colData[0:8])
                ncode2 = self.encodeRS(colData[8:])
                
                R=ncode1[8:] + ncode2[8:]
    
            ## R contain nows the parity bits 
            print("ColData")
            print(colData)
            print("End ColData")
            Encoded.append(R)
                
      
        
        return Encoded   
    
    def encodeFileRS2D(self, filename, address=0):
        
        """
        Prepare the file to encode in 2D Reed-Solomon
        and write the encoded contents to the output file
        """
        
        encoded = self.encodeRS2D(filename)

        self.FileOut = open(self.outputFile, "w")
        self.Address = address

        for ncode in encoded:
            self.write_DMOS(ncode)
            print(list(ncode))
                
        
        self.FileOut.close()      
        


    def encodeLDPC(self, message, designs="LDPC01"):
        
        DevPath = "/home/acroper/Documents/NCAT/Research/DMOS/DMOS_System/FECC/LDPC"
        ldpc_path = os.path.join(DevPath,'ProtographLDPC','LDPC-library')
        ldpc_designs = os.path.join(DevPath,'ProtographLDPC','Designs')
        
        
        pathdir = "/tmp/LDPC/"
        
        if not os.path.exists(pathdir):
            os.makedirs(pathdir)
        
        filename =os.path.join(pathdir,"message.txt") 
#        print(filename)
        f = open( filename , 'w')
        f.write(message)
        f.close()    
        
        src_file = os.path.join(pathdir,"message.txt")
        out_path = os.path.join(pathdir,"encoded.txt")
        
        pchk_file = os.path.join(ldpc_designs, designs+".pchk")
        gen_file = os.path.join(ldpc_designs, designs+".gen")
    
        ldpc_encode_path = os.path.join(ldpc_path, 'encode.py')
        
        
            # first perform the encoding
        subprocess.run("python3 " + ldpc_encode_path + ' --pchk-file ' + pchk_file + ' --gen-file ' + gen_file +
                       ' --input-file ' + src_file + '  --output-file ' + out_path, shell=True)
        
#        print("python3 " + ldpc_encode_path + ' --pchk-file ' + pchk_file + ' --gen-file ' + gen_file +
#                       ' --input-file ' + src_file + '  --output-file ' + out_path)
        
        
        f = open(out_path,'r')
        encoded = f.read()
        f.close()
        
        return encoded
    
    
    def checkMsgSize(self, msg):
        FlagN = True
        if len(msg) < self.LDPC_N:
            d = self.LDPC_N - len(msg)
            for k in range(d):
                if FlagN:
                    msg += "0"
                else:
                    msg += "1"
#                FlagN = not FlagN
        return msg
    
    
    def encodeFileLDPC(self, filename, designs="LDPC01"):
        
        DevPath = "/home/acroper/Documents/NCAT/Research/DMOS/DMOS_System/FECC/LDPC"
        ldpc_path = os.path.join(DevPath,'ProtographLDPC','LDPC-library')
        ldpc_designs = os.path.join(DevPath,'ProtographLDPC','Designs')
        
        
        pathdir = "/tmp/LDPC/"
        
        if not os.path.exists(pathdir):
            os.makedirs(pathdir)
        
            
        f = open(filename, 'rb')  # Read binary file
        content = f.read()
        f.close()
        
        ### Create groups of n bits
        
        nb = self.LDPC_N/8
        
        n = math.ceil(len(content)/nb)
        
        words = []
        
        ### Message for LDPC
        filename =os.path.join(pathdir,"message.txt") 
        f = open( filename , 'w')        
        
        for k in range(n):
            ## Adjust to 16 bytes
            i1 =int(nb*k)
            i2 = int(nb*k+nb)
            grp = self.adjust(content[i1: i2] )
            msg = self.byteTobinStr(grp)
            msg = self.checkMsgSize(msg)
            f.write(msg + "\n")
            # print(grp)
            
        

#        f.write(message)
        f.close()    
        
        src_file = os.path.join(pathdir,"message.txt")
        out_path = os.path.join(pathdir,"encoded.txt")
        
        pchk_file = os.path.join(ldpc_designs, designs+".pchk")
        gen_file = os.path.join(ldpc_designs, designs+".gen")
    
        ldpc_encode_path = os.path.join(ldpc_path, 'encode.py')
        
        
            # first perform the encoding
        subprocess.run("python3 " + ldpc_encode_path + ' --pchk-file ' + pchk_file + ' --gen-file ' + gen_file +
                       ' --input-file ' + src_file + '  --output-file ' + out_path, shell=True)
        
#        print("python3 " + ldpc_encode_path + ' --pchk-file ' + pchk_file + ' --gen-file ' + gen_file +
#                       ' --input-file ' + src_file + '  --output-file ' + out_path)
        
        # try:
        f = open(out_path,'r')
        encoded = f.read().splitlines()
        f.close()
        try:
            os.remove(out_path)
            os.remove(out_path+".unpunctured")
        except:
            None
        #     f = open(out_path+".unpunctured",'r')
        #     encoded = f.read().splitlines()
        #     f.close()
            
        
        return encoded    
    
    def byteTobinStr(self, code):
        salida = ""
        for byten in code:
             nd = format(byten, '#010b')[2:]
             salida += nd
        return salida    
    
    def encodeToLDPC(self, messageASCII, designs = "LDPC01"):
        message = self.byteTobinStr(messageASCII.encode())
        s = self.encodeLDPC(message, designs)
        ## Back to bytes
        encoded = int(s, 2).to_bytes(len(s) // 8, byteorder='big')
        
        self.FileOut = open(self.outputFile, "w")
        

        self.write_DMOS(encoded)
        
        self.FileOut.close()              


    def encodeFile_LDPC_DMOS(self, filename, designs = "LDPC01"):
        
        lines = self.encodeFileLDPC(filename, designs)
        
        ## Back to bytes
        encoded = bytearray()
        for s in lines:
            encoded += int(s, 2).to_bytes(len(s) // 8, byteorder='big')
        
        self.FileOut = open(self.outputFile, "w")

        self.write_DMOS(encoded)
        
        self.FileOut.close()        
        
          
        

