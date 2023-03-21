#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 16:08:22 2022

@author: acroper
"""
import sys
import os
from MolFSGen import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)))     ## Put the MolFS library path

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject

from GUI.StartupScreen import *
from GUI.FileBrowser import *
from GUI.CreateScreen import *
from GUI.CreateFromPoolScreen import *




class MolFSUi(QtWidgets.QMainWindow):
    
    
    
    def __init__(self):
        super(MolFSUi, self).__init__()
        uic.loadUi('GUI/MOLFS_GUI_MW.ui', self)
        self.show()
#        self.showMaximized()
        
        self.FS = None
        
        self.ScreenBox = QHBoxLayout()
        self.ScreensFrame.setLayout(self.ScreenBox)
        self.currentScreen = None
        
        self.loadScreens()
        
        self.showScreen(0) ## Init screen
        
        
    def SetScreen(self, screen):
        if self.currentScreen != None:
            self.ScreenBox.removeWidget(self.currentScreen)
            self.currentScreen.hide()
        
        self.ScreenBox.addWidget(screen)
        
        self.currentScreen = screen
        self.currentScreen.show()
        
        
        
    def loadScreens(self):

        self.Screens = []
        
        self.InitScreen = StartupScreen()
        self.InitScreen.setMainUi(self)
        
        self.FileBrowser = FileBrowser()
        self.FileBrowser.setMainUi(self)
        
        self.CreateScreen = CreateScreen()
        self.CreateScreen.setMainUi(self)
        
        self.CreateFromPoolScreen = CreateFromPoolScreen()
        self.CreateFromPoolScreen.setMainUi(self)

        
        self.Screens.append(self.InitScreen)  #0
        self.Screens.append(self.FileBrowser) #1
        self.Screens.append(self.CreateScreen) #2
        self.Screens.append(self.CreateFromPoolScreen) #3
        
        
#        self.ScreenBox.addWidget(self.InitScreen)
        
    def showScreen(self, position):
        self.SetScreen(self.Screens[position])
        
    
    def aboutToQuit(self):
        QtCore.QCoreApplication.instance().quit()
        print("Exiting...")
        
        
    def openFolderNameDialog(self, location):
        title = "Select a folder"
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getExistingDirectory(self, title, location)
        if fileName:
            return fileName
        else:
            return ""         
        
    def OpenFromFolder(self):
        print("Opening folder")
        folderLocation = self.openFolderNameDialog("/tmp/MolFS")
        
        basename = os.path.basename(folderLocation)
        Descriptor = os.path.join(folderLocation,"Descriptor.molfs")
        if os.path.exists(Descriptor):
            #Load filesystem
            self.FS = MolFS()
            self.FS.LoadSystem(basename)
            
            self.showScreen(1)
        
    def OpenFileSystem(self):
        print("Opening system")
        self.showScreen(1)
    
    def OpenFromPool(self):
        print("Opening pool")
        self.showScreen(3)
        self.currentScreen.Reset()
        
    def CreateSystem(self):
        print("Creating system")
        self.showScreen(2)
        self.currentScreen.Reset()
        

app = QtWidgets.QApplication(sys.argv)
window = MolFSUi()
app.aboutToQuit.connect(app.deleteLater)
app.exec_()
