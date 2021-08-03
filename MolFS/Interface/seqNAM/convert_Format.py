#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 17:07:26 2021

@author: acroper
"""
import sys
import argparse

import csv
import os.path

def convertFormat(inputFile, outputFile):
    
    print("Converting file to FastQ...")
    
    if os.path.exists(inputFile):
    
        Salida = open(outputFile, "w")
        
        k = 0
        with open(inputFile, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                linea = row['sequence']
                
                Salida.write("@Seq"+ str(k) + "\n")
                Salida.write(linea)
                Salida.write("\n+\n")
                Salida.write(linea)
                Salida.write("\n")
                k+=1
        
        
        
        
        Salida.close()



def main (args = None):
    
 
   
    filein = args[0]
    fileout = args[1]
        

    convertFormat(filein, fileout)
    

if __name__ == '__main__':
    main(sys.argv[1:])            
    