#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 16:08:22 2022

@author: acroper
"""

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject
import sys


class StartupScreen(QtWidgets.QFrame):
    
    LoadFolder = pyqtSignal()
    LoadPool = pyqtSignal()
    LoadSystem = pyqtSignal()
    CreateSystem = pyqtSignal()
    
    FSPath = ""
    
    Sysmode = ""
    
    MainUi = None
    
    def __init__(self):
        super(StartupScreen, self).__init__()
        uic.loadUi('GUI/StartupScreen.ui', self)
#        self.show()
        
    
    def setMainUi(self, mainui):
        self.MainUi = mainui
        self.createMenus()
        self.connectActions()
    
    def createMenus(self):
        self.menu1 = QtWidgets.QMenu()
        self.fromPool = QAction("Load from Pool", self)
        self.fromFolder = QAction("Load from Folder", self)
        self.menu1.addAction(self.fromPool)
        self.menu1.addAction(self.fromFolder)
        self.LoadButton.setMenu(self.menu1)
        
        
        self.fromPool.triggered.connect(self.sfromPool)
        self.fromFolder.triggered.connect(self.sfromFolder)
        
        
        
        
        self.menu2 = QtWidgets.QMenu()
        self.dmosbt = QAction("DMOS", self)
        self.seqnambt = QAction("SeqNAM", self)
        self.menu2.addAction(self.dmosbt)
        self.menu2.addAction(self.seqnambt)
        
        self.CreateButton.setMenu(self.menu2)
        
        self.dmosbt.triggered.connect(self.startSystem)
        self.seqnambt.triggered.connect(self.startSystem)
        
        
        
    def connectActions(self):
        self.LoadFolder.connect( self.MainUi.OpenFromFolder  )
        self.LoadPool.connect( self.MainUi.OpenFromPool )
        self.LoadSystem.connect( self.MainUi.OpenFileSystem )
        self.CreateSystem.connect( self.MainUi.CreateSystem )
        
        
    def sfromPool(self):
        self.LoadPool.emit()
        
    def sfromFolder(self): 
        self.LoadFolder.emit()
        
    def sfromHistory(self): 
        self.LoadSystem.emit()
        
    def startSystem(self): 
        self.CreateSystem.emit()
        
        
        
        
        