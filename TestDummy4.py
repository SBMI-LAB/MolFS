# -*- coding: utf-8 -*-

from MolFS.MolFSGen import *


samplePath= "ExampleFiles/"


fs = MolFS("dummy")
fs.StartFS("TestLoad")
fs.setUseZlib(True)
fs.mDevice.RecursiveImport = True

fs.ImportFastQ(samplePath)

fs.ProcessFastQ()


# Restart the system
fs = MolFS()
fs.LoadSystem("TestLoad")


