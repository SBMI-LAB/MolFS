# -*- coding: utf-8 -*-

# Defines a Molecular Device
# Creates an interface

#from Interface.seqnam import *
import sys

sys.path.insert(1,"MolFS/Interface")

class MolDevice:
    
    
    def __init__(self, devtype = "seqnam"):
        self.devtype = devtype
        
        self.Active = False ## No device detected
        
        self.mDevice = None
        
        self.encodeParam = [0]
        
        self.selectDevice()
        #self.readDevice()
        
    
    def selectDevice(self):
        
        rname = self.devtype
        name =  "MolFS.Interface." + self.devtype
        
        try:
            mod = __import__ (name, fromlist=[''])
            self.mDevice = mod.MolFSDev()
            self.Active = True
            
            print("Device " + rname + " initialized")
            
        except:
            print("Error loading module " + rname)
        
            
        
        
    
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
            self.mDevice.encode(file_in, file_out)
            self.encodeParam[0] = self.mDevice.encodeParam
        else:
            print("Device is not ready")
    
    def decode (self, file_in, file_out):
        if self.Active:
            self.mDevice.decode(file_in, file_out)
        else:
            print("Device is not ready")
            
    def simulate (self, file_in, file_out):
        if self.Active:
            self.mDevice.simulate(file_in, file_out)
        else:
            print("Device is not ready")
    
    def setDecodeParam(self, param):
        self.mDevice.decodeParam = param
        
        

