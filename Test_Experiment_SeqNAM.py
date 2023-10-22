# -*- coding: utf-8 -*-

from MolFS.MolFSGen import *

# This procedure uses the nanopore sequenced data
# and needs to be filtered (Smith-waterman)
# We included a filter module, that requires to run on a Linux environment
# The module can be recompiled using Qt Creator to run on Windows or Mac
# located in the folder MolFS/Interface/SeqNAMFilter

# To test this experiment, download the sequenced data from
# https://trace.ncbi.nlm.nih.gov/Traces/?run=SRR26445816
# And uncompress them in the hard drive

# Configure samplePath as the folder containing the FastQ files

samplePath = "/tmp/SeqNAMReads/"


fs = MolFS("seqnam")
fs.StartFS("TestLoad")
fs.setUseZlib(True)
fs.mDevice.RecursiveImport = True


process = fs.PreProcessFastQ(samplePath)

print("Reading results...")
k = 0
while True:
    nextline = process.stdout.readline()
    ndec = nextline.decode()
    
    if "Progress" in ndec:
        ndec = ndec.replace("\n","")
        print( ndec)
        
    k+= 1
    if ndec == '' and process.poll() is not None:
        break
    
process.kill()


fs.ProcessFastQ()


# Restart the system
fs = MolFS()
fs.LoadSystem("TestLoad")


