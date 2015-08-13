import xbmcaddon
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
if action =="ADDSHORTCUT":
    MainModule.addShortcutWorkAround()

elif action == "DEFAULTSETTINGS":
    MainModule.defaultSettings()


    
    