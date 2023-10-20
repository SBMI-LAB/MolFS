# -*- coding: utf-8 -*-

from MolFS.MolFSGen import *

# This example


samplePath = "ExampleFiles/SeqNAM/"


fs = MolFS("seqnam")
fs.StartFS("TestRead_Filtered")
fs.setUseZlib(True)
fs.mDevice.RecursiveImport = True

fs.ImportFastQ(samplePath)

fs.ProcessFastQ()


# Restart the system
fs = MolFS()
fs.LoadSystem("TestLoad")


