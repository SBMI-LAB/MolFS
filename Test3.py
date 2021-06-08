#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 16:24:22 2021

@author: acroper
"""
import pickle

filename = "/tmp/MolFS/Prueba/struct.data"

with open(filename, 'rb') as filehandle:
    # read the data as binary data stream
    fs3 = pickle.load(filehandle)  
    

fs3.Root.recursivePrint()