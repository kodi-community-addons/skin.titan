import xbmcplugin
import xbmcgui
import xbmc
import json

def logMsg(msg, level = 1):
    doDebugLog = False
    if doDebugLog == True or level == 0:
        xbmc.log("Titanskin DEBUG --> " + msg)

def getContentPath(libPath):
    if "$INFO" in libPath:
        win = xbmcgui.Window( 10000 )
        libPath = libPath.replace("$INFO[Window(Home).Property(", "")
        libPath = libPath.replace(")]", "")
        libPath = win.getProperty(libPath)    

    if "Activate" in libPath:
        libPath = libPath.split(",",1)[1]
        libPath = libPath.replace(",return","")
        libPath = libPath.replace(", return","")
        libPath = libPath.replace(")","")
        libPath = libPath.replace("\"","")
    
    return libPath

def getJSON(method,params):
    json_response = xbmc.executeJSONRPC('{ "jsonrpc" : "2.0" , "method" : "' + method + '" , "params" : ' + params + ' , "id":1 }')

    jsonobject = json.loads(json_response.decode('utf-8','replace'))
   
    if(jsonobject.has_key('result')):
        return jsonobject['result']
    else:
        logMsg("no result " + str(jsonobject))
        return None

        
def createListItem(item):
       
    liz = xbmcgui.ListItem(item['title'])
    liz.setInfo( type="Video", infoLabels={ "Title": item['title'] })
    liz.setProperty('IsPlayable', 'true')
    season = None
    episode = None
    
    if "runtime" in item:
        liz.setInfo( type="Video", infoLabels={ "duration": str(item['runtime']/60) })
    
    if "episode" in item:
        episode = "%.2d" % float(item['episode'])
        liz.setInfo( type="Video", infoLabels={ "Episode": item['episode'] })
    
    if "season" in item:
        season = "%.2d" % float(item['season'])
        liz.setInfo( type="Video", infoLabels={ "Season": item['season'] })
        
    if season and episode:
        episodeno = "s%se%s" %(season,episode)
        liz.setProperty("episodeno", episodeno)
    
    if "episodeid" in item:
        liz.setProperty("dbid", str(item['episodeid']))
        
    if "movieid" in item:
        liz.setProperty("dbid", str(item['movieid']))
    
    if "firstaired" in item:
        liz.setInfo( type="Video", infoLabels={ "Premiered": item['firstaired'] })
    
    plot = item['plot']
    liz.setInfo( type="Video", infoLabels={ "Plot": plot })
    
    if "showtitle" in item:
        liz.setInfo( type="Video", infoLabels={ "TVshowTitle": item['showtitle'] })
    
    if "rating" in item:
        liz.setInfo( type="Video", infoLabels={ "Rating": str(round(float(item['rating']),1)) })
    liz.setInfo( type="Video", infoLabels={ "Playcount": item['playcount'] })
    if "director" in item:
        liz.setInfo( type="Video", infoLabels={ "Director": " / ".join(item['director']) })
    if "writer" in item:
        liz.setInfo( type="Video", infoLabels={ "Writer": " / ".join(item['writer']) })
        
    if "cast" in item:
        listCast = []
        listCastAndRole = []
        for castmember in item["cast"]:
            listCast.append( castmember["name"] )
            listCastAndRole.append( (castmember["name"], castmember["role"]) ) 
        cast = [listCast, listCastAndRole]
        liz.setInfo( type="Video", infoLabels={ "Cast": cast[0] })
        liz.setInfo( type="Video", infoLabels={ "CastAndRole": cast[1] })
    
    liz.setProperty("resumetime", str(item['resume']['position']))
    liz.setProperty("totaltime", str(item['resume']['total']))
    liz.setArt(item['art'])
    liz.setThumbnailImage(item['art'].get('thumb',''))
    liz.setIconImage('DefaultTVShows.png')
    
    #liz.setProperty("fanart_image", item['art'].get('tvshow.fanart',''))
    for key, value in item['streamdetails'].iteritems():
        for stream in value:
            liz.addStreamInfo( key, stream )
    
    return liz