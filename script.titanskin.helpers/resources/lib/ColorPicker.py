import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os, sys
import urllib
import threading
import InfoDialog
from PIL import Image
from xml.dom.minidom import parse

win = xbmcgui.Window( 10000 )
addon = xbmcaddon.Addon(id='script.titanskin.helpers')
addondir = xbmc.translatePath(addon.getAddonInfo('profile'))
colorsPath = os.path.join(addondir,"colors") + os.sep

class ColorPicker(xbmcgui.WindowXMLDialog):

    manualEdit = None
    colorsList = None
    skinString = None
    
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        
    def addColorToList(self, colorname, colorstring):
        
        colorImageFile = os.path.join(colorsPath,colorstring + ".png")
        
        if not xbmcvfs.exists(colorImageFile):
            colorstring = colorstring.strip()
            if colorstring[0] == '#': colorstring = colorstring[1:]
            if len(colorstring) != 8:
                raise ValueError, "input #%s is not in #AARRGGBB format" % colorstring
            a, r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:6], colorstring[6:]
            a, r, g, b = [int(n, 16) for n in (a, r, g, b)]
            color = (r, g, b, a)
            im = Image.new("RGBA", (64, 64), color)
            im.save(colorImageFile)
        
        listitem = xbmcgui.ListItem(label=colorname, iconImage=colorImageFile)
        listitem.setProperty("colorstring",colorstring)
        self.colorsList.addItem(listitem)
        
    
    
    def onInit(self):
        self.action_exitkeys_id = [10, 13]

        if not xbmcvfs.exists(colorsPath):
            xbmcvfs.mkdir(colorsPath)
        
        self.colorsList = self.getControl(3110)
        self.manualEdit = self.getControl(3010)
        
        colors_file = xbmc.translatePath( 'special://home/addons/script.titanskin.helpers/resources/colors/colors.xml' ).decode("utf-8")
        if xbmcvfs.exists( colors_file ):
            doc = parse( colors_file )
            listing = doc.documentElement.getElementsByTagName( 'color' )
            
            for count, color in enumerate(listing):
                name = color.attributes[ 'name' ].nodeValue
                colorstring = color.childNodes [ 0 ].nodeValue
                self.addColorToList(name, colorstring)

    def onFocus(self, controlId):
        pass
        
    def onAction(self, action):

        ACTION_CANCEL_DIALOG = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
        ACTION_SHOW_INFO = ( 11, )
        ACTION_SELECT_ITEM = 7
        ACTION_PARENT_DIR = 9
        
        if action.getId() in ACTION_CANCEL_DIALOG:
            self.close()
        else:
            item =  self.colorsList.getSelectedItem()
            colorstring = item.getProperty("colorstring")
            self.manualEdit.setLabel(colorstring)


    def closeDialog(self):
        self.close()
        
    def onClick(self, controlID):

        if(controlID == 3110):       
            item = self.colorsList.getSelectedItem()
            colorstring = item.getProperty("colorstring")
            xbmc.executebuiltin("Skin.SetString(" + self.skinString + ','+ colorstring + ')')
            self.closeDialog()
        else:
            self.closeDialog()
            pass
