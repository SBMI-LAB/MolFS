#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to rebuild a file structure
from the Pools
"""

from MolFSGen import *

fs = MolFS()
fs.StartFS("Prueba")
fs.addFolder("/home/acroper/Documents/Tax")
fs.Root.recursivePrint()

fs.WriteBlocks()
# fs.readAll()
fs.Stats()

