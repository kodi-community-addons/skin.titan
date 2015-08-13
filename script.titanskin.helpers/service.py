#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xbmc, xbmcgui
import xbmcaddon


__settings__ = xbmcaddon.Addon(id='script.titanskin.helpers')
__cwd__ = __settings__.getAddonInfo('path')
__addonversion__ = __settings__.getAddonInfo('version')


class Main:
    
    win = None
    
    def __init__(self):
        
        listItem = None
        lastListItem = None
        mainMenuContainer = "300"
        self.win = xbmcgui.Window( 10000 )

        while not (KodiMonitor.abortRequested() or xbmc.abortRequested):
                        
            # monitor main menu when home is active
            if (xbmc.getCondVisibility("Window.IsActive(home) + !Window.IsActive(fullscreenvideo)")):

                #monitor widget window prop
                if self.win.getProperty("ShowWidget") == "show" and not xbmc.getCondVisibility("Window.IsActive(selectdialog) | Window.IsActive(shutdownmenu) | Window.IsActive(contextmenu)"):
                    self.showWidget()
                
                listItem = xbmc.getInfoLabel("Container(%s).ListItem.Label" %mainMenuContainer)
                if ((listItem != lastListItem) and xbmc.getCondVisibility("!Window.IsActive(selectdialog) + !Window.IsActive(shutdownmenu) + !Window.IsActive(contextmenu)")):
                    
                    # update the widget content
                    if (xbmc.getCondVisibility("!Skin.HasSetting(DisableAllWidgets) + !Skin.String(GadgetRows, 3)")):
                        
                        #spotlight widget
                        if xbmc.getCondVisibility("Skin.String(GadgetRows, enhanced)"):
                            self.setSpotlightWidget(mainMenuContainer)
                        
                        #normal widget
                        self.setWidget(mainMenuContainer)

                    lastListItem = listItem
  

            xbmc.sleep(150)

    def logMsg(self, msg, level = 1):
        doDebugLog = False
        if doDebugLog == True or level == 0:
            xbmc.log("Titanskin DEBUG --> " + msg)
    
    def showWidget(self):
        linkCount = 20
        while linkCount != 0 and not xbmc.getCondVisibility("ControlGroup(77777).HasFocus"):
            xbmc.executebuiltin('Control.SetFocus(77777,0)')
            linkCount -= 1
            xbmc.sleep(50)
    
    def setWidget(self, containerID):
        self.win.clearProperty("activewidget")
        self.win.clearProperty("customwidgetcontent")
        skinStringContent = ""
        customWidget = False
        
        # workaround for numeric labels (get translated by xbmc)
        skinString = xbmc.getInfoLabel("Container(" + containerID + ").ListItem.Property(submenuVisibility)")
        skinString = skinString.replace("num-","")
        if xbmc.getCondVisibility("Skin.String(widget-" + skinString + ')'):
            skinStringContent = xbmc.getInfoLabel("Skin.String(widget-" + skinString + ')')
        
        # normal method by getting the defaultID
        if skinStringContent == "":
            skinString = xbmc.getInfoLabel("Container(" + containerID + ").ListItem.Property(defaultID)")
            if xbmc.getCondVisibility("Skin.String(widget-" + skinString + ')'):
                skinStringContent = xbmc.getInfoLabel("Skin.String(widget-" + skinString + ')')
           
        if skinStringContent and not "search" in skinStringContent:
            if ("$INFO" in skinStringContent or "Activate" in skinStringContent or ":" in skinStringContent):
                skinStringContent = self.getContentPath(skinStringContent)
                customWidget = True   
            if customWidget:
                 self.win.setProperty("customwidgetcontent", skinStringContent)
                 self.win.setProperty("activewidget","custom")
            else:
                self.win.clearProperty("customwidgetcontent")
                self.win.setProperty("activewidget",skinStringContent)

        else:
            self.win.clearProperty("activewidget")

    def setSpotlightWidget(self, containerID):
        self.win.clearProperty("spotlightwidgetcontent")
        skinStringContent = ""
        customWidget = False
        
        # workaround for numeric labels (get translated by xbmc)
        skinString = xbmc.getInfoLabel("Container(" + containerID + ").ListItem.Property(submenuVisibility)")
        skinString = skinString.replace("num-","")
        if xbmc.getCondVisibility("Skin.String(spotlightwidget-" + skinString + ')'):
            skinStringContent = xbmc.getInfoLabel("Skin.String(spotlightwidget-" + skinString + ')')
        
        # normal method by getting the defaultID
        if skinStringContent == "":
            skinString = xbmc.getInfoLabel("Container(" + containerID + ").ListItem.Property(defaultID)")
            if xbmc.getCondVisibility("Skin.String(spotlightwidget-" + skinString + ')'):
                skinStringContent = xbmc.getInfoLabel("Skin.String(spotlightwidget-" + skinString + ')')
           
        if skinStringContent and not "search" in skinStringContent:
            if ("$INFO" in skinStringContent or "Activate" in skinStringContent or ":" in skinStringContent):
                skinStringContent = self.getContentPath(skinStringContent)
                customWidget = True
            self.win.setProperty("spotlightwidgetcontent", skinStringContent)

        else:
            self.win.clearProperty("spotlightwidgetcontent")        
                              

xbmc.log('titan helper version %s started' % __addonversion__)
Main()
xbmc.log('titan helper version %s stopped' % __addonversion__)
