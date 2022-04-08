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
    

def binText(inFile, outFile):
    # Converts a binary file into a text file, with new lines
    # each time
    
    lineSize = 1
    
    f = open(inFile, 'rb')
    content = f.read()
    f.close()
    
    f2 = open(outFile,'w')
    
    xl = 0
    
    for cbyte in content:
        f2.write(str(cbyte))
        xl+=1
        if xl >= lineSize:
            f2.write("\n")
            xl=0
        
    
    f2.close()
    
    
def dprint(text):
    print(text)