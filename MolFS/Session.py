# -*- coding: utf-8 -*-

import sys, os 
import shutil

from Binary import *
from IndexFile import *
#from FileObjects import *
from MolDevice import *


class Session:
    
    ### Sessions folders
    
    ## MolFSRoot/Cache
    ## MolFSRoot/Cache/0     
    ## MolFSRoot/Cache/0/C0.bin
    ## MolFSRoot/Cache/1
    ## MolFSRoot/Cache/1/C0.diff
    ## MolFSRoot/Current/Documents/File0.doc
    ## MolFSRoot/Pools/bin/0/block0.bin 
    ## MolFSRoot/Pools/mol/0/block0.mol
    
    MolPath = "/tmp/MolFS/"
    
    number = 1
    
    Prev = None
    Next = None
    
    indexFile = None
    Root = None
    mDevice = None
        
    Status = "NAN"
    
    LastId = 0
    
    def __init__(self, prev=None):
        
        if prev != None:    ## Link the sessions
            pNumb = prev.number
            self.number = pNumb + 1
            self.Prev = prev
            prev.Next = self
            
            self.LastId = prev.LastId
            
            
    def Create(self, Name):
        # Create a session
        self.Name = Name
        
        self.FSPath = self.MolPath + self.Name + "/Session_" + str(self.number) + "/"
        
        self.indexFile = IndexFile(self.Name)
        self.indexFile.IndexPool.Index = IndexFile("Temp")
        self.indexFile.FSPath = self.FSPath
        self.indexFile.LastId = self.LastId
        
        self.Root = self.indexFile.Root  ## Root folder

        self.Root.mDevice = self.mDevice
        self.indexFile.IndexPool.mDevice = self.mDevice

        self.CreateFS()
        self.Status = "Open"
        
        
        if self.Prev != None:
            self.Root.lastBlock = self.Prev.Root.lastBlock
            
            
        

        
    def Open(self):
        # Open the session
        ...
        
        
    def Close(self):
        # Close the session
        self.LastId = self.indexFile.LastId
        self.Status = "Closed"
        
        
    def CreateFS(self):
        # Create the file structure
        dprint("Create")
        
        
        ## Directory structure -- keep for updates
        
        # Path for the Pools - binary
        self.PoolsPath = self.FSPath + "Pools/"
        
        # Path for the Sessions
        self.CachePath = self.FSPath + "Cache/"
        
        # Path for the Current Session
        self.Current = self.MolPath + self.Name + "/Current/"
        
        # Path for the Previous Session        
        self.Previous = self.MolPath + self.Name + "/Previous/"
        
        self.Patches = self.MolPath + self.Name + "/Patches/"
        
        
        # Path for the binary input files
        self.SourcePath = self.Current
        
        # Path for the binary output files 
        self.OutputPath = self.FSPath + "Output/"
        
        self.Root.PoolsPath = self.PoolsPath
        self.indexFile.IndexPool.PoolsPath = self.PoolsPath
        
        self.InterfaceOut = self.FSPath + "Interface/Out"
        self.InterfaceIn = self.FSPath + "Interface/In"
        
        os.makedirs(self.FSPath, exist_ok = True)
        os.makedirs(self.Current, exist_ok = True)
        os.makedirs(self.Previous, exist_ok = True)
        os.makedirs(self.Patches, exist_ok = True)
        os.makedirs(self.PoolsPath, exist_ok = True)
        os.makedirs(self.SourcePath, exist_ok = True)
        os.makedirs(self.OutputPath, exist_ok = True)
        
        #os.makedirs(self.InterfaceOut, exist_ok = True)
        #os.makedirs(self.InterfaceIn, exist_ok = True)
        
        
        """
        Newly created sessions are actually the current session.
        The source files must be copied first to the "current" folder.
        """
        
        
        dprint("System created")
        
      
        
        