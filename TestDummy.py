# -*- coding: utf-8 -*-

from MolFS.MolFSGen import *



samplePath= "/home/acroper/Documents/NCAT/Research/DMOS/DMOS_System/Diff/Assembly/Versions4/"


fs = MolFS("dummy")
fs.StartFS("dummyTest")


fs.mDevice.encode("/tmp/TestFile.txt", "/tmp/TestFile.dna")


fs.mDevice.decode("/tmp/TestFile.dna", "/tmp/TestFileDec.txt")

