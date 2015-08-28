import xbmcaddon,xbmc,xbmcvfs,xbmcgui
import os
from xml.dom.minidom import parse
import math

__settings__ = xbmcaddon.Addon(id='script.titanskin.helpers')
__cwd__ = __settings__.getAddonInfo('path')
KODI_VERSION  = int(xbmc.getInfoLabel( "System.BuildVersion" ).split(".")[0])


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
if action =="migrate":
    
    #migrate function
    # to migrate all current user settings to the new skinhelper and skinshortcuts
    # applied only once
    
    # migrate skin shortcuts 
   
    propertiesList = []
    xbmc.log("TITAN SKIN --> Migrating Widget and background settings.....")
    
    #read existing properties
    propertiesfile = xbmc.translatePath("special://home/userdata/addon_data/script.skinshortcuts/%s.properties" %xbmc.getSkinDir()).decode("utf-8")
    if xbmcvfs.exists( propertiesfile ):
        f = open(propertiesfile, "r")
        for line in f:
            line = line.replace("[[","[").replace("]]","]").replace(",\n","").replace("\n","")
            if line.startswith("['") or line.startswith(" ['"):
                propertiesList.append(line)
        f.close()
        
    #Migrate skin shortcuts - convert widget settings
    skinshortcutspath = xbmc.translatePath("special://home/userdata/addon_data/script.skinshortcuts/mainmenu.DATA.xml").decode("utf-8")
    if xbmcvfs.exists( skinshortcutspath ):
        doc = parse( skinshortcutspath )
        listing = doc.documentElement.getElementsByTagName( 'shortcut' )
        for shortcut in listing:
            defaultID = shortcut.getElementsByTagName( 'defaultID' )
            if defaultID:
                defaultID = defaultID[0].firstChild
                if defaultID:
                    defaultID = defaultID.data
                    label = shortcut.getElementsByTagName( 'label' )[0].firstChild.data
                    widget = xbmc.getInfoLabel("$INFO[Skin.String(widget-%s)]" %defaultID)
                    xbmc.executebuiltin("Skin.Reset(widget-%s)" %defaultID)
                    widgetPropExists = False
                    backgroundPropExists = False
                    for line in propertiesList:
                        if "widget" in line and "'" + defaultID + "'" in line:
                            widgetPropExists = True
                        if "background" in line and "'" + defaultID + "'" in line:
                            backgroundPropExists = True
                    
                    if widget and not widgetPropExists:
                        if widget == "weather":
                            propertiesList.append("['mainmenu', '%s', 'widget', u'weather']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$LOCALIZE[12600]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'static']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'static']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'$INCLUDE[StaticWidgetContent]']"%defaultID)
                        elif widget == "movies":
                            propertiesList.append("['mainmenu', '%s', 'widget', u'recommendedmovies']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$ADDON[script.skin.helper.service 32003]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'movies']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'plugin://script.skin.helper.service/?action=RECOMMENDEDMOVIES&reload=$INFO[Window(Home).Property(widgetreload)]']"%defaultID)
                        elif widget == "tvshows":
                            propertiesList.append("['mainmenu', '%s', 'widget', u'nextepisodes']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$ADDON[script.skin.helper.service 32002]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'episodes']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'plugin://script.skin.helper.service/?action=nextepisodes&reload=$INFO[Window(Home).Property(widgetreload)]']"%defaultID)
                        elif widget == "youtube":
                            propertiesList.append("['mainmenu', '%s', 'widget', u'popularyoutube']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$LOCALIZE[31563]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'plugin://plugin.video.youtube/special/popular_right_now/']"%defaultID)
                        elif widget == "systeminfo":
                            propertiesList.append("['mainmenu', '%s', 'widget', u'systeminfo']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$LOCALIZE[130]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'static']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'static']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'$INCLUDE[StaticWidgetContent]']"%defaultID)
                        elif widget == "music":
                            propertiesList.append("['mainmenu', '%s', 'widget', u'recentalbums']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$LOCALIZE[359]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'songs']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'music']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'special://skin/extras/widgetplaylists/recentalbums.xsp']"%defaultID)
                        elif widget == "custom" and "window-home-property" in defaultID:
                            propertiesList.append("['mainmenu', '%s', 'widget', u'custom']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'%s']"%(defaultID,label.replace(".title",".recent.title")))
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'%s']"%(defaultID,label.replace(".title",".recent.content")))
                        elif widget == "custom" and "musicvideo" in defaultID:
                            propertiesList.append("['mainmenu', '%s', 'widget', u'musicvideos']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$LOCALIZE[20390]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'musicvideos']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'videodb://recentlyaddedmusicvideos/']"%defaultID)
                        else:
                            propertiesList.append("['mainmenu', '%s', 'widget', u'custom']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetName', u'$LOCALIZE[636]']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetType', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetTarget', u'video']"%defaultID)
                            propertiesList.append("['mainmenu', '%s', 'widgetPath', u'%s']"%(defaultID,widget))

                    if not backgroundPropExists:
                        if defaultID == "movies":
                            propertiesList.append("['mainmenu', 'movies', 'background', u'$INFO[Window(Home).Property(SkinHelper.AllMoviesBackground)]']")
                            propertiesList.append("['mainmenu', 'movies', 'backgroundName', u'$ADDON[script.skin.helper.service 32039]']")
                        elif defaultID == "tvshows":
                            propertiesList.append("['mainmenu', 'tvshows', 'background', u'$INFO[Window(Home).Property(SkinHelper.AllTvShowsBackground)]']")
                            propertiesList.append("['mainmenu', 'tvshows', 'backgroundName', u'$ADDON[script.skin.helper.service 32043]']")    
                        elif defaultID == "livetv":
                            propertiesList.append("['mainmenu', 'livetv', 'background', u'special://skin/extras/backgrounds/hover_my tv.jpg']")
                            propertiesList.append("['mainmenu', 'livetv', 'backgroundName', u'$LOCALIZE[10040]']")
                        if defaultID == "music":
                            propertiesList.append("['mainmenu', 'music', 'background', u'$INFO[Window(Home).Property(SkinHelper.AllMusicBackground)]']")
                            propertiesList.append("['mainmenu', 'music', 'backgroundName', u'$ADDON[script.skin.helper.service 32048]']")
                        if defaultID == "musicvideos":
                            propertiesList.append("['mainmenu', 'musicvideos', 'background', u'$INFO[Window(Home).Property(SkinHelper.AllMusicVideosBackground)]']")
                            propertiesList.append("['mainmenu', 'musicvideos', 'backgroundName', u'$ADDON[script.skin.helper.service 32047]']")
                        if defaultID == "weather":
                            propertiesList.append("['mainmenu', 'weather', 'background', u'$VAR[WeatherFanArtPath]$INFO[Window(Weather).Property(Current.FanartCode)]']")
                            propertiesList.append("['mainmenu', 'weather', 'backgroundName', u'$LOCALIZE[8]']")
                        if defaultID == "plugin.video.youtube":
                            propertiesList.append("['mainmenu', 'plugin.video.youtube', 'background', u'special://skin/extras/backgrounds/hover_extensions.jpg']")
                            propertiesList.append("['mainmenu', 'plugin.video.youtube', 'backgroundName', u'$LOCALIZE[10040]']")
                        if defaultID == "pictures":
                            propertiesList.append("['mainmenu', 'pictures', 'background', u'$INFO[Window(Home).Property(SkinHelper.PicturesBackground)]']")
                            propertiesList.append("['mainmenu', 'pictures', 'backgroundName', u'$ADDON[script.skin.helper.service 32046]']")
                        if defaultID == "10040":
                            propertiesList.append("['mainmenu', '10040', 'background', u'special://skin/extras/backgrounds/programs.jpg']")
                            propertiesList.append("['mainmenu', '10040', 'backgroundName', u'$LOCALIZE[10040]']")
                        if defaultID == "videos" or defaultID=="10006" or defaultID=="Videos":
                            propertiesList.append("['mainmenu', 'videos', 'background', u'$INFO[Window(Home).Property(SkinHelper.GlobalFanartBackground)]']")
                            propertiesList.append("['mainmenu', 'videos', 'backgroundName', u'$ADDON[script.skin.helper.service 32038]']")
                        if defaultID == "settings":
                            propertiesList.append("['mainmenu', 'settings', 'background', u'special://skin/extras/backgrounds/systeminfo.jpg']")
                            propertiesList.append("['mainmenu', 'settings', 'backgroundName', u'$LOCALIZE[10040]']")


    #write the properties list
    if propertiesList:
        TotalCount = len(propertiesList)
        count = 1
        f = open(propertiesfile, "w")
        for line in propertiesList:
            if count == 1:
                f.write("[" + line + ",\n")
            elif count == TotalCount:
                f.write(line+"]")
            else:
                f.write(line + ",\n")
            count += 1
        f.close()
        
    
    # migrate skin shortcuts - replace VARs
    skinshortcutspath = xbmc.translatePath("special://home/userdata/addon_data/script.skinshortcuts/").decode("utf-8")
    if xbmcvfs.exists( skinshortcutspath ):
        dirs, files = xbmcvfs.listdir(skinshortcutspath)
        for file in files:
            f = open(skinshortcutspath+file, "r")
            contents = f.read() 
            f.close()
            contents = contents.replace("$VAR[MusicButtonThumb]","$INFO[Window(Home).Property(SkinHelper.AllMusicBackground)]")
            contents = contents.replace("$VAR[MoviesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.AllMoviesBackground)]")
            contents = contents.replace("$VAR[MoviesGenresButtonThumb]","$INFO[Window(Home).Property(SkinHelper.AllMoviesBackground)]")
            contents = contents.replace("$VAR[TvseriesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.AllTvShowsBackground)]")
            contents = contents.replace("$VAR[MusicVideosButtonThumb]","$INFO[Window(Home).Property(SkinHelper.AllMusicVideosBackground)]")
            contents = contents.replace("$VAR[WeatherButtonThumb]","special://skin/extras/weather/$INFO[Window(Weather).Property(Current.FanartCode)]/weather.jpg")
            contents = contents.replace("$VAR[PicturesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.PicturesBackground)]")
            contents = contents.replace("$VAR[InProgressMoviesButtonOnClick]","ActivateWindow(10025,special://skin/extras/widgetplaylists/inprogressmovies.xsp)")
            contents = contents.replace("$VAR[UnwatchedMoviesButtonOnClick]","ActivateWindow(10025,special://skin/extras/widgetplaylists/unwatchedmovies.xsp)")
            contents = contents.replace("$VAR[InProgressMoviesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.InProgressMoviesBackground)]")
            contents = contents.replace("$VAR[UnwatchedMoviesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.UnwatchedMoviesBackground)]")
            contents = contents.replace("$VAR[RecentTVseriesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.RecentEpisodesBackground)]")
            contents = contents.replace("$VAR[InprogressTVseriesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.InProgressShowsBackground)]")
            contents = contents.replace("$VAR[RecentMoviesButtonThumb]","$INFO[Window(Home).Property(SkinHelper.RecentMoviesBackground)]")
            contents = contents.replace("$VAR[CustomCollectionClick]","SetFocus(4444)")
            contents = contents.replace("plugin://script.titanskin.helpers/?","plugin://script.skin.helper.service/?action=")
            
            f = open(skinshortcutspath+file, "w")
            f.write(contents)
            f.close()
    
    xbmc.log("TITAN SKIN --> Migrating Color settings.....")
    
    #get all colors from the colors xml file and fill a list with tuples to sort later on
    allColors = []
    colors_file = xbmc.translatePath("special://home/addons/script.skin.helper.service/resources/colors/colors.xml").decode("utf-8")
    if xbmcvfs.exists( colors_file ):
        doc = parse( colors_file )
        listing = doc.documentElement.getElementsByTagName( 'color' )
        for count, color in enumerate(listing):
            name = color.attributes[ 'name' ].nodeValue.lower()
            colorstring = color.childNodes [ 0 ].nodeValue.lower()
            allColors.append((name,colorstring))
    
    #get skin colors too
    colors_file = xbmc.translatePath("special://skin/colors/defaults.xml").decode("utf-8")
    if xbmcvfs.exists( colors_file ):
        doc = parse( colors_file )
        listing = doc.documentElement.getElementsByTagName( 'color' )
        for count, color in enumerate(listing):
            name = color.attributes[ 'name' ].nodeValue.lower()
            colorstring = color.childNodes [ 0 ].nodeValue.lower()
            allColors.append((name,colorstring))
    
    #read the guisettings file to get all skin settings
    skinsettingsList = []
    if KODI_VERSION < 16:
        guisettings_path = 'special://profile/guisettings.xml'
    else:
        guisettings_path = 'special://profile/addon_data/%s/settings.xml' %xbmc.getSkinDir()
    if xbmcvfs.exists(guisettings_path):
        print guisettings_path
        guisettings_path = xbmc.translatePath(guisettings_path).decode("utf-8")
        doc = parse(guisettings_path)
        skinsettings = doc.documentElement.getElementsByTagName('setting')
        
        for count, skinsetting in enumerate(skinsettings):
            
            if KODI_VERSION < 16:
                settingname = skinsetting.attributes['name'].nodeValue
            else:
                settingname = skinsetting.attributes['id'].nodeValue
            
            #only get settings for the current skin                    
            if ( KODI_VERSION < 16 and settingname.startswith(xbmc.getSkinDir()+".")) or KODI_VERSION >= 16:
                
                if skinsetting.childNodes:
                    settingvalue = skinsetting.childNodes[0].nodeValue
                else:
                    settingvalue = ""
                
                settingname = settingname.replace(xbmc.getSkinDir()+".","")
                settingtype = skinsetting.attributes['type'].nodeValue

                if "color" in settingname.lower() and not settingname.lower().endswith(".name") and settingtype == "string":
                    match = None
                    for color in allColors:
                        if settingvalue == color[0] or settingvalue == color[1]:
                            match = color
                            break
                    if match:
                        xbmc.executebuiltin("Skin.SetString(" + settingname + '.name,'+ match[0] + ')')
                        xbmc.executebuiltin("Skin.SetString(" + settingname + ','+ match[1] + ')')
                    elif settingvalue.lower() == "none" or not settingvalue or settingvalue.upper()=="00FFFFFF":
                        xbmc.executebuiltin("Skin.SetString(%s.name,None)" %settingname)
                        xbmc.executebuiltin("Skin.SetString(%s,None)" %settingname)
                    else:
                        xbmc.executebuiltin("Skin.SetString(%s.name, Custom %s)" %(settingname,settingvalue))
                    
                    #check for old opacity setting...
                    opacity = xbmc.getInfoLabel("$INFO[Skin.String(%s)]" %settingname.replace("Color","Opacity"))
                    if opacity:
                        xbmc.sleep(250)
                        try:
                            color = xbmc.getInfoLabel("$INFO[Skin.String(%s)]" %settingname)
                            num = int(opacity) / 100.0 * 255
                            e = num - math.floor( num )
                            a = e < 0.5 and int( math.floor( num ) ) or int( math.ceil( num ) )
                            
                            colorstring = color.strip()
                            r, g, b = colorstring[2:4], colorstring[4:6], colorstring[6:]
                            r, g, b = [int(n, 16) for n in (r, g, b)]
                            color = (a, r, g, b)
                            colorstringvalue = '%02x%02x%02x%02x' % color
                            xbmc.executebuiltin("Skin.SetString(" + settingname + ','+ colorstringvalue + ')')
                            xbmc.executebuiltin("Skin.Reset(%s)" %settingname.replace("Color","Opacity"))
                        except:
                            xbmc.log("Error has occurred while correcting " + settingname)
                            xbmc.executebuiltin("Skin.Reset(%s)" %settingname.replace("Color","Opacity"))
                        
    #rebuild skinshortcuts
    xbmc.executebuiltin("RunScript(script.skinshortcuts,type=buildxml&amp;mainmenuID=300&amp;group=mainmenu|powermenu)")

    
    #wait for the skinshortcuts hashfile
    skinshortcutspath = xbmc.translatePath("special://home/userdata/addon_data/script.skinshortcuts/%s.hash" %xbmc.getSkinDir()).decode("utf-8")
    count = 0
    while count != 240 and not xbmcvfs.exists( skinshortcutspath ):
        xbmc.sleep(500)
        count += 1
    #delete the hashfile
    xbmcvfs.delete( skinshortcutspath )
    xbmc.sleep(500)
    xbmc.executebuiltin("RunScript(script.skinshortcuts,type=buildxml&amp;mainmenuID=300&amp;group=mainmenu|powermenu)")

            