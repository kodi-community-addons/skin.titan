import xbmcplugin
import xbmcgui
import shutil
import xbmcaddon
import os
import time
import urllib

def sendClick(controlId):
    win = xbmcgui.Window( 10000 )
    time.sleep(0.5)
    xbmc.executebuiltin('SendClick('+ controlId +')')

def setCustomContent(skinString):
    win = xbmcgui.Window( 10000 )
    print(skinString)
    skinStringContent = xbmc.getInfoLabel("Skin.String(" + skinString + ')')
    print(skinStringContent)
    
    if "$INFO" in skinStringContent:
        skinStringContent = skinStringContent.replace("$INFO[Window(Home).Property(", "")
        skinStringContent = skinStringContent.replace(")]", "")
        skinStringContent = win.getProperty(skinStringContent)    

    if "Activate" in skinStringContent:
        skinStringContent = skinStringContent.split(",",1)[1]
        skinStringContent = skinStringContent.replace(",return","")
        skinStringContent = skinStringContent.replace(")","")
        skinStringContent = skinStringContent.replace("\"","")
           
        #xbmc.executebuiltin("Skin.SetString(" + skinString + ','+ skinStringContent + ')')         
    
    print(skinStringContent)
    win.setProperty("customwidgetcontent", skinStringContent)


def showInfoPanel():
    win = xbmcgui.Window( 10000 )
    time.sleep(2)
    xbmc.executebuiltin('Action(info)')
    time.sleep(8)
    xbmc.executebuiltin('Action(info)')

def addShortcutWorkAround():
    win = xbmcgui.Window( 10000 )
    xbmc.executebuiltin('SendClick(301)')
    time.sleep(0.5)
    xbmc.executebuiltin('SendClick(401)')


def setView(containerType,viewId):

    if viewId=="00":
        win = xbmcgui.Window( 10000 )

        curView = xbmc.getInfoLabel("Container.Viewmode")

        if curView == "list":
            viewId="50"        
        elif curView == "Showcase":
            viewId="51"
        elif curView == "Horizontal Panel":
            viewId="52"        
        elif curView == "Panel details":
            viewId="53"       
        elif curView == "Panel Wall":
            viewId="54"
        elif curView == "Banner list":
            viewId="55"
        elif curView == "Banner Plex":
            viewId="56"            
        elif curView == "Big Panel":
            viewId="57" 
        elif curView == "Large Poster":
            viewId="58"
        elif curView == "Big Panel details":
            viewId="59"
        elif curView == "Landscape":
            viewId="501"
        elif curView == "Landscape Single Row":
            viewId="502"             
        elif curView == "Landscape details":
            viewId="505"            
        elif curView == "Extended":
            viewId="506"
        elif curView == "FanArt":
            viewId="507"
        elif curView == "Single Poster":
            viewId="508"
        elif curView == "Panel Square":
            viewId="509"
        elif curView == "Panel Square details":
            viewId="510"
        elif curView == "Thumbs":
            viewId="511"
        elif curView == "Thumbs details":
            viewId="512"
        elif curView == "Poster Row":
            viewId="513"
        elif curView == "Poster Shift":
            viewId="514"            

    else:
        viewId=viewId    

    if xbmc.getCondVisibility("System.HasAddon(plugin.video.xbmb3c)"):
        __settings__ = xbmcaddon.Addon(id='plugin.video.xbmb3c')
        __settings__.setSetting(xbmc.getSkinDir()+ '_VIEW_' + containerType, viewId)

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

        #xbmc.executebuiltin("Container.Refresh")


def showSubmenu(showOrHide,doFocus):

    win = xbmcgui.Window( 10000 )
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
else:
    xbmc.executebuiltin("Notification(Titan Mediabrowser,you can not run this script directly)") 