#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcplugin
import xbmcaddon
import xbmcgui
import threading
import xbmcvfs
import random
import xml.etree.ElementTree as etree
import base64
import json
from datetime import datetime

import Utils as utils

doDebugLog = False

win = xbmcgui.Window( 10000 )
addon = xbmcaddon.Addon(id='script.titanskin.helpers')
addondir = xbmc.translatePath(addon.getAddonInfo('profile'))


class LibraryMonitor(threading.Thread):
    
    event = None
    exit = False
    liPath = None
    liPathLast = None
    unwatched = 1
    lastEpPath = ""
    allStudioLogos = list()
    LastStudioImagesPath = None
    delayedTaskInterval = 1800
    
    def __init__(self, *args):
        utils.logMsg("LibraryMonitor - started")
        self.event =  threading.Event()
        threading.Thread.__init__(self, *args)    
    
    def stop(self):
        utils.logMsg("LibraryMonitor - stop called")
        self.exit = True
        self.event.set()

    def run(self):

        lastListItemPath = None
        listItemPath = None

        while (xbmc.abortRequested == False and self.exit != True):
            
            #do some background stuff every 30 minutes
            if (xbmc.getCondVisibility("!Window.IsActive(videolibrary) + !Window.IsActive(fullscreenvideo)")):
                if (self.delayedTaskInterval >= 1800):
                    self.getStudioLogos()
                    self.delayedTaskInterval = 0                   
            
            # monitor listitem props when videolibrary is active
            if (xbmc.getCondVisibility("Window.IsActive(videolibrary) + !Window.IsActive(fullscreenvideo)")):
                
                self.liPath = xbmc.getInfoLabel("ListItem.Path")
                if ((self.liPath != self.liPathLast) and xbmc.getCondVisibility("!Container.Scrolling")):
                    
                    self.liPathLast = self.liPath
                    
                    # update the listitem stuff
                    self.setDuration()
                    self.setStudioName()
                    self.focusEpisode()
                    self.checkExtraFanArt()
                    self.setMovieSetDetails()
                    self.setAddonName()
  
                else:
                    xbmc.sleep(50)

            else:
                xbmc.sleep(1000)
                self.delayedTaskInterval += 1
    
    def setMovieSetDetails(self):
        #get movie set details -- thanks to phil65 - used this idea from his skin info script
            
        if xbmc.getCondVisibility("SubString(ListItem.Path,videodb://movies/sets/,left)"):
            
            dbId = xbmc.getInfoLabel("ListItem.DBID")
            
            win.clearProperty('MovieSet.Title')
            win.clearProperty('MovieSet.Runtime')
            win.clearProperty('MovieSet.Writer')
            win.clearProperty('MovieSet.Director')
            win.clearProperty('MovieSet.Genre')
            win.clearProperty('MovieSet.Country')
            win.clearProperty('MovieSet.Studio')
            win.clearProperty('MovieSet.Years')
            win.clearProperty('MovieSet.Year')
            win.clearProperty('MovieSet.Count')
            win.clearProperty('MovieSet.Plot')
                    
            if dbId != "":
                json_response = utils.getJSON('VideoLibrary.GetMovieSetDetails', '{"setid": %s, "properties": [ "thumbnail" ], "movies": { "properties":  [ "rating", "art", "file", "year", "director", "writer", "playcount", "genre" , "thumbnail", "runtime", "studio", "plotoutline", "plot", "country", "streamdetails"], "sort": { "order": "ascending",  "method": "year" }} }' % dbId)
                #clear_properties()
                if ("setdetails" in json_response):
                    
                    count = 1
                    unwatchedcount = 0
                    watchedcount = 0
                    runtime = 0
                    writer = []
                    director = []
                    genre = []
                    country = []
                    studio = []
                    years = []
                    plot = ""
                    title_list = ""
                    title_header = "[B]" + str(json_response['setdetails']['limits']['total']) + " " + xbmc.getLocalizedString(20342) + "[/B][CR]"
                    set_fanart = []
                    for item in json_response['setdetails']['movies']:
                        
                        if item["playcount"] == 0:
                            unwatchedcount += 1
                        else:
                            watchedcount += 1
                        
                        art = item['art']
                        set_fanart.append(art.get('fanart', ''))
                        title_list += "[I]" + item['label'] + " (" + str(item['year']) + ")[/I][CR]"
                        if item['plotoutline']:
                            plot += "[B]" + item['label'] + " (" + str(item['year']) + ")[/B][CR]" + item['plotoutline'] + "[CR][CR]"
                        else:
                            plot += "[B]" + item['label'] + " (" + str(item['year']) + ")[/B][CR]" + item['plot'] + "[CR][CR]"
                        runtime += item['runtime']
                        count += 1
                        if item.get("writer"):
                            writer += [w for w in item["writer"] if w and w not in writer]
                        if item.get("director"):
                            director += [d for d in item["director"] if d and d not in director]
                        if item.get("genre"):
                            genre += [g for g in item["genre"] if g and g not in genre]
                        if item.get("country"):
                            country += [c for c in item["country"] if c and c not in country]
                        if item.get("studio"):
                            studio += [s for s in item["studio"] if s and s not in studio]
                        years.append(str(item['year']))
                    win.setProperty('MovieSet.Plot', plot)
                    if json_response['setdetails']['limits']['total'] > 1:
                        win.setProperty('MovieSet.ExtendedPlot', title_header + title_list + "[CR]" + plot)
                    else:
                        win.setProperty('MovieSet.ExtendedPlot', plot)
                    win.setProperty('MovieSet.Title', title_list)
                    durationString = self.getDurationString(runtime / 60)
                    win.setProperty('MovieSet.Runtime', durationString)
                    win.setProperty('MovieSet.Writer', " / ".join(writer))
                    win.setProperty('MovieSet.Director', " / ".join(director))
                    win.setProperty('MovieSet.Genre', " / ".join(genre))
                    win.setProperty('MovieSet.Country', " / ".join(country))
                    win.setProperty('MovieSet.Studio', " / ".join(studio))
                    for item in studio:
                        if item in self.allStudioLogos:
                            studio = item
                            break
                    win.setProperty("ListItemStudio", studio)
                    
                    win.setProperty('MovieSet.Years', " / ".join(years))
                    win.setProperty('MovieSet.Year', years[0] + " - " + years[-1])
                    win.setProperty('MovieSet.Count', str(json_response['setdetails']['limits']['total']))
                    win.setProperty('MovieSet.WatchedCount', str(watchedcount))
                    win.setProperty('MovieSet.UnWatchedCount', str(unwatchedcount))
                    
                    count = 5
                    delaycount = 5
                    backgroundDelayStr = xbmc.getInfoLabel("skin.string(extrafanartdelay)")
                    if backgroundDelayStr:
                        count = int(backgroundDelayStr)
                        delaycount = int(backgroundDelayStr)
                    while dbId == xbmc.getInfoLabel("ListItem.DBID") and set_fanart != []:
                        #rotate fanart from movies in set while listitem is in focus
                        if count == delaycount:
                            random.shuffle(set_fanart)
                            win.setProperty('ExtraFanArtPath', set_fanart[0])
                            count = 0
                        else:
                            xbmc.sleep(1000)
                            count += 1
            else:
                win.clearProperty('MovieSet.Title')
                win.clearProperty('MovieSet.Runtime')
                win.clearProperty('MovieSet.Writer')
                win.clearProperty('MovieSet.Director')
                win.clearProperty('MovieSet.Genre')
                win.clearProperty('MovieSet.Country')
                win.clearProperty('MovieSet.Studio')
                win.clearProperty('MovieSet.Years')
                win.clearProperty('MovieSet.Year')
                win.clearProperty('MovieSet.Count')
                win.clearProperty('MovieSet.Plot')

    def setAddonName(self):
        # set addon name as property
        if not xbmc.Player().isPlayingAudio():
            if (xbmc.getCondVisibility("Container.Content(plugins) | !IsEmpty(Container.PluginName)")):
                AddonName = xbmc.getInfoLabel('Container.PluginName')
                AddonName = xbmcaddon.Addon(AddonName).getAddonInfo('name')
                win.setProperty("Player.AddonName", AddonName)
            else:
                win.clearProperty("Player.AddonName")
    
    def setStudioName(self):
        studio = xbmc.getInfoLabel('ListItem.Studio')
        if "/" in studio:
            studios = studio.split(" / ")
            count = 0
            for item in studios:
                if item in self.allStudioLogos:
                    studio = studios[count]
                    break
                count += 1
        win.setProperty("ListItemStudio", studio)
                
    def getStudioLogos(self):
        #fill list with all studio logos
        StudioImagesCustompath = xbmc.getInfoLabel("Skin.String(StudioImagesCustompath)")
        if StudioImagesCustompath:
            path = StudioImagesCustompath
        else:
            path = "special://skin/extras/flags/studios/"
        
        if path != self.LastStudioImagesPath:
            self.LastStudioImagesPath = path
            allLogos = list()
            dirs, files = xbmcvfs.listdir(path)
            for file in files:
                file = file.replace(".png","")
                file = file.replace(".PNG","")
                allLogos.append(file)

            self.allStudioLogos = set(allLogos)
    
    def focusEpisode(self):
        # monitor episodes for auto focus first unwatched
        if xbmc.getCondVisibility("Skin.HasSetting(AutoFocusUnwatchedEpisode)"):
            
            #store unwatched episodes
            if ((xbmc.getCondVisibility("Container.Content(seasons) | Container.Content(tvshows)")) and xbmc.getCondVisibility("!IsEmpty(ListItem.Property(UnWatchedEpisodes))")):
                try:
                    self.unwatched = int(xbmc.getInfoLabel("ListItem.Property(UnWatchedEpisodes)"))
                except: pass
            
            if (xbmc.getCondVisibility("Container.Content(episodes) | Container.Content(seasons)")):
                
                if (xbmc.getInfoLabel("Container.FolderPath") != self.lastEpPath and self.unwatched != 0):
                    totalItems = 0
                    curView = xbmc.getInfoLabel("Container.Viewmode") 
                    viewId = int(self.getViewId(curView))
                    
                    wid = xbmcgui.getCurrentWindowId()
                    window = xbmcgui.Window( wid )        
                    control = window.getControl(int(viewId))
                    totalItems = int(xbmc.getInfoLabel("Container.NumItems"))
                    
                    #only do a focus if we're on top of the list, else skip to prevent bouncing of the list
                    if not int(xbmc.getInfoLabel("Container.Position")) > 1:
                        if (xbmc.getCondVisibility("Container.SortDirection(ascending)")):
                            curItem = 0
                            control.selectItem(0)
                            xbmc.sleep(250)
                            while ((xbmc.getCondVisibility("Container.Content(episodes) | Container.Content(seasons)")) and totalItems >= curItem):
                                if (xbmc.getInfoLabel("Container.ListItem(" + str(curItem) + ").Overlay") != "OverlayWatched.png" and xbmc.getInfoLabel("Container.ListItem(" + str(curItem) + ").Label") != ".." and not xbmc.getInfoLabel("Container.ListItem(" + str(curItem) + ").Label").startswith("*")):
                                    if curItem != 0:
                                        control.selectItem(curItem)
                                    break
                                else:
                                    curItem += 1
                        
                        elif (xbmc.getCondVisibility("Container.SortDirection(descending)")):
                            curItem = totalItems
                            control.selectItem(totalItems)
                            xbmc.sleep(250)
                            while ((xbmc.getCondVisibility("Container.Content(episodes) | Container.Content(seasons)")) and curItem != 0):
                                
                                if (xbmc.getInfoLabel("Container.ListItem(" + str(curItem) + ").Overlay") != "OverlayWatched.png"):
                                    control.selectItem(curItem-1)
                                    break
                                else:    
                                    curItem -= 1
                                        
                            self.lastEpPath = xbmc.getInfoLabel("Container.FolderPath")
        
    def setDuration(self):
        # monitor listitem to set duration
        if (xbmc.getCondVisibility("!IsEmpty(ListItem.Duration)") ):
            currentDuration = xbmc.getInfoLabel("ListItem.Duration")
            durationString = self.getDurationString(currentDuration)
            win.setProperty('Duration', durationString)
        else:
            win.clearProperty('Duration')
        
    def getDurationString(self, duration):
        try:
            full_minutes = int(duration)
            if full_minutes <= 60:
                durationString = duration + " min."
            else:
                minutes = full_minutes % 60
                hours   = full_minutes // 60
                durationString = str(hours) + ':' + str(minutes).zfill(2)
        except:
            durationString = duration + " min."
        return durationString
            
    def getViewId(self, viewString):
        # get all views from views-file
        viewId = None
        skin_view_file = os.path.join(xbmc.translatePath('special://skin/extras'), "views.xml")
        tree = etree.parse(skin_view_file)
        root = tree.getroot()
        for view in root.findall('view'):
            if viewString == xbmc.getLocalizedString(int(view.attrib['languageid'])):
                viewId=view.attrib['value']
        
        return viewId    

    def checkExtraFanArt(self):
        
        lastPath = None
        efaPath = None
        efaFound = False
        liArt = None
        containerPath = xbmc.getInfoLabel("Container.FolderPath")
        
        if not xbmc.getCondVisibility("Skin.HasSetting(EnableExtraFanart) + Window.IsActive(myvideonav.xml) + !Container.Scrolling"):
            win.clearProperty("ExtraFanArtPath")
            return
        
        if (self.liPath != None and (xbmc.getCondVisibility("Container.Content(movies) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(tvshows)")) and not "videodb:" in self.liPath):
                           
            if xbmc.getCondVisibility("Container.Content(episodes)"):
                liArt = xbmc.getInfoLabel("ListItem.Art(tvshow.fanart)")
            
            # do not set extra fanart for virtuals
            if (("plugin://" in self.liPath) or ("addon://" in self.liPath) or ("sources" in self.liPath) or ("plugin://" in containerPath) or ("sources://" in containerPath) or ("plugin://" in containerPath)):
                win.clearProperty("ExtraFanArtPath")
                lastPath = None
            else:

                if xbmcvfs.exists(self.liPath + "extrafanart/"):
                    efaPath = self.liPath + "extrafanart/"
                else:
                    pPath = self.liPath.rpartition("/")[0]
                    pPath = pPath.rpartition("/")[0]
                    if xbmcvfs.exists(pPath + "/extrafanart/"):
                        efaPath = pPath + "/extrafanart/"
                        
                if xbmcvfs.exists(efaPath):
                    dirs, files = xbmcvfs.listdir(efaPath)
                    if files.count > 1:
                        efaFound = True
                        
                if (efaPath != None and efaFound == True):
                    if lastPath != efaPath:
                        win.setProperty("ExtraFanArtPath",efaPath)
                        lastPath = efaPath
                        
                else:
                    win.clearProperty("ExtraFanArtPath")
                    lastPath = None
        else:
            win.clearProperty("ExtraFanArtPath")
            lastPath = None

class Kodi_Monitor(xbmc.Monitor):
    
    WINDOW = xbmcgui.Window(10000)

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onDatabaseUpdated(self, database):
        pass

    def onNotification(self,sender,method,data):

        if method == "VideoLibrary.OnUpdate":
            jsondata = json.loads(data)
            if jsondata != None:
                #update nextup list when library has changed
                self.WINDOW.setProperty("widgetreload", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                                           