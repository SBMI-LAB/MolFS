# -*- coding: utf-8 -*-

from MolFSGen import *

fs = MolFS()
fs.StartFS("Prueba")


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

#fs.add('/home/acroper/toma1.jpeg')

fs.add('/home/acroper/Text1.txt')
fs.add('/home/acroper/Text2.txt')

fs.Root.recursivePrint()

#fs.Save()

fs.WriteBlocks()