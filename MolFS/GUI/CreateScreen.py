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


class CreateScreen(QtWidgets.QFrame):
    
    
    MainUi = None
    
    current = 0
    
    def __init__(self):
        super(CreateScreen, self).__init__()
        uic.loadUi('GUI/CreateScreen.ui', self)
        
    
    def setMainUi(self, mainui):
        self.MainUi = mainui
#        self.createMenus()
        self.connectActions()
        self.Tabs.setStyleSheet("QTabBar::tab {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
        
    
    def Reset(self):
        self.current = 0
        self.Tabs.setCurrentIndex(self.current)
        self.DriveName.Text = ""
        self.warningLabel.Text = ""
        self.warningLabel.hide()
        
        self.backBtn.setEnabled(False)
        
    def connectActions(self):
        self.nextBtn.clicked.connect(self.Next)
        self.backBtn.clicked.connect(self.Back)
        self.cancelBtn.clicked.connect(self.Cancel)
        

    def Next(self):

        if self.current == 0:
            if self.Validate():
                self.current = 1
                self.Tabs.setCurrentIndex(self.current)
                self.nextBtn.setText("Finish")
                self.backBtn.setEnabled(True)
            
        elif self.current == 1:
            print("Finish!")
            self.CreateSystem()
        
        
            
        
    def Back(self):
        if self.current == 1:
            self.current = 0
            self.Tabs.setCurrentIndex(self.current)
            self.nextBtn.setText("Next")
            self.backBtn.setEnabled(False)
        
        
    def Cancel(self):
        ...
        
    def Validate(self):
        passed = False
        # Check the drive name
        
        messages = ""
        
        dname = self.DriveName.text()
        
        if " " in dname:
            messages += "Spaces are not allowed in the Drive name"
            
        
        if messages != "":
            self.warningLabel.setText(messages)
            self.warningLabel.show()
            
        else:
            passed = True
            self.warningLabel.hide()
            
        
        
        return passed            
        
        
        
    def CreateSystem(self):
        ## this is after all validations
        
        
        # Finish with opening the file system
        self.MainUi.OpenFromFolder()
        
        