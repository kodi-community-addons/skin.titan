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
from xml.dom.minidom import parse
import base64
import json

import Utils as utils


class BackgroundsUpdater(threading.Thread):
    
    event = None
    exit = False
    allBackgrounds = {}
    tempBlacklist = set()
    defBlacklist = set()
    lastPicturesPath = None
    smartShortcuts = {}
    cachePath = None
    SmartShortcutsCachePath = None
    win = None
    
    def __init__(self, *args):
        
        self.win = xbmcgui.Window( 10000 )
        self.lastPicturesPath = xbmc.getInfoLabel("skin.string(CustomPicturesBackgroundPath)")
        
        addon = xbmcaddon.Addon(id='script.titanskin.helpers')
        addondir = xbmc.translatePath(addon.getAddonInfo('profile'))
        
        self.cachePath = os.path.join(addondir,"backgroundscache.json")
        self.SmartShortcutsCachePath = os.path.join(addondir,"smartshotcutscache.json")

        utils.logMsg("BackgroundsUpdater - started")
        self.event =  threading.Event()
        threading.Thread.__init__(self, *args)    
    
    def stop(self):
        utils.logMsg("BackgroundsUpdater - stop called")
        self.saveCacheToFile()
        self.exit = True
        self.event.set()

    def run(self):

        backgroundDelay = 30000
            
        #first run get backgrounds immediately from filebased cache and reset the cache in memory to populate all images from scratch
        self.getCacheFromFile()
        self.UpdateBackgrounds()
        self.allBackgrounds = {}
        self.smartShortcuts = {}
         
        while (self.exit != True):
            
            if not xbmc.Player().isPlayingVideo():
                
                # Update home backgrounds every interval (default 60 seconds)
                backgroundDelayStr = xbmc.getInfoLabel("skin.string(randomfanartdelay)")
                if backgroundDelayStr:
                    backgroundDelay = int(backgroundDelayStr) * 1000

                self.UpdateBackgrounds()
            
            xbmc.sleep(backgroundDelay)
                               
    def saveCacheToFile(self):
        #safety check: does the config directory exist?
        if not xbmcvfs.exists(addondir + os.sep):
            xbmcvfs.mkdir(addondir)
        
        self.allBackgrounds["blacklist"] = list(self.defBlacklist)
        json.dump(self.allBackgrounds, open(self.cachePath,'w'))
        
        json.dump(self.smartShortcuts, open(self.SmartShortcutsCachePath,'w'))
        

    def getCacheFromFile(self):
        if xbmcvfs.exists(self.cachePath):
            with open(self.cachePath) as data_file:    
                data = json.load(data_file)
                
                self.defBlacklist = data["blacklist"]
                self.allBackgrounds = data
        
        if xbmcvfs.exists(self.SmartShortcutsCachePath):
            with open(self.SmartShortcutsCachePath) as data_file:    
                self.smartShortcuts = json.load(data_file)    
                

    def getImageFromPath(self, libPath):
        
        if self.exit:
            return None
            
        libPath = utils.getContentPath(libPath)
        utils.logMsg("getting images for path " + libPath)

        #is path in the temporary blacklist ?
        if libPath in self.tempBlacklist:
            utils.logMsg("path blacklisted - skipping for path " + libPath)
            return None
        
        #is path in the definitive blacklist ?
        if libPath in self.defBlacklist:
            utils.logMsg("path blacklisted - skipping for path " + libPath)
            return None
        
        #no blacklist so read cache and/or path
        utils.logMsg("path is NOT blacklisted (or blacklist file error) - continuing for path " + libPath)
        images = []
               
        #cache entry exists and cache is not expired, load cache entry
        if self.allBackgrounds.has_key(libPath):
            utils.logMsg("load random image from the cache file... " + libPath)
            image = None
            image = random.choice(self.allBackgrounds[libPath])
            if image:
                utils.logMsg("loading done setting image from cache... " + image)
                return image
            else:
                utils.logMsg("cache entry empty ?...skipping...")
        else:
            #no cache file so try to load images from the path
            utils.logMsg("get images from the path or plugin... " + libPath)
            if libPath.startswith("plugin://"):
                media_type = "files"
            else:
                media_type = "video"
            media_array = None
            media_array = utils.getJSON('Files.GetDirectory','{ "properties": ["title","art"], "directory": "' + libPath + '", "media": "' + media_type + '", "limits": {"end":50}, "sort": { "order": "ascending", "method": "random", "ignorearticle": true } }')
            if(media_array != None and media_array.has_key('files')):
                for media in media_array['files']:
                    if media.has_key('art'):
                        if media['art'].has_key('fanart'):
                            images.append(media['art']['fanart'])
                        if media['art'].has_key('tvshow.fanart'):
                            images.append(media['art']['tvshow.fanart'])
            else:
                utils.logMsg("media array empty or error so add this path to temporary blacklist..." + libPath)
                if libPath.startswith("musicdb://") or libPath.startswith("videodb://") or libPath.startswith("library://") or libPath.endswith(".xsp") or libPath.startswith("plugin://plugin.video.emby"):
                    #addpath to temporary blacklist
                    self.tempBlacklist.add(libPath)
                    return None
                else:
                    #blacklist this path
                    self.defBlacklist.add(libPath)
                    return None
        
        #all is fine, we have some images to randomize and return one
        image = None
        if images != []:
            self.allBackgrounds[libPath] = images
            random.shuffle(images)
            image = images[0]
            utils.logMsg("setting random image.... " + image)
        else:
            utils.logMsg("image array or cache empty so skipping this path until next restart - " + libPath)
            self.tempBlacklist.add(libPath)
        
        return image

    def getPicturesBackground(self):
        utils.logMsg("setting pictures background...")
        customPath = xbmc.getInfoLabel("skin.string(CustomPicturesBackgroundPath)")
        if (self.lastPicturesPath != customPath):
            if (self.allBackgrounds.has_key("pictures")):
                utils.logMsg("path has changed for pictures - clearing cache...")
                del self.allBackgrounds["pictures"]
            
        self.lastPicturesPath = customPath

        try:
            if (self.allBackgrounds.has_key("pictures")):
                #get random image from our global cache file
                image = None
                image = random.choice(self.allBackgrounds["pictures"])
                if image:
                    utils.logMsg("setting random image from cache.... " + image)
                return image 
            else:
                #load the pictures from the custom path or from all picture sources
                images = []
                
                if customPath:
                    #load images from custom path
                    dirs, files = xbmcvfs.listdir(customPath)
                    #pick all images from path
                    for file in files:
                        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".PNG"):
                            image = os.path.join(customPath,file)
                            images.append(image)
                else:
                    #load picture sources
                    media_array = utils.getJSON('Files.GetSources','{"media": "pictures"}')
                    if(media_array != None and media_array.has_key('sources')):
                        for source in media_array['sources']:
                            if source.has_key('file'):
                                if not "plugin://" in source["file"]:
                                    dirs, files = xbmcvfs.listdir(source["file"])
                                    if dirs:
                                        #pick 10 random dirs
                                        randomdirs = []
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        randomdirs.append(os.path.join(source["file"],random.choice(dirs)))
                                        
                                        #pick 5 images from each dir
                                        for dir in randomdirs:
                                            subdirs, files = xbmcvfs.listdir(dir)
                                            count = 0
                                            for file in files:
                                                if ((file.endswith(".jpg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".PNG")) and count < 5):
                                                    image = os.path.join(dir,file)
                                                    images.append(image)
                                                    count += 1
                                    if files:
                                        #pick 10 images from root
                                        count = 0
                                        for file in files:
                                            if ((file.endswith(".jpg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".PNG")) and count < 10):
                                                image = os.path.join(source["file"],file)
                                                images.append(image)
                                                count += 1
                
                #store images in the cache
                self.allBackgrounds["pictures"] = images
                
                # return a random image
                if images != []:
                    random.shuffle(images)
                    image = images[0]
                    utils.logMsg("setting random image.... " + image)
                    return image
                else:
                    utils.logMsg("image sources array or cache empty so skipping this path until next restart - " + libPath)
                    return None
        #if something fails, return None
        except:
            utils.logMsg("exception occured in getPicturesBackground.... ")
            return None            
            
    def getGlobalBackground(self):
        #just get a random image from all the images in the cache
        if self.allBackgrounds != {}:
            #get random image from our global cache
            image = None
            randomimages = random.choice(self.allBackgrounds.keys())
            image = random.choice(randomimages)
            return image 
            
       
    def UpdateBackgrounds(self):
        
        #get all movies  
        self.win.setProperty("AllMoviesBackground",self.getImageFromPath("videodb://movies/titles/"))
        
        
        #get all tvshows  
        self.win.setProperty("AllTvShowsBackground",self.getImageFromPath("videodb://tvshows/titles/"))
        
        #get all musicvideos  
        self.win.setProperty("AllMusicVideosBackground",self.getImageFromPath("videodb://musicvideos/titles/"))
        
            
        #get all music  
        self.win.setProperty("AllMusicBackground",self.getImageFromPath("musicdb://artists/"))
        
        #get global fanart background 
        self.win.setProperty("GlobalFanartBackground",self.getGlobalBackground())
        
            
        #get in progress movies  
        self.win.setProperty("InProgressMovieBackground",self.getImageFromPath("special://skin/extras/widgetplaylists/inprogressmovies.xsp"))

        #get recent and unwatched movies
        self.win.setProperty("RecentMovieBackground",self.getImageFromPath("videodb://recentlyaddedmovies/"))
        
            
        #unwatched movies
        self.win.setProperty("UnwatchedMovieBackground",self.getImageFromPath("special://skin/extras/widgetplaylists/unwatchedmovies.xsp"))
      
        #get in progress tvshows
        self.win.setProperty("InProgressShowsBackground",self.getImageFromPath("library://video/inprogressshows.xml"))
        
        #get recent episodes
        self.win.setProperty("RecentEpisodesBackground",self.getImageFromPath("videodb://recentlyaddedepisodes/"))
        
        #get pictures background
        self.win.setProperty("PicturesBackground", self.getPicturesBackground())
        
        #smart shortcuts --> emby nodes
        if xbmc.getCondVisibility("Skin.HasSetting(SmartShortcuts.emby)"):
            utils.logMsg("Processing smart shortcuts for emby nodes.... ")
            
            if self.smartShortcuts.has_key("emby"):
                utils.logMsg("get emby entries from cache.... ")
                nodes = self.smartShortcuts["emby"]
                for node in nodes:
                    key = node[0]
                    label = node[1]
                    path = node[2]
                    image = self.getImageFromPath(node[2])
                    self.win.setProperty(key + ".image", image)
                    self.win.setProperty(key + ".title", label)
                    self.win.setProperty(key + ".path", path)
            else:
                utils.logMsg("no cache - Get emby entries from file.... ")            
                #wait for max 5 seconds untill the emby nodes are available
                count = 0
                while (count < 20 and self.win.getProperty("Emby.nodes.total") == ""):
                    xbmc.sleep(250)
                    count += 1
                
                embyProperty = self.win.getProperty("Emby.nodes.total")
                contentStrings = ["", ".recent", ".inprogress", ".unwatched", ".recentepisodes", ".inprogressepisodes", ".nextepisodes"]
                if embyProperty:
                    nodes = []
                    totalNodes = int(embyProperty)
                    for i in range(totalNodes):
                        for contentString in contentStrings:
                            key = "Emby.nodes.%s%s"%(str(i),contentString)
                            path = self.win.getProperty("Emby.nodes.%s%s.path"%(str(i),contentString))
                            label = self.win.getProperty("Emby.nodes.%s%s.title"%(str(i),contentString))
                            if path:
                                nodes.append( (key, label, path ) )
                                image = self.getImageFromPath(path)
                                if image:
                                    self.win.setProperty("Emby.nodes.%s%s.image"%(str(i),contentString),image)
                                
                    self.smartShortcuts["emby"] = nodes
                    
                    
        #smart shortcuts --> playlists
        if xbmc.getCondVisibility("Skin.HasSetting(SmartShortcuts.playlists)"):
            utils.logMsg("Processing smart shortcuts for playlists.... ")
            try:
                if self.smartShortcuts.has_key("playlists"):
                    utils.logMsg("get playlist entries from cache.... ")
                    playlists = self.smartShortcuts["playlists"]
                    for playlist in playlists:
                        playlistCount = playlist[0]
                        label = playlist[1]
                        path = playlist[2]
                        image = self.getImageFromPath(playlist[2])
                        self.win.setProperty("playlist." + str(playlistCount) + ".image", image)
                        self.win.setProperty("playlist." + str(playlistCount) + ".label", label)
                        self.win.setProperty("playlist." + str(playlistCount) + ".action", path)
                else:
                    utils.logMsg("no cache - Get playlist entries from file.... ")
                    playlistCount = 0
                    playlists = []
                    path = "special://profile/playlists/video/"
                    if xbmcvfs.exists( path ):
                        dirs, files = xbmcvfs.listdir(path)
                        for file in files:
                            if file.endswith(".xsp"):
                                playlist = path + file
                                label = file.replace(".xsp","")
                                image = self.getImageFromPath(playlist)
                                if image != None:
                                    playlist = "ActivateWindow(Videos," + playlist + ",return)"
                                    self.win.setProperty("playlist." + str(playlistCount) + ".image", image)
                                    self.win.setProperty("playlist." + str(playlistCount) + ".label", label)
                                    self.win.setProperty("playlist." + str(playlistCount) + ".action", playlist)
                                    playlists.append( (playlistCount, label, playlist ))
                                    playlistCount += 1
                    
                    self.smartShortcuts["playlists"] = playlists
            except:
                #something wrong so disable the smartshortcuts for this section for now
                xbmc.executebuiltin("Skin.Reset(SmartShortcuts.playlists)")
                utils.logMsg("Error while processing smart shortcuts for playlists - set disabled.... ")
        
            
        #smart shortcuts --> favorites
        if xbmc.getCondVisibility("Skin.HasSetting(SmartShortcuts.favorites)"):
            utils.logMsg("Processing smart shortcuts for favourites.... ")
            try:
                if self.smartShortcuts.has_key("favourites"):
                    utils.logMsg("get favourites entries from cache.... ")
                    favourites = self.smartShortcuts["favourites"]
                    for favourite in favourites:
                        playlistCount = favourite[0]
                        label = favourite[1]
                        path = favourite[2]
                        image = self.getImageFromPath(favourite[2])
                        self.win.setProperty("favorite." + str(playlistCount) + ".image", image)
                        self.win.setProperty("favorite." + str(playlistCount) + ".label", label)
                        self.win.setProperty("favorite." + str(playlistCount) + ".action", path)
                else:
                    utils.logMsg("no cache - Get favourite entries from file.... ")
                    favoritesCount = 0
                    favourites = []
                    fav_file = xbmc.translatePath( 'special://profile/favourites.xml' ).decode("utf-8")
                    if xbmcvfs.exists( fav_file ):
                        doc = parse( fav_file )
                        listing = doc.documentElement.getElementsByTagName( 'favourite' )
                        
                        for count, favourite in enumerate(listing):
                            name = favourite.attributes[ 'name' ].nodeValue
                            path = favourite.childNodes [ 0 ].nodeValue
                            if (path.startswith("ActivateWindow(Videos") or path.startswith("ActivateWindow(10025") or path.startswith("ActivateWindow(videos") or path.startswith("ActivateWindow(Music") or path.startswith("ActivateWindow(10502")) and not "script://" in path:
                                image = self.getImageFromPath(path)
                                if image != None:
                                    self.win.setProperty("favorite." + str(favoritesCount) + ".image", image)
                                    self.win.setProperty("favorite." + str(favoritesCount) + ".label", name)
                                    self.win.setProperty("favorite." + str(favoritesCount) + ".action", path)
                                    favourites.append( (favoritesCount, label, path) )
                                    favoritesCount += 1
                                    
                    self.smartShortcuts["favourites"] = favourites
            except:
                #something wrong so disable the smartshortcuts for this section for now
                xbmc.executebuiltin("Skin.Reset(SmartShortcuts.favorites)")
                utils.logMsg("Error while processing smart shortcuts for favourites - set disabled.... ")                
        
        
        #get plex nodes
        if xbmc.getCondVisibility("System.HasAddon(plugin.video.plexbmc)"):
            
            utils.logMsg("Processing smart shortcuts for plex nodes.... ")
            
            if self.smartShortcuts.has_key("plex"):
                utils.logMsg("get plex entries from cache.... ")
                nodes = self.smartShortcuts["plex"]
                for node in nodes:
                    key = node[0]
                    label = node[1]
                    path = node[2]
                    image = self.getImageFromPath(node[2])
                    self.win.setProperty(key + ".background", image)
                    self.win.setProperty(key + ".title", label)
                    self.win.setProperty(key + ".path", path)
            else:
                utils.logMsg("no cache - Get plex entries from file.... ")    
            
                #wait for max 5 seconds untill the plex nodes are available
                count = 0
                while (count < 20 and not self.win.getProperty("plexbmc.0.title")):
                    xbmc.sleep(250)
                    count += 1
                    
                totalNodes = 14
                nodes = []
                for i in range(totalNodes):
                    plextitle = self.win.getProperty("plexbmc.%s.title"%str(i))
                    if plextitle:
                        plexcontent = self.win.getProperty("plexbmc.%s.all"%str(i))
                        if not plexcontent:
                            plexcontent = self.win.getProperty("plexbmc.%s.path"%str(i))
                        plextype = self.win.getProperty("plexbmc.%s.type" %str(i))
                        image = self.getImageFromPath(plexcontent)
                        key = "plexbmc.%s"%str(i)
                        nodes.append( (key, plextitle, plexcontent ) )
                        if image:
                            self.win.setProperty("plexbmc.%s.background"%str(i),image)
                            if plextype == "movie":
                                self.win.setProperty("plexfanartbg", image)
                    else:
                        break
                
                self.smartShortcuts["plex"] = nodes