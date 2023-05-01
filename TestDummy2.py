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

fs = MolFS("dummy")
# Replace dummy with your molecular device interface


fs.StartFS("CompleteDummy")  # Create FS and new session

fs.mkdir("Figures")
fs.cd ("Figures")

fs.add(samplePath+"JSNN_Logo.svg")

fs.cd("..")

fs.setUseZlib(True)  #Activates/deactivates compression

fs.CloseSession()

#fs.readAll()
###
fs.CreateSession()
# ## Copy the new file version
shutil.copyfile(samplePath+"JSNN_Logo_V2.svg", fs.CurrentSession.Current + "/Figures/JSNN_Logo.svg" )
fs.CloseSession()
#
#
#
fs.CreateSession()

fs.mkdir("Text")
fs.cd("Text")

fs.add(samplePath + "Title.txt")
fs.cd("..")


shutil.copyfile(samplePath+"JSNN_Logo_V3.svg", fs.CurrentSession.Current + "/Figures/JSNN_Logo.svg" )
fs.CloseSession()
#
#
fs.CreateSession()

shutil.copyfile(samplePath+"JSNN_Logo_V4.svg", fs.CurrentSession.Current + "/Figures/JSNN_Logo.svg" )
shutil.copyfile(samplePath+"Title_S2.txt", fs.CurrentSession.Current + "/Text/Title.txt" )


fs.CloseSession()
#
#
fs.CreateSession()

shutil.copyfile(samplePath+"JSNN_Logo_V5.svg", fs.CurrentSession.Current + "/Figures/JSNN_Logo.svg" )
shutil.copyfile(samplePath+"Title_S3.txt", fs.CurrentSession.Current + "/Text/Title.txt" )
fs.CloseSession()

#
##fs.readAll()
#fs.ExportSequences("/tmp/Sequences.txt")  # To implement