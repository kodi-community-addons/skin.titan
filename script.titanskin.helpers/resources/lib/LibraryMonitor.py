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
    moviesetCache = {}
    extraFanartcache = {}
    
    win = None
    addon = None
    addondir = None
    
    def __init__(self, *args):
        
        self.win = xbmcgui.Window( 10000 )
        self.addon = xbmcaddon.Addon(id='script.titanskin.helpers')
        self.addondir = xbmc.translatePath(self.addon.getAddonInfo('profile'))
        
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
            if (xbmc.getCondVisibility("[Window.IsActive(videolibrary) | Window.IsActive(movieinformation)] + !Window.IsActive(fullscreenvideo)")):
                
                self.liPath = xbmc.getInfoLabel("ListItem.Path")
                if ((self.liPath != self.liPathLast) and xbmc.getCondVisibility("!Container.Scrolling")):
                    
                    self.liPathLast = self.liPath
                    
                    # update the listitem stuff
                    try:
                        self.setDuration()
                        self.setStudioName()
                        self.focusEpisode()
                        self.checkExtraFanArt()
                        self.setMovieSetDetails()
                        self.setAddonName()
                    except Exception as e:
                        utils.logMsg("ERROR in LibraryMonitor ! --> " + str(e), 0)
  
                else:
                    xbmc.sleep(50)

            else:
                xbmc.sleep(1000)
                self.delayedTaskInterval += 1
    
    def setMovieSetDetails(self):
        #get movie set details -- thanks to phil65 - used this idea from his skin info script
        
        self.win.clearProperty('MovieSet.Title')
        self.win.clearProperty('MovieSet.Runtime')
        self.win.clearProperty('MovieSet.Duration')
        self.win.clearProperty('MovieSet.Writer')
        self.win.clearProperty('MovieSet.Director')
        self.win.clearProperty('MovieSet.Genre')
        self.win.clearProperty('MovieSet.Country')
        self.win.clearProperty('MovieSet.Studio')
        self.win.clearProperty('MovieSet.Years')
        self.win.clearProperty('MovieSet.Year')
        self.win.clearProperty('MovieSet.Count')
        self.win.clearProperty('MovieSet.Plot')
            
        if xbmc.getCondVisibility("SubString(ListItem.Path,videodb://movies/sets/,left)"):
            
            dbId = xbmc.getInfoLabel("ListItem.DBID")
                    
            if dbId:
                
                #try to get from cache first
                if self.moviesetCache.has_key(dbId):
                    json_response = self.moviesetCache[dbId]
                else:
                    json_response = utils.getJSON('VideoLibrary.GetMovieSetDetails', '{"setid": %s, "properties": [ "thumbnail" ], "movies": { "properties":  [ "rating", "art", "file", "year", "director", "writer", "playcount", "genre" , "thumbnail", "runtime", "studio", "plotoutline", "plot", "country", "streamdetails"], "sort": { "order": "ascending",  "method": "year" }} }' % dbId)
                
                #save to cache
                self.moviesetCache[dbId] = json_response
                
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
                    self.win.setProperty('MovieSet.Plot', plot)
                    if json_response['setdetails']['limits']['total'] > 1:
                        self.win.setProperty('MovieSet.ExtendedPlot', title_header + title_list + "[CR]" + plot)
                    else:
                        self.win.setProperty('MovieSet.ExtendedPlot', plot)
                    self.win.setProperty('MovieSet.Title', title_list)
                    self.win.setProperty('MovieSet.Runtime', str(runtime))
                    durationString = self.getDurationString(runtime / 60)
                    if durationString:
                        self.win.setProperty('MovieSet.Duration', durationString)
                    self.win.setProperty('MovieSet.Writer', " / ".join(writer))
                    self.win.setProperty('MovieSet.Director', " / ".join(director))
                    self.win.setProperty('MovieSet.Genre', " / ".join(genre))
                    self.win.setProperty('MovieSet.Country', " / ".join(country))
                    self.win.setProperty('MovieSet.Studio', " / ".join(studio))
                    for item in studio:
                        if item in self.allStudioLogos:
                            studio = item
                            break
                    self.win.setProperty("ListItemStudio", studio)
                    
                    self.win.setProperty('MovieSet.Years', " / ".join(years))
                    self.win.setProperty('MovieSet.Year', years[0] + " - " + years[-1])
                    self.win.setProperty('MovieSet.Count', str(json_response['setdetails']['limits']['total']))
                    self.win.setProperty('MovieSet.WatchedCount', str(watchedcount))
                    self.win.setProperty('MovieSet.UnWatchedCount', str(unwatchedcount))
                    
                    #rotate fanart from movies in set while listitem is in focus
                    if xbmc.getCondVisibility("Skin.HasSetting(EnableExtraFanart)"):
                        count = 5
                        delaycount = 5
                        backgroundDelayStr = xbmc.getInfoLabel("skin.string(extrafanartdelay)")
                        if backgroundDelayStr:
                            count = int(backgroundDelayStr)
                            delaycount = int(backgroundDelayStr)
                        while dbId == xbmc.getInfoLabel("ListItem.DBID") and set_fanart != []:
                            
                            if count == delaycount:
                                random.shuffle(set_fanart)
                                self.win.setProperty('ExtraFanArtPath', set_fanart[0])
                                count = 0
                            else:
                                xbmc.sleep(1000)
                                count += 1

    def setAddonName(self):
        # set addon name as property
        if not xbmc.Player().isPlayingAudio():
            if (xbmc.getCondVisibility("Container.Content(plugins) | !IsEmpty(Container.PluginName)")):
                AddonName = xbmc.getInfoLabel('Container.PluginName')
                AddonName = xbmcaddon.Addon(AddonName).getAddonInfo('name')
                self.win.setProperty("Player.AddonName", AddonName)
            else:
                self.win.clearProperty("Player.AddonName")
    
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
        self.win.setProperty("ListItemStudio", studio)
                
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
        if (xbmc.getCondVisibility("!IsEmpty(ListItem.Duration)")):
            currentDuration = xbmc.getInfoLabel("ListItem.Duration")
            durationString = self.getDurationString(currentDuration)
            if durationString:
                self.win.setProperty('Duration', durationString)
            else:
                self.win.clearProperty('Duration')
        else:
            self.win.clearProperty('Duration')
        
    def getDurationString(self, duration):
        if duration == None or duration == 0:
            return None
        try:
            full_minutes = int(duration)
            minutes = full_minutes % 60
            hours   = full_minutes // 60
            durationString = str(hours) + ':' + str(minutes).zfill(2)
        except:
            print "exception in getDurationString"
            return None
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
        
        if xbmc.getCondVisibility("Window.IsActive(movieinformation)"):
            return
        
        #get the item from cache first
        if self.extraFanartcache.has_key(self.liPath):
            if self.extraFanartcache[self.liPath] == "None":
                self.win.clearProperty("ExtraFanArtPath")
                return
            else:
                self.win.setProperty("ExtraFanArtPath",self.extraFanartcache[self.liPath])
                return
        
        if not xbmc.getCondVisibility("Skin.HasSetting(EnableExtraFanart) + [Window.IsActive(videolibrary) | Window.IsActive(movieinformation)] + !Container.Scrolling"):
            self.win.clearProperty("ExtraFanArtPath")
            return
        
        if (self.liPath != None and (xbmc.getCondVisibility("Container.Content(movies) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(tvshows)")) and not "videodb:" in self.liPath):
                           
            if xbmc.getCondVisibility("Container.Content(episodes)"):
                liArt = xbmc.getInfoLabel("ListItem.Art(tvshow.fanart)")
            
            # do not set extra fanart for virtuals
            if (("plugin://" in self.liPath) or ("addon://" in self.liPath) or ("sources" in self.liPath) or ("plugin://" in containerPath) or ("sources://" in containerPath) or ("plugin://" in containerPath)):
                self.win.clearProperty("ExtraFanArtPath")
                self.extraFanartcache[self.liPath] = "None"
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
                        self.win.setProperty("ExtraFanArtPath",efaPath)
                        self.extraFanartcache[self.liPath] = efaPath
                        lastPath = efaPath       
                else:
                    self.win.clearProperty("ExtraFanArtPath")
                    self.extraFanartcache[self.liPath] = "None"
                    lastPath = None
        else:
            self.win.clearProperty("ExtraFanArtPath")
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

                                           