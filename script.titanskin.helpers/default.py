import xbmcaddon
import xbmcplugin
import os

__settings__ = xbmcaddon.Addon(id='script.titanskin.helpers')
__cwd__ = __settings__.getAddonInfo('path')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

import MainModule

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
    MainModule.sendClick(argument1)
elif action =="ADDSHORTCUT":
    MainModule.addShortcutWorkAround()
elif action == "SHOWSUBMENU":
    MainModule.showSubmenu(argument1,argument2)
elif action == "SHOWINFO":
    MainModule.showInfoPanel()
elif action == "SETWIDGET":
    MainModule.setWidget(argument1)
elif action == "UPDATEPLEXLINKS":   
    MainModule.updatePlexlinks()
elif action == "SHOWWIDGET":   
    MainModule.showWidget()
elif action == "SETCUSTOM":
    MainModule.setCustomContent(argument1)
elif action == "DEFAULTSETTINGS":
    MainModule.defaultSettings()
elif action == "MUSICSEARCH":
    MainModule.musicSearch()
elif action == "SETVIEW":
    MainModule.setView()
elif action == "SETFORCEDVIEW":
    MainModule.setForcedView(argument1)    
elif action == "ENABLEVIEWS":
    MainModule.enableViews()
elif action == "VIDEOSEARCH":
    from SearchDialog import SearchDialog
    searchDialog = SearchDialog("CustomSearch.xml", __cwd__, "default", "1080i")
    searchDialog.doModal()
    del searchDialog
elif action == "COLORPICKER":
    from ColorPicker import ColorPicker
    colorPicker = ColorPicker("ColorPicker.xml", __cwd__, "default", "1080i")
    colorPicker.skinString = argument1
    colorPicker.doModal()
    del colorPicker
elif action == "COLORTHEMES":
    from ColorThemes import ColorThemes
    colorThemes = ColorThemes("ColorThemes.xml", __cwd__, "default", "1080i")
    colorThemes.doModal()
    del colorPicker
elif action == "COLORTHEMETEXTURE":    
    MainModule.selectOverlayTexture()   
elif action == "BACKUP":
    import BackupRestore
    BackupRestore.backup()
elif action == "RESTORE":
    import BackupRestore
    BackupRestore.restore()
elif action == "RESET":
    import BackupRestore
    BackupRestore.reset()
elif action == "BACKGROUNDS":
    MainModule.UpdateBackgrounds()
elif action == "CHECKNOTIFICATIONS":
    MainModule.checkNotifications(argument1)
elif action == "SETSKINVERSION":
    MainModule.setSkinVersion()
elif argument1 == "?FAVOURITES":
    MainModule.getFavourites()
elif "?LAUNCHAPP" in argument1:
    try:
        app = argument1.split("&&&")[-1]
        xbmc.executebuiltin(app)
    except: pass


    
    