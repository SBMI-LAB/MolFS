# -*- coding: utf-8 -*-

### Binary operations


def binaryRead(filename):
    ## Read a whole binary file in memory and
    ## Returns the content
    f = open(filename, 'rb')  # Read binary file
    content = f.read()
    f.close()
    
    return content
    
    
def binaryWriteHex(block, outFile):
    # Receives a block and generates a Hex file
    f = open(outFile,'w') # Open to write
    
    for k in range(len(block)):
        if (block[k]<16):
            f.write("0")
        f.write( hex(block[k]).upper()[2:] )
        f.write(" ")
        
    f.close()
        

def HexRead(inFile):
    ## Receive a Hex file, read and convert to binary
    f = open(inFile,'r') # Read text file
    cont = f.read()
    f.close()
    cont = bytearray.fromhex(cont)
    
    return cont


def binaryWrite(content, filename):
    # Receives the content of a file and store in disc
    f = open(filename, 'wb') # Write binary
    f.write(content)
    f.close()
    
    
def dprint(text):
    print(text)