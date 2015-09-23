from migration import *


# get arguments
action = ""
try:
    action = str(sys.argv[1])
except: 
    pass

if action =="migrate":
    fullMigration()
	
elif action =="migratecolors":
    migrateColorSettings()

elif action =="migratethemes":
    migrateColorThemes()

elif action:
    #TEMP: issue warning about the incompatible helper script
    xbmcgui.Dialog().ok("Titan skin - unsupported configuration", "Warning - You are using the stable version of the skin while having the beta repo installed, this is currently unsupported. Switch to the beta version of the skin or see the forums how to fix the stable version.")