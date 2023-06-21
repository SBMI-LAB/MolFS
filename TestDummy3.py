# -*- coding: utf-8 -*-
"""
Test for create a file structure 
by importing files
"""
import shutil

from MolFS.MolFSGen import *
#from MolFS.Interface.seqNAM import *
#from MolFS.MolDevice import *


samplePath= "ExampleFiles/"

fs = MolFS("seqnam")
# Replace dummy with your molecular device interface


fs.StartFS("TestSession1")  # Create FS and new session

fs.mkdir("Figures")
fs.cd ("Figures")

fs.add(samplePath+"JSNN_Logo.svg")

fs.setUseZlib(True)  #Activates/deactivates compression

fs.CloseSession()



fs = MolFS("seqnam")
fs.StartFS("TestSession2")
fs.mkdir("Figures")
fs.cd("Figures")
fs.add(samplePath+"JSNN_Logo_V2.svg")
fs.setUseZlib(True)
fs.CloseSession()
#
#
#

fs = MolFS("seqnam")
fs.StartFS("TestSession3")
fs.mkdir("Figures")
fs.cd("Figures")
fs.add(samplePath+"JSNN_Logo_V3.svg" )
fs.mkdir("Text")
fs.cd("Text")

fs.add(samplePath + "Title.txt")

fs.setUseZlib(True)
fs.CloseSession()
#
#

fs = MolFS("seqnam")
fs.StartFS("TestSession4")
fs.mkdir("Figures")
fs.cd("Figures")
fs.add(samplePath+"JSNN_Logo_V4.svg")
fs.mkdir("Text")
fs.cd("Text")
fs.add(samplePath+"Title_S2.txt" )

fs.setUseZlib(True)
fs.CloseSession()
#
#

fs = MolFS("seqnam")
fs.StartFS("TestSession5")
fs.mkdir("Figures")
fs.cd("Figures")
fs.add(samplePath+"JSNN_Logo_V5.svg")
fs.cd("..")
fs.mkdir("Text")
fs.cd("Text")

fs.add(samplePath+"Title_S3.txt")
fs.setUseZlib(True)
fs.CloseSession()
