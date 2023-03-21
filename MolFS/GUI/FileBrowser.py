#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 16:08:22 2022

@author: acroper
"""

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject
import sys, os


class FileBrowser(QtWidgets.QFrame):
    
#    LoadFolder = pyqtSignal()
#    LoadPool = pyqtSignal()
#    LoadSystem = pyqtSignal()
#    CreateSystem = pyqtSignal()
#    
#    FSPath = ""
#    
#    Sysmode = ""
    
    MainUi = None
    
    def __init__(self):
        super(FileBrowser, self).__init__()
        uic.loadUi('GUI/FileBrowser.ui', self)
#        self.show()
        self.path = ""
        
    
    def setMainUi(self, mainui):
        self.MainUi = mainui
        self.createMenus()
        self.connectActions()
        self.populate()
        
    def populate(self):
        # This checks an existing file system
        self.path="/tmp/MolFS/Complete4/Current"
        self.cpath = self.path
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(QtCore.QDir.rootPath())
        
        # This adds the Name filters according to the system
        self.model.setNameFilters(["JSNN_Logo.svg", "Title.txt"])
        self.model.setNameFilterDisables(False)

        self.fileList.setModel(self.model)
        self.fileList.setRootIndex(self.model.index(self.path))
        
        self.fileList.clicked.connect(self.clickedItem)
        self.fileList.doubleClicked.connect(self.doubleClickedItem)
        
        
    def clickedItem(self, index):
        path = self.sender().model().filePath(index)
        print(self.path)
        
    def doubleClickedItem(self, index):
        path = self.sender().model().filePath(index)
        print("Opening")
        print(path)
        if os.path.isdir(path):
            self.fileList.setRootIndex(self.model.index(path))
            self.cpath = path
            
        
        
    
    def createMenus(self):
        ...
        
    def connectActions(self):
        self.upBtn.clicked.connect(self.UpFolder)
        self.newFolderBtn.clicked.connect(self.CreateFolder)
        self.importFileBtn.clicked.connect(self.ImportFile)
        self.closeSessionBtn.clicked.connect(self.CloseSession)
        self.importPoolBtn.clicked.connect(self.ImportPool)
        
    
    def UpFolder(self):
        
        if self.cpath != self.path:
            path = os.path.dirname(self.cpath)
            self.fileList.setRootIndex(self.model.index(path))
            self.cpath = path
            print(self.cpath, self.path)
        
        
        
    def CreateFolder(self):
        ...
        
    def ImportFile(self):
        ...
        
    def ImportPool(self):
        ...
        
    def CloseSession(self):
        ...
