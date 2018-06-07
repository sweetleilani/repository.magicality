import sys
import xbmcgui
import xbmcplugin
import xbmc
import urllib
import urlparse
import requests
from bs4 import BeautifulSoup

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'movies')

scrape_base = "http://hentaihaven.org/"
mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}

def usersearch():
    kb = xbmc.Keyboard('default', 'heading')
    kb.setDefault('')
    kb.setHeading('Search')
    kb.setHiddenInput(False)
    kb.doModal()
    if (kb.isConfirmed()):
        searched  = kb.getText()
        search_term = searched.replace(" ", "+")
        return(search_term)
    else:
        return

def bsseries(url):
    get = requests.get(url, headers = mozhdr)
    soupeddata = BeautifulSoup(get.content, "html.parser")
    links = soupeddata.find_all("a", class_ = "category_alphabet_title_link")
    desc = soupeddata.find_all("div", class_ = "archive-meta category-meta")
    for a in links:
        href = a.get("href")
        hentaititle = a.text	
        urlchoice = build_url({'mode': 'serieschoice', 'foldername': href})
        li = xbmcgui.ListItem(hentaititle, iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlchoice, listitem=li, isFolder=True)		
    xbmcplugin.endOfDirectory(addon_handle)

def bscategories(url):
        get = requests.get(url, headers = mozhdr)
        soupeddata = BeautifulSoup(get.content, "html.parser")
        links = soupeddata.find_all("div", class_ = "taglist tags-links")
        for div in links:
            categories = div.find_all("a")
            for link in categories:
                    href = link.get("href")
                    cname = link.text
                    urlchoice = build_url({'mode': 'categorychoice', 'foldername': href})
                    li = xbmcgui.ListItem(cname, iconImage='DefaultFolder.png')
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlchoice, listitem=li, isFolder=True)
        xbmcplugin.endOfDirectory(addon_handle)

def bslinks(url):
        get = requests.get(url, headers = mozhdr)
        soupeddata = BeautifulSoup(get.content, "html.parser")
        links = soupeddata.find_all("a", class_ = "thumbnail-image")
        for a in links:
            href = a.get("href")
            epname = href.replace("http://hentaihaven.org/", "")
            epname2 = epname.replace("-"," ")
            epname3 = epname2.replace("/","")
            epnamefinal = epname3.title()
            thumb = a.find_all("img")
            for b in thumb:
                thumbimg = b.get("data-src")            
            urlchoice = build_url({'mode': 'videochoice', 'playlink': href})
            li = xbmcgui.ListItem(epnamefinal, iconImage=thumbimg)
            li.setProperty('IsPlayable' , 'true')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlchoice, listitem=li)
        xbmcplugin.endOfDirectory(addon_handle)	

def playsource(path):
    get = requests.get(path, headers = mozhdr)
    soupeddata = BeautifulSoup(get.content, "html.parser")
    link = soupeddata.find("source")
    href = link.get("src")	
    return href

def play_video(path):	
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

	
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)


if mode is None:
    urlseries = build_url({'mode': 'series', 'foldername': 'pick-your-series/'})
    li = xbmcgui.ListItem('Series', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlseries, listitem=li, isFolder=True)
    urlcategories = build_url({'mode': 'categories', 'foldername': 'pick-your-poison/'})
    li = xbmcgui.ListItem('Categories', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlcategories, listitem=li, isFolder=True)
    urlsearch = build_url({'mode': 'search', 'foldername': 'search/'})
    li = xbmcgui.ListItem('Search', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlsearch, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

	
elif mode[0] == 'series':
    scrape_add = args['foldername'][0]
    scrape_link = scrape_base + scrape_add
    bsseries(scrape_link)

elif mode[0] == 'categories':
    scrape_add = args['foldername'][0]
    scrape_link = scrape_base + scrape_add
    bscategories(scrape_link)

elif mode[0] == 'search':
    scrape_search = usersearch()
    scrape_add = args['foldername'][0]
    scrape_link = scrape_base + scrape_add + scrape_search
    bslinks(scrape_link)
	
elif mode[0] == 'serieschoice':
    scrape_link = args['foldername'][0]
    bslinks(scrape_link)

elif mode[0] == 'categorychoice':
    scrape_link = args['foldername'][0]
    bslinks(scrape_link)

elif mode[0] == 'videochoice':
    scrape_link = args['playlink'][0]
    play_source = playsource(scrape_link)
    play_video(play_source)
  
