# -*- coding: utf-8 -*-
import sys, os 
import shutil

import pickle
import time


sys.path.append(os.path.dirname(os.path.abspath(__file__)))     ## Put the MolFS library path


from Binary import *
from IndexFile import *

# from FileObjects import *
from Folder import *

from MolDevice import *
from Session import *
from MolFSLoader import *



class MolFS:
    
    
    #Parameters
    
    #MolFS generates binary files for
    # Datablocks - DNA
    # Temporal Read Files
    # Temporal Input Files
    
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
    
        
    def __init__(self, devType = ""):
        
        if devType != "":
            self.mDevice = MolDevice(devType.lower())
        
        
        
        
        self.InitSession = None
        self.CurrentSession = None
        self.EncodeTime = -1
        self.DecodeTime = -1   
        self.Name = "Test"
        
        self.GlobalIndex = None
        
        self.UseZLib = False
        
        self.UseFlags = True
        
        self.Sessions = []
        
        self.Loader = MolFSLoader()
        
        self.ImportedFastQ = 0
        
        
    def restartDevice(self, devType):
        self.mDevice = MolDevice(devType.lower())
        
    
    def setUseZlib(self, value):
        self.UseZLib = value
        
    def setUseFlags(self, value):
        self.UseFlags = value
        
        
    def StartFS(self, Name = ""):
        # Open or create a new FileSystem with the given name
        
        if self.GlobalIndex == None:
            self.GlobalIndex = IndexFile(Name)
        
        if self.InitSession == None:        
            self.InitSession = Session()
            self.CurrentSession = self.InitSession
        else:
            nSession = Session(self.CurrentSession)
            
            self.CurrentSession = nSession
            
            
        self.Sessions.append(self.CurrentSession)
        
        self.CurrentSession.mDevice = self.mDevice
        
        self.CurrentSession.Create(Name)

        self.Name = Name
        
        self.FSPath = self.MolPath + self.Name + "/"
        
        self.WD = ""
        
        self.indexFile = self.CurrentSession.indexFile
        self.Root = self.CurrentSession.Root
        
        self.indexFile.SessionNumber = self.CurrentSession.number - 2
        self.indexFile.GlobalIndex = self.GlobalIndex
        
        
        # self.indexFile = IndexFile(Name)
        
        # self.indexFile.IndexPool.Index = IndexFile("Temp")
        
        # self.indexFile.FSPath = self.FSPath
        
        # self.Root = self.indexFile.Root  ## Root folder
        
        self.CF = self.Root # Current folder
        
        
        # self.CurrentSession.IndexFile = self.indexFile
        
        
        
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
        
        
        
        # self.CreateFS()
        
        self.getPaths()
        #self.mDevice = MolDevice(devType.lower())
        
        # self.Root.mDevice = self.mDevice
        # self.indexFile.IndexPool.mDevice = self.mDevice
        
    def changeSession(self, session):
        self.CurrentSession = session
        self.Root = self.CurrentSession.Root
        self.OutputPath = self.CurrentSession.OutputPath
    
    def getPaths(self):

        self.PoolsPath = self.CurrentSession.PoolsPath
        
        # Path for the Sessions
        self.CachePath = self.CurrentSession.CachePath
        
        # Path for the Current Session
        self.Current = self.CurrentSession.Current
        
        # Path for the binary input files
        self.SourcePath = self.CurrentSession.SourcePath
        
        # Path for the binary output files 
        self.OutputPath = self.CurrentSession.OutputPath
        
        self.Root.PoolsPath = self.CurrentSession.PoolsPath
        self.indexFile.IndexPool.PoolsPath = self.PoolsPath
        
        self.InterfaceOut = self.CurrentSession.InterfaceOut
        self.InterfaceIn = self.CurrentSession.InterfaceIn
        
    
    
    def CreateFS(self):
        # Create the file structure
        dprint("Create")
        
        
        ## Directory structure -- keep for updates
        
        # Path for the Pools - binary
        self.PoolsPath = self.FSPath + "Pools/"
        
        # Path for the Sessions
        self.CachePath = self.FSPath + "Cache/"
        
        # Path for the Current Session
        self.Current = self.FSPath + "Current/"
        
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


    def NewFS (self):
        # Open the system
        dprint("New FS")
        dprint("----------")
    
    def OpenFS (self):
        # Open the system
        dprint("Open FS from File")
        dprint("----------")
#        self.Loader.SaveSystem(self)
        
        
    def OpenPool (self):
        # Open the system
        dprint("Open FS from Pool")
        dprint("----------")
        

    def CloseSession(self):
        
        self.Root.setUseZlib(self.UseZLib)
        self.Root.setUseFlags(self.UseFlags)
        
        self.CheckDifferential()
        
        self.WriteBlocks()        
        self.MoveToPrevious()
        self.CurrentSession.Close()
        
        self.Loader.SaveSystem(self)
        

    def CheckDifferential(self):
        ### Recursively compare the files of the current session and previous session
        for file in self.GlobalIndex.files:
            
            CFile = file.localPath
            PFile = CFile.replace("Current", "Previous")
            
            print("Last session Path:", CFile)
            print("Previous session Path:", PFile)
            if os.path.exists(PFile): # path exists
                if os.path.isfile(PFile): # is file
                    ### Compare files
                    print("Comparing the two files")
                    patchFile =  self.CurrentSession.Patches + "Patch_F_" + str(file.Id) + "-S" +str(self.CurrentSession.number) + ".patch"
                    success = genPatch(PFile, CFile, patchFile, self.mDevice)
                    
                    if success:
                        ## Add the patchFile to the system
                        npath = os.path.basename(patchFile)
                        # self.Root.addNewFile(patchFile, self.CurrentSession.Current + npath)
                        self.Root.addPatchFile(patchFile, self.CurrentSession.Current + npath, file.Id)
            
            
        
    
    def MoveToPrevious(self):
        ### Copy files from current to previous session
        # self.Root.readAllFiles(self.CurrentSession.Previous)
        self.Root.readSession(self.CurrentSession.Previous)
        
    
    def CreateSession(self):
        self.StartFS(self.Name)
    
    
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
        
        self.Root.setFS(self)
        
        self.Root.genBlocks()
        
        #self.indexFile.SessionNumber = self.CurrentSession.number
        self.indexFile.FS = self
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
        
        ## Adjust
        if self.mDevice.devtype == "dmos":
            strandsn = (strands-len(self.Root.blocks))/5
            strands = round(strandsn)

        
        return strands, size
    
    
    def ExportSequences(self, csvFile):
        # Creates a CSV file, with the sequences
        
        OutFile = open(csvFile, 'w')
        
        for nSession in self.Sessions:
            # index and pool
            nPoolsPath = nSession.PoolsPath
            npools = os.listdir(nPoolsPath)
            
            for fpool in npools:
                dirPath = os.path.join(nPoolsPath, fpool)
                nblocks = os.listdir(dirPath)
                
                for nblock in nblocks:
                    if nblock.endswith(".dna"):
                        blockName = nblock[:-4]
                        nblock = os.path.join( dirPath, nblock )
                        SeqLists = self.mDevice.exportSequences(nblock)
                        
                        for seq in SeqLists:
                            OutFile.write(blockName + "," + seq )
                            if "\n" not in seq:
                                OutFile.write("\n")


        OutFile.close()


    
    def ExportFastQ(self, fastqFile):
        # Creates a FastQ file, with the sequences
        
        OutFile = open(fastqFile, 'w')
        
        for nSession in self.Sessions:
            # index and pool
            nPoolsPath = nSession.PoolsPath
            npools = os.listdir(nPoolsPath)
            
            for fpool in npools:
                dirPath = os.path.join(nPoolsPath, fpool)
                nblocks = os.listdir(dirPath)
                
                for nblock in nblocks:
                    if nblock.endswith(".dna"):
                        blockName = nblock[:-4]
                        nblock = os.path.join( dirPath, nblock )
                        SeqLists = self.mDevice.exportSequences(nblock)
                        
                        for seq in SeqLists:
                            OutFile.write("@\n")
                            OutFile.write( seq )
                            if "\n" not in seq:
                                OutFile.write("\n")
                            OutFile.write("+\n")
                            OutFile.write("$\n")
                            


        OutFile.close()        
    
    def LoadSystem(self, name):
        self.Name = name
        self.Loader.LoadSystem(self)
        
        
    def PreProcessFastQ(self, fastqfolder):
        
        Tmpfolder = os.path.join(self.CurrentSession.FastQCache, "FastQ_"+str(self.ImportedFastQ))
        try:
            os.mkdir(Tmpfolder)
        except:
            None
            
        self.ImportedFastQ += 1
        process = self.mDevice.PreProcessFastQ(fastqfolder, Tmpfolder)
        return process
    
    def ImportFastQ(self, fastqfolder):
        
        Tmpfolder = os.path.join(self.CurrentSession.FastQCache, "FastQ_"+str(self.ImportedFastQ))
        try:
            os.mkdir(Tmpfolder)
        except:
            None
        
        
        nfiles = os.listdir(fastqfolder)
        
        nk = 0
        
        for file in nfiles:
            fpath = os.path.join(fastqfolder, file)
            
            if ".fastq" in fpath :
                CFile = os.path.join(Tmpfolder, "Imported_"+str(nk)+".fastq")
                shutil.copy(fpath, Tmpfolder)
                
        
        self.ImportedFastQ += 1
        
    
    def ProcessFastQ(self):
        
        self.mDevice.importSequences(self.CurrentSession.FastQCache, self.CurrentSession.CachePath)
        
        # Next step: try to identify the sessions
#        for Session in self.Sessions:
        Session = self.CurrentSession
        
        if Session.FS == None:
            Session.FS = self
        Session.CheckSession()
        
        self.Sessions.pop(-1)
        self.CurrentSession = self.Sessions[-1]
        
        self.Loader.SaveSystem(self)
        
    
    def Stats(self):
        
        et = int(self.EncodeTime*100)/100
        dt = int(self.DecodeTime*100)/100
        
        blocks = len(self.Root.blocks)
        pools = self.Root.Pools
        
        time.sleep(0.1)
        print("------------------------------- ")
        print("\nMolecular File System - MOLFS\n")
        print("Device type: " + self.mDevice.devtype.upper())
        
        if self.CurrentSession != None:
            print("Last Session: ", self.CurrentSession.number )
            
        
        if self.mDevice.Active:
        
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
        else:
            print("Error opening device")
            
        return et, dt,  blocks, pools, strands, size            
            
            
            
            
            
            

    