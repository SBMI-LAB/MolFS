# -*- coding: utf-8 -*-

import sys, os, shutil

from MolFSGen import *

class MolFSLoader:
    
    def __init__(self):
        self.Location = ""
        
        self.fstype = ""
        self.fsname = ""
        self.compressed = False
        self.flags = False
        self.LastSession = "-1"
        
    
    def SaveSystem(self, fs):
        savefile = os.path.join(fs.FSPath, "Descriptor.molfs")
        
        outFile = open(savefile,'w')
        
        outFile.write("<MolFS>\n")
        outFile.write("<fstype='"+fs.mDevice.devtype+"'>\n")
        outFile.write("<fsname='"+fs.Name+"'>\n")
        outFile.write("<compressed='"+str(fs.UseZLib)+"'>\n")
        outFile.write("<flags='"+str(fs.UseFlags)+"'>\n")
        outFile.write("<LastSession='"+str(len(fs.Sessions))+"'>\n")
        
        outFile.write("</MolFS>")
        
        outFile.close()
        
    def LoadSystem(self, fs):
        
        savefile = os.path.join(fs.MolPath,fs.Name, "Descriptor.molfs")
        
        if os.path.exists(savefile):
            print("File system exists")
            inFile = open(savefile,'r')
            Lines = inFile.readlines()
            
            for line in Lines:
                if 'fstype' in line:
                    self.fstype = line[9:-3]
                    print(self.fstype)
                    
                if 'fsname' in line:
                    self.fsname = line[9:-3]
                    print(self.fsname)
                
                if 'compressed' in line:
                    self.compressed = line[13:-3]
                    print(self.compressed)
                    
                if 'flags' in line:
                    self.flags = line[8:-3]
                    print(self.flags)
                    
                if 'LastSession' in line:
                    self.LastSession = line[14:-3]
                    print(self.LastSession)
                    
            
            self.StartSystem(fs)
            

            
    def StartSystem(self, fs):
        fs.restartDevice(self.fstype)
        fs.StartFS(self.fsname)
        
        # Reset the flags
        if self.flags == "True":
            fs.setUseFlags(True)
        else:
            fs.setUseFlags(False)
            
        if self.compressed == "True":
            fs.setUseZlib(True)
        else:
            fs.setUseZlib(False)
            
        sessions = -1
        # Number of sessions
        try:
            sessions = int(self.LastSession)
        except:
            sessions = -1
        
        
        for k in range(sessions):
            fs.CurrentSession.FS = fs
            fs.CurrentSession.reloadSession()
            
            for nblock in fs.CurrentSession.Root.blocks:
                if fs.UseFlags:
                    nblock.setFlags()
                else:
                    nblock.unsetFlags()
                
                nblock.useZlib = fs.UseZLib
                    
            
            fs.Root.readSession(fs.CurrentSession.Previous)
            
            
            if k < sessions-1:
                fs.CreateSession()
            # break
                
            
    def AddFastQFiles(self, fs, fastqfolder):
        ###
        # MolFS will use the fastq files and talk
        # with the interface.
        # The interface must provide a pre-processing step
        # Then, the files will be sorted by pool
        # and by Session 
        # And MolFS will attempt to recover the files
        fs.mDevice.ProcessFastQ(fastqfolder)
        
        

        
    
          
                
        
    
