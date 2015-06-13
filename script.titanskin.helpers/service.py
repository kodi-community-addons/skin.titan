#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xbmc
import xbmcaddon


__settings__ = xbmcaddon.Addon(id='script.titanskin.helpers')
__cwd__ = __settings__.getAddonInfo('path')
__addonversion__ = __settings__.getAddonInfo('version')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

from BackgroundsUpdater import BackgroundsUpdater
from LibraryMonitor import LibraryMonitor
from LibraryMonitor import Kodi_Monitor
from HomeMonitor import HomeMonitor

class Main:
    
    KodiMonitor = Kodi_Monitor()
    
    def __init__(self):
                   
        #start the extra threads
        homeMonitor = HomeMonitor()
        homeMonitor.start()
        
        backgroundsUpdater = BackgroundsUpdater()
        backgroundsUpdater.start()
        
        libraryMonitor = LibraryMonitor()
        libraryMonitor.start()
        
        while not self.KodiMonitor.abortRequested():
                     
            if self.KodiMonitor.waitForAbort(1):
                # Abort was requested while waiting. We should exit
                xbmc.log('TITANSKIN DEBUG --> shutdown requested !')         
        else:
            #stop the extra threads
            backgroundsUpdater.stop()
            libraryMonitor.stop()
            homeMonitor.stop()
    

xbmc.log('titan helper version %s started' % __addonversion__)
Main()
xbmc.log('titan helper version %s stopped' % __addonversion__)
