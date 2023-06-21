# -*- coding: utf-8 -*-

# Defines a Molecular Device
# Creates an interface

#from Interface.seqnam import *
import sys
import os
import pathlib

from Binary import *

sys.path.insert(1,"MolFS/Interface")

class MolDevice:
    
    
    def __init__(self, devtype = "seqnam"):
        self.devtype = devtype
        
        self.Active = False ## No device detected
        
        self.mDevice = None
        
        self.encodeParam = [0]
        
        self.selectDevice()
        
        self.Pool = 0
        
        self.Block = 0
        
        self.CacheList = []
        
        self.CacheFileList = []
        self.CacheNames = []
        
        self.RecursiveImport = False
        
        #self.readDevice()
        
    
    def selectDevice(self):
        
        rname = self.devtype
        name =  "Interface." + self.devtype
        
        try:
            mod = __import__ (name, fromlist=[''])
            self.mDevice = mod.MolFSDev()
            self.Active = True
            
            print("Device " + rname + " initialized")
            
        except Exception as e:
            print("Error loading module " + rname)
            print(e)
        
            
        
        
    
#    def selectDevice (self):
#        
#        if self.devtype == "seqnam":
#            self.mDevice = seqnam()
#            self.Active = True
#            print("Selected device: seqNAM")
#        
#        if self.devtype == "dmos":
#            print("DMOS is not yet ready")
#            self.Active = False
            
    
    def setAddress(self, Address):
        if self.Active:
            self.mDevice.Address = Address
        else:
            print("Device is not ready")            
        
    def getAddress(self):
        if self.Active:
            return self.mDevice.Address
        else:
            print("Device is not ready")
            return -1
    
    def encode(self, file_in, file_out):
        if self.Active:
            self.mDevice.Pool = self.Pool
            self.mDevice.Block = self.Block
            self.mDevice.encode(file_in, file_out)
            self.encodeParam[0] = self.mDevice.encodeParam
        else:
            print("Device is not ready")
    
    def decode (self, file_in, file_out):
        Result = False
        if self.Active:
            self.mDevice.Pool = self.Pool
            self.mDevice.Block = self.Block
            Result = self.mDevice.decode(file_in, file_out)
        else:
            print("Device is not ready")
        
        return Result
            
    def simulate (self, file_in, file_out):
        if self.Active:
            self.mDevice.simulate(file_in, file_out)
        else:
            print("Device is not ready")
    
    def setDecodeParam(self, param):
        self.mDevice.decodeParam = param
        
    def exportSequences(self, in_file):
        # Reads a block file
        # and returns the plain list of sequences
        Lists = self.mDevice.exportSequences(in_file)
        return Lists
    
    
    def getCacheFile(self, cPool, cBlock):
        # Get the cache file
        cacheName = "Pool_"+str(cPool)+"_Block_"+str(cBlock)+self.suffixCache+".fastq"
        
        cachefile = os.path.join(self.CacheFolder, cacheName)
        
#        if cacheName not in self.CacheList:
#            if os.path.exists( cachefile ):
#                try:
#                    os.remove( cachefile )
#                except:
#                    None
#        cFile = open(cachefile,'a')
        if cacheName not in self.CacheNames:
            cFile = open(cachefile,'w')
            if self.devtype == "seqnam":
                cFile.write("sequence\n")
                
            self.CacheNames.append(cacheName)
            self.CacheFileList.append(cFile)
        else:
            pos = self.CacheNames.index(cacheName)
            cFile = self.CacheFileList[pos]
        
        
        return cFile
        
        
    
    def writeToCache(self, seq):
        cPool, cBlock, oseq = self.mDevice.ClassifySequence(seq)
        
        if cPool >= 0 and cBlock >= 0:
            cFile = self.getCacheFile(cPool, cBlock)
            if len(oseq) > 50:
                if "\n" not in oseq:
                    cFile.write(oseq+"\n")
                else:
                    cFile.write(oseq)
#            cFile.close()
        else:
            self.skipSequences += 1
        

        
    
    def RecFastQSearch(self, in_folder, listings):
        
        ## Force to have a recursive search of the fastq files
        # to allow combine multiple folders when importing them
    
        listfolders = os.listdir(in_folder)
        
        for elem in listfolders:
            lelem = os.path.join(in_folder, elem)
            
            if os.path.isdir(lelem):
                self.RecFastQSearch(lelem, listings)
            else:
                if pathlib.Path(lelem).suffix == ".fastq":
                    listings.append(lelem)
    
    
    def importSequences(self, in_folder, out_folder):
        # Reads a folder with sequences files
        # and uses the interface to organize
        # the sequences to the corresponding blocks
        self.skipSequences = 0
        self.CacheFolder = out_folder
        
        self.suffixCache = ""
        if self.mDevice.DoubleStep:
            self.suffixCache = ".raw"
        
        # process format: fastQ, output: fastQ
        #listings = os.listdir(in_folder)
        
        if self.RecursiveImport:
            listings = []
            self.RecFastQSearch(in_folder, listings)
        else:
            listings = os.listdir(in_folder)
            
        
        
        Total = 0
        
        for file in listings:
            fastqfile = os.path.join(in_folder,file)
            passed=False
            
            if '.fastq.gz' in file:
                sequences = fastqgzread(fastqfile)
                passed = True
            elif '.fastq' in file:
                sequences = fastqread(fastqfile)
                passed = True
                
            if passed:
                ### Process the sequences
                for seq in sequences:
                    self.writeToCache(seq)
                    Total += 1
                    
        for cFile in self.CacheFileList:
            cFile.close()
            
        print("Skipped:", self.skipSequences , "/", Total)
                    
        
        
    def ProcessFastQ(self, fastqfolder, workpath):
        ### will call the interface to process the folder
        self.mDevice.ProcessFastQ(fastqfolder, workpath)
        
    def PreProcessFastQ(self, fastqfolder, workpath):
        process = self.mDevice.PreProcessFastQ(fastqfolder, workpath)
        return process
    
        
        

