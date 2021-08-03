# -*- coding: utf-8 -*-

from MolFSGen import *
#from MolFS.Interface.seqNAM import *
from MolFS.MolDevice import *


fs = MolFS()
fs.StartFS("Tests")


fs.mkdir('Jorge')

fs.mkdir('Test')

fs.mkdir('Other')

fs.cd('Jorge')

#fs.mkdir('Inner_Jorge')
#
#fs.cd('..')
#
#fs.cd('Test')
#
#fs.mkdir('Test_folder')
#
#fs.cd("..")
#
#fs.cd("Jorge")
#
#fs.cd('Inner_Jorge')




fs.add('/home/acroper/toma1.jpeg')
fs.add('/home/acroper/testfile.jpg')
fs.add('/home/acroper/Text1.txt')
fs.add('/home/acroper/Text2.txt')




#fs.add('/home/acroper/testfile.jpg')


fs.Root.recursivePrint()

#fs.Save()

fs.WriteBlocks()



#filname="/tmp/MolFS/Tests/Pools/Pool_1_Block_40.dna"
#fs.mDevice.decode(filname, filname+".dec.bin")


fs.readAll()


#mdev = MolDevice("seqnam")

#mdev.encode("MolFS/Interface/tests/testfile.jpg","MolFS/Interface/tests/testfile.dna")
#mdev.simulate("MolFS/Interface/tests/testfile.dna","MolFS/Interface/tests/testfile.fastq")
#mdev.decode("MolFS/Interface/tests/testfile.fastq","MolFS/Interface/tests/testfileOut.jpg")