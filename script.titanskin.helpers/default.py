import xbmcplugin
import xbmcgui
import shutil
import xbmcaddon
import xbmcvfs
import os
import time
import urllib
import xml.etree.ElementTree as etree

doDebugLog = False

def logMsg(msg, level = 1):
    if self.doDebugLog == True:
        xbmc.log(msg)

def sendClick(controlId):
    win = xbmcgui.Window( 10000 )
    time.sleep(0.5)
    xbmc.executebuiltin('SendClick('+ controlId +')')

def setCustomContent(skinString):
    win = xbmcgui.Window( 10000 )
    skinStringContent = xbmc.getInfoLabel("Skin.String(" + skinString + ')')

    if "$INFO" in skinStringContent:
        skinStringContent = skinStringContent.replace("$INFO[Window(Home).Property(", "")
        skinStringContent = skinStringContent.replace(")]", "")
        skinStringContent = win.getProperty(skinStringContent)    

    if "Activate" in skinStringContent:
        skinStringContent = skinStringContent.split(",",1)[1]
        skinStringContent = skinStringContent.replace(",return","")
        skinStringContent = skinStringContent.replace(")","")
        skinStringContent = skinStringContent.replace("\"","")
           
        xbmc.executebuiltin("Skin.SetString(" + skinString + ','+ skinStringContent + ')')         

    win.setProperty("customwidgetcontent", skinStringContent)

def updatePlexlinks():
    win = xbmcgui.Window( 10000 )
    linkCount = 0
    while linkCount !=10:
        plexstring = "plexbmc." + str(linkCount)
        randomNr = random.randrange(1,10+1)
        link = win.getProperty(plexstring + ".title")
        logMsg(plexstring + ".title --> " + link)
        plexType = win.getProperty(plexstring + ".type")
        logMsg(plexstring + ".type --> " + plexType)            

        randomimage = ""
        if plexType == "movie":
            randomimage = xbmc.getInfoLabel("Container(100" + str(linkCount) + ").ListItem(" + str(randomNr) + ").Art(fanart)")
            win.setProperty("plexfanartbg", randomimage)
        elif plexType == "artist":
            randomimage = xbmc.getInfoLabel("Container(100" + str(linkCount) + ").ListItem(" + str(randomNr) + ").Art(fanart)")
            if randomimage == "":
                randomimage = xbmc.getInfoLabel("Container(100" + str(linkCount) + ").ListItem(1).Art(fanart)")
            if randomimage == "":
                randomimage = "special://skin/extras/backgrounds/hover_my music.png"                
        elif plexType == "show":
            randomimage = xbmc.getInfoLabel("Container(100" + str(linkCount) + ").ListItem(" + str(randomNr) + ").Property(Fanart_Image)")
        elif plexType == "photo":
            randomimage = xbmc.getInfoLabel("Container(100" + str(linkCount) + ").ListItem(" + str(randomNr) + ").PicturePath")                

        if randomimage != "":
            win.setProperty(plexstring + ".image", randomimage)
            logMsg(plexstring + ".image --> " + randomimage)            

        link = win.getProperty(plexstring + ".recent")
        logMsg(plexstring + ".recent --> " + link)
        link = link.replace("ActivateWindow(VideoLibrary, ", "")
        link = link.replace("ActivateWindow(VideoLibrary,", "")
        link = link.replace("ActivateWindow(MusicFiles,", "")
        link = link.replace("ActivateWindow(Pictures,", "")
        link = link.replace(",return)", "")
        win.setProperty(plexstring + ".recent.content", link)
        logMsg(plexstring + ".recent --> " + link)

        link = win.getProperty(plexstring + ".viewed")
        logMsg(plexstring + ".viewed --> " + link)
        link = link.replace("ActivateWindow(VideoLibrary, ", "")
        link = link.replace("ActivateWindow(VideoLibrary,", "")
        link = link.replace("ActivateWindow(MusicFiles,", "")
        link = link.replace("ActivateWindow(Pictures,", "")
        link = link.replace(",return)", "")
        win.setProperty(plexstring + ".viewed.content", link)
        logMsg(plexstring + ".viewed --> " + link)

        linkCount += 1    

        
def showInfoPanel():
    win = xbmcgui.Window( 10000 )
    time.sleep(2)
    xbmc.executebuiltin('Action(info)')
    time.sleep(8)
    xbmc.executebuiltin('Action(info)')

def addShortcutWorkAround():
    win = xbmcgui.Window( 10000 )
    xbmc.executebuiltin('SendClick(301)')
    time.sleep(0.8)
    xbmc.executebuiltin('SendClick(401)')


def setView(containerType,viewId):

    if viewId=="00":
        win = xbmcgui.Window( 10000 )

        curView = xbmc.getInfoLabel("Container.Viewmode")
        
        # get all views from views-file
        skin_view_file = os.path.join(xbmc.translatePath('special://skin'), "views.xml")
        skin_view_file_alt = os.path.join(xbmc.translatePath('special://skin/extras'), "views.xml")
        if xbmcvfs.exists(skin_view_file_alt):
            skin_view_file = skin_view_file_alt
        try:
            tree = etree.parse(skin_view_file)
        except:           
            sys.exit()
        
        root = tree.getroot()
        
        for view in root.findall('view'):
            if curView == view.attrib['id']:
                viewId=view.attrib['value']
    else:
        viewId=viewId    

    if xbmc.getCondVisibility("System.HasAddon(plugin.video.netflixbmc)"):
        __settings__ = xbmcaddon.Addon(id='plugin.video.netflixbmc')

        if containerType=="MOVIES":
            __settings__.setSetting('viewIdVideos', viewId)
        elif containerType=="SERIES":
            __settings__.setSetting('viewIdEpisodesNew', viewId)
        elif containerType=="SEASONS":
            __settings__.setSetting('viewIdEpisodesNew', viewId)
        elif containerType=="EPISODES":
            __settings__.setSetting('viewIdEpisodesNew', viewId)
        else:
            __settings__.setSetting('viewIdActivity', viewId) 


def showSubmenu(showOrHide,doFocus):

    win = xbmcgui.Window( 10000 )
    submenuTitle = xbmc.getInfoLabel("Container(300).ListItem.Label")
    submenu = win.getProperty("submenutype")
    submenuloading = ""
    if xbmc.getCondVisibility("Skin.HasSetting(AutoShowSubmenu)"):
        submenuloading = win.getProperty("submenuloading")

    # SHOW SUBMENU    
    if showOrHide == "SHOW":
        if submenuloading != "loading":
            if submenu != "":
                win.setProperty("submenu", "show")
                if doFocus != None:
                    win.setProperty("submenuTitle", submenuTitle)
                    xbmc.executebuiltin('Control.SetFocus('+ doFocus +',0)')
                    time.sleep(0.2)
                    xbmc.executebuiltin('Control.SetFocus('+ doFocus +',0)')
            else:
                win.setProperty("submenu", "hide")
        else:
            win.setProperty("submenuloading", "")

    #HIDE SUBMENU
    elif showOrHide == "HIDE":
        win.setProperty("submenuloading", "loading")
        win.setProperty("submenu", "hide")
        if doFocus != None:
            xbmc.executebuiltin('Control.SetFocus('+ doFocus +',0)')
            time.sleep(0.8)
            xbmc.executebuiltin('Control.SetFocus('+ doFocus +',0)')


#script init
action = ""
argument1 = ""
argument2 = ""
argument3 = ""

# get arguments
try:
    action = str(sys.argv[1])
except: 
    pass

try:
    argument1 = str(sys.argv[2])
except: 
    pass

try:
    argument2 = str(sys.argv[3])
except: 
    pass

try:
    argument3 = str(sys.argv[4])
except: 
    pass  

# select action
if action == "SENDCLICK":
    sendClick(argument1)
elif action =="ADDSHORTCUT":
    addShortcutWorkAround()
elif action == "SETVIEW":
    setView(argument1, argument2)
elif action == "SHOWSUBMENU":
    showSubmenu(argument1,argument2)
elif action == "SHOWINFO":
    showInfoPanel()
elif action == "SETCUSTOM":
    setCustomContent(argument1)
elif action == "UPDATEPLEXLINKS":   
    updatePlexlinks()   
else:
    xbmc.executebuiltin("Notification(Titan Mediabrowser,you can not run this script directly)") 