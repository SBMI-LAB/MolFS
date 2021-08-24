# -*- coding: utf-8 -*-
import os 
import shutil

import pickle

import time

from MolFS.Binary import *
from MolFS.IndexFile import *
from MolFS.FileObjects import *

from MolFS.MolDevice import *




class MolFS:
    
    
    #Parameters
    
    #MolFS generates binary files for
    # Datablocks - DNA
    # Temporal Read Files
    # Temporal Input Files
    
    MolPath = "/tmp/MolFS/"
    

        
        
    
    def StartFS(self, Name):
        # Open or create a new FileSystem with the given name
        
        self.Name = Name
        
        self.FSPath = self.MolPath + self.Name + "/"
        
        self.WD = ""
        
        self.indexFile = IndexFile(Name)
        
        self.indexFile.IndexPool.Index = IndexFile("Temp")
        
        self.indexFile.FSPath = self.FSPath
        
        self.Root = self.indexFile.Root  ## Root folder
        
        self.CF = self.Root # Current folder
        
        self.EncodeTime = -1
        self.DecodeTime = -1
        
        self.pathtree = []
        # Check existence
        #if os.path.exists(self.FSPath):
        #    self.OpenFS()
        #else:
        
        ## Check existence
        binaryName = self.FSPath + "struct.data"
#        if os.path.exists(binaryName ):
#            with  open(binaryName ,'rb') as filehandle:
#                self = pickle.load(filehandle)
#        else:
        self.CreateFS()
        
        self.mDevice = MolDevice("seqnam")
        
        self.Root.mDevice = self.mDevice
        self.indexFile.IndexPool.mDevice = self.mDevice
        
        

    def CreateFS(self):
        # Create the file structure
        dprint("Create")
        
        
        ## Directory structure -- keep for updates
        
        # Path for the Pools - binary
        self.PoolsPath = self.FSPath + "Pools/"
        
        
        # Path for the binary input files
        self.SourcePath = self.FSPath + "Source/"
        
        # Path for the binary output files 
        self.OutputPath = self.FSPath + "Output/"
        
        self.Root.PoolsPath = self.PoolsPath
        self.indexFile.IndexPool.PoolsPath = self.PoolsPath
        
        self.InterfaceOut = self.FSPath + "Interface/Out"
        self.InterfaceIn = self.FSPath + "Interface/In"
        
        os.makedirs(self.FSPath, exist_ok = True)
        os.makedirs(self.PoolsPath, exist_ok = True)
        os.makedirs(self.SourcePath, exist_ok = True)
        os.makedirs(self.OutputPath, exist_ok = True)
        
        os.makedirs(self.InterfaceOut, exist_ok = True)
        os.makedirs(self.InterfaceIn, exist_ok = True)
        
        
        dprint("System created")
        
        self.OpenFS()
    
    def OpenFS (self):
        # Open the system
        dprint("Open")
        dprint("----------")
    
    def Check(self):
        # Check if filesystem has changed
        ...

    def Save(self):
        # Just save changes
        filename =  self.FSPath + "struct.data"
        with open(filename, 'wb') as filehandle:
            # store the data as binary data stream
            pickle.dump(self, filehandle)
        
    def WriteBlocks (self):
        
        t = time.time()
        # Create DataBlocks
        self.Root.genBlocks()
        
        self.indexFile.genIndexFile()
        
        toc = time.time()
        
        self.EncodeTime = toc-t
        
        
    
    def Sync (self):
        # Generate protocol
        ...

    # file management
    
    def pathWD (self, np = ""):
        #npwd = self.SourcePath + self.WD +"/"+ np
        npwd = self.SourcePath
        
        for k in self.pathtree:
            npwd = npwd + "/" + k + "/"
        npwd = npwd + np
        return npwd
    
    def buildWD(self):
        self.WD = ''
        for k in self.pathtree:
            self.WD = self.WD + "/" + k
    
    def pwd (self):
        return self.WD
       
    def cd (self, path):
        
        
        if path == "..":
            if len(self.pathtree) > 0:
                self.pathtree = self.pathtree[0:-1]
                self.buildWD()
                
                self.CF = self.CF.getParent()
                
                return self.WD
        else:   
            np = self.pathWD(path)
            if os.path.exists(np):
                self.pathtree.append(path)
                
                self.buildWD()
                
                self.CF = self.CF.getFolder(path)
                
                return self.WD
            else:
                dprint("Non existing directory")
                return None
        
    
    def mkdir(self, path):
        # try to create folder
        np = self.pathWD(path)        
        os.makedirs(np, exist_ok = True)
        
        self.CF.createFolder(path)
        
        

    def ls (self):
        np = self.pathWD()
        
        subfolders = [ f.name for f in os.scandir(np) if f.is_dir() ]
        
        for k in subfolders:
            print(k+"/")
            
        files = [ f.name for f in os.scandir(np) if f.is_file() ]
        
        for k in files:
            print(k) 
            
    
    def add(self, filename):
        
        if os.path.exists(filename): # path exists
            if os.path.isfile(filename): # is file
                npath = os.path.basename(filename) # cut path
                dpath = self.pathWD() + npath      # create relative path 
                
                self.CF.addNewFile(filename, dpath) # Add the file to the Current Folder CF

        else:
            print(filename, ": File doesn't exist")
            
    
    def addFolder(self, folder, restore = True):
        
        
        
        
        if restore:
            ubication = self.CF
        
        
        
        
        if os.path.isdir(folder):
            
            if folder[-1] != "/":
                folder += "/"
            
            foldername = os.path.basename(os.path.dirname(folder))
            
            self.mkdir(foldername)
            
            self.cd(foldername)
            
            for fold in os.listdir(folder):
                d = os.path.join(folder, fold)
                
                if os.path.isdir(d):
                    self.addFolder(d, False)
                else:
                    self.add(d)
                
            self.cd("..")
            
            
        if restore:
            self.CF = ubication
            
        
            
    def readAll(self):
        # Read all files of the filesystem
        # and write them to the output folder
        t = time.time()
        
        self.Root.readAllFiles(self.OutputPath)
        
        toc = time.time()
        
        self.DecodeTime = toc - t
                
            

    def countStrands(self):
        strands = 0
        
        size = 0
        
        for block in self.Root.blocks:
            lineas, lsize = block.countStrands()
            if lineas > 0:
                strands += lineas - 1
            
            size += lsize
                
        return strands, size
    
    
    def Stats(self):
        
        et = int(self.EncodeTime*100)/100
        dt = int(self.DecodeTime*100)/100
        
        blocks = len(self.Root.blocks)
        pools = self.Root.Pools
        
        
        print("------------------------------- ")
        print("\nMolecular File System - MOLFS\n")
        
        if et != -1:
            print("Encoding time:", et, "secods")
        if dt != -1:
            print("Decoding time:", dt, "secods")
            
        if et != -1:
            print("Blocks generated:" , blocks)
            print("Pools generated:" , pools)
            
            strands, size = self.countStrands()
            
            print("DNA strands:", strands)
            print("Binary use:", size, " bytes")
            
            
            
            
            
            

    