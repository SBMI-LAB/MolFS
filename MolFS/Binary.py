# -*- coding: utf-8 -*-

### Binary operations
import subprocess
import os
import shutil
import gzip

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
    
# -*- coding: utf-8 -*-

### DiffScript

def genPatch (Original, Modified, Patch, Device):
    
    if Device.devtype == "dmos":
        ### Copy to tmp folder and process there
        OrigFile = "/tmp/OrigFile"
        ModFile  = "/tmp/ModFile"
        TextToMyers(Original, OrigFile )
        TextToMyers(Modified, ModFile)
      
        Original = OrigFile
        Modified = ModFile  ## Replace names of the variables
        
        
        

    subprocess.run("diff -a --minimal " + Original + "  " + Modified +  " > " + Patch, shell = True )
    
    ### Check the file
    size = os.stat(Patch).st_size
    
    if size > 0:
        return True
    else:
        return False
    


def restorePatch (Original, Patch, Device):
    # Original = os.path.join("Original", filename)
    # Patch = os.path.join("Patches", filename2+".patch")
    # Restored = os.path.join("Reconstructed", filename2)
    
    if Device.devtype == "dmos":
        ### Copy to tmp folder and process there
        OrigFile = "/tmp/OrigFile"
        TextToMyers(Original, OrigFile )
        Original2 = Original # backup filename
        Original = OrigFile
    
    
    Restored = "/tmp/RestoredPatch"
    
    subprocess.run("patch " + Original + " -i " + Patch +  " -o " + Restored , shell = True)
    
    shutil.copyfile(Restored, Original)
    
    if Device.devtype == "dmos":
        MyersToText(Original, Original2)
    
    

def restorePatch2 (filename, filename2, outputfile):
    Original = filename
    Patch =  filename2
    Restored = outputfile
    
    subprocess.run("patch " + Original + " -i " + Patch +  " -o " + Restored , shell = True)
    
    
def TextToMyers(filename, outputfile):
    ### Transforms spaces of text file to Enters
    ## To reduce cost of Myers algorithm
    file = open(filename,'r')
    output = open(outputfile,'w')
    
    lines = file.readlines()
    
    n = len(lines)
    k = 0
    
    ## Each line has an enter
    ## Lets re encode in term of lines
    for line in lines:
        k2=line.split(" ")
        for nk in k2:
            output.write(nk+"\n")
        
        k = k+1
        if k<n:
            output.write(chr(143))   ## This is a real enter   
    
    
    file.close()
    output.close()
    

def MyersToText(filename, outputfile):
    ### Transforms modified file after restoring to 
    ## The original formatting
    file = open(filename,'r')
    output = open(outputfile,'w')
    
    lines=file.readlines()
    
    for line in lines:
        
        nline = line.split(chr(143))
        n = len(nline)
        k=0
        
        
        
        for kline in nline:
            
            k=k+1
            if k<n:
                output.write(kline[:-1]+"\n")
            else:
                output.write(kline[:-1]+" ")
        
    output.close()
    file.close()
    
    
def fastqread(file):
    
    fqfile = open(file,'r')
    lines = fqfile.readlines()
    fqfile.close()
    pos = 1
    
    seqs = []
    for line in lines:
        if pos == 2:
            seqs.append(line)
        pos = pos + 1
        
        if pos == 5:
            pos = 1
    
    return seqs

def fastqgzread(file):
    
    fqfile = gzip.open(file, 'r')
    lines = fqfile.readlines()
    fqfile.close()
    pos = 1
    
    seqs = []
    for line in lines:
        
        if pos == 2:
            line = line.decode('utf-8')
            seqs.append(line)
        pos = pos + 1
        
        if pos == 5:
            pos = 1
    
    return seqs
    

