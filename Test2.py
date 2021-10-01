# -*- coding: utf-8 -*-
"""
Test for create a file structure 
by importing files
"""


from MolFSGen import *
#from MolFS.Interface.seqNAM import *
#from MolFS.MolDevice import *


samplePath= "/home/acroper/Documents/NCAT/Research/DMOS/TestFiles/"
fs = MolFS()
fs.StartFS("Tests")
fs.mkdir('Texts')
fs.mkdir('Pictures')
fs.mkdir('Documents')
fs.mkdir('Videos')


fs.cd('Texts')
fs.add(samplePath+'Text1.txt')
fs.add(samplePath+'Text2.txt')

fs.cd('..')
fs.cd('Pictures')
fs.add(samplePath+'testfile.jpg')
fs.add(samplePath+'toma1.jpeg')
fs.add(samplePath+'jsnn-logo2.svg')

fs.cd('..')
fs.cd('Documents')
fs.add(samplePath+'2021_Research_Proposal_Jorge_Guerrero.pdf')
#fs.addFolder('/home/acroper/Documents/NCAT/Research/DMOS/TestFiles/Papers')


fs.cd('..')
fs.cd('Videos')
fs.add(samplePath+'JSNN-dean.mp4.zip')




fs.Root.recursivePrint()

#fs.Save()
#fs.TimerLog()

fs.WriteBlocks()




fs.readAll()


fs.Stats()

#mdev = MolDevice("seqnam")

#mdev.encode("MolFS/Interface/tests/testfile.jpg","MolFS/Interface/tests/testfile.dna")
#mdev.simulate("MolFS/Interface/tests/testfile.dna","MolFS/Interface/tests/testfile.fastq")
#mdev.decode("MolFS/Interface/tests/testfile.fastq","MolFS/Interface/tests/testfileOut.jpg")