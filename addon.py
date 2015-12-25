# -*- coding: utf-8 -*-
# Module: default
# Author: Yangqian
# Created on: 25.12.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# Largely following the example at 
# https://github.com/romanvm/plugin.video.example/blob/master/main.py
import xbmc,xbmcgui,urllib2,re,xbmcplugin
from BeautifulSoup import BeautifulSoup
from urlparse import parse_qsl
import sys
import json


# Get the plugin url in plugin:// notation.
_url=sys.argv[0]
# Get the plugin handle as an integer number.
_handle=int(sys.argv[1])

def list_categories():
    f=urllib2.urlopen('http://www.panda.tv/cate')
    rr=BeautifulSoup(f.read())
    catel=rr.findAll('li',{'class':'category-list-item'})
    rrr=rrr=[(x.a['class'], x.a.text) for x in catel]
    listing=[]
    for classname,text in rrr:
        img=rr.find('img',{'alt':text})['src']
        list_item=xbmcgui.ListItem(label=text,thumbnailImage=img)
        list_item.setProperty('fanart_image',img)
        url='{0}?action=listing&category={1}'.format(_url,classname)
        is_folder=True
        listing.append((url,list_item,is_folder))
    xbmcplugin.addDirectoryItems(_handle,listing,len(listing))
    #xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle) 

def list_videos(category):
    f=urllib2.urlopen('http://www.panda.tv/cate/'+category)
    rr=BeautifulSoup(f.read())
    videol=rr.findAll('a',{'class':'video-list-item-inner'})
    rrr=rrr=[(x['href'][1:],x.img,x.findNext('div',{'class':'live-info'}).findAll('span')) for x in videol]
    listing=[]
    for roomid,image,liveinfo in rrr:
        img=image['src']
        roomname=image['alt']
        nickname=liveinfo[0].text
        peoplenumber=liveinfo[1].text

        combinedname=u'{0}:{1}:{2}'.format(nickname,roomname,peoplenumber)
        list_item=xbmcgui.ListItem(label=combinedname,thumbnailImage=img)
        list_item.setProperty('fanart_image',img)
        url='{0}?action=play&video={1}'.format(_url,roomid)
        is_folder=False
        listing.append((url,list_item,is_folder))
    xbmcplugin.addDirectoryItems(_handle,listing,len(listing))
    #xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle) 


def play_video(roomid):
    """
    Play a video by the provided path.
    :param path: str
    :return: None
    """
    f=urllib2.urlopen('http://www.panda.tv/api_room?roomid='+roomid)
    r=f.read()
    ss=json.loads(r)
    hostname=ss['data']['hostinfo']['name']
    roomname=ss['data']['roominfo']['name']
    #s=re.search('''"room_key":"(.*?)"''',r).group(1)
    s=ss['data']['videoinfo']['room_key']
    img=ss['data']['hostinfo']['avatar']
    combinedname=u'{0}:{1}'.format(hostname,roomname)
    # Create a playable item with a path to play.
    path='http://pl3.live.panda.tv/live_panda/{0}.flv'.format(s)
    play_item = xbmcgui.ListItem(path=path,thumbnailImage=img)
    play_item.setInfo(type="Video",infoLabels={"Title":combinedname})
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    # directly play the item.
    xbmc.Player().play(path, play_item)
 

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring:
    :return:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
