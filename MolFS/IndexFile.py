# -*- coding: utf-8 -*-

from MolFS.FileObjects import *

class IndexFile:
    
    def __init__(self, name):
        
        self.Name = name
        
        self.Root = folder("")
        
        self.Root.Index = self
        
        self.files = []
        
    
    
    def addFiles(self, file):
        self.files.append(file)
    
    
    
    def readFS(self):
        # Read the existing file system
        ... 
        
        
    def saveFS(self):
        # Save the existing file system
        ...
        
    def genDataBlocks(self):
        # Generate the datablocks
        ...
        
        

