# -*- coding: latin-1 -*-
import re
import json
import sys
import time
import urllib
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import requests
import CommonFunctions as common


MODE_MOST_SEEN = "Mestsett"
MODE_LATEST_NEWS = "Senastenyheter"
MODE_LATEST_SPORT = "Senastesport"
MODE_LATEST_ENT = "Senastenoje"
MODE_A_TO_O = "a-o"
MODE_VIDEO = "video"
MODE_PROGRAM = "program"
MODE_PRG_LAST_EP = "latest-episodes"
MODE_PRG_LAST_CUT = "latest-videos"
MODE_PRG_POP_CUT = "popular-videos"

S_DEBUG = "debug"


addon = xbmcaddon.Addon("plugin.video.aftonbladet")
localize = addon.getLocalizedString

common.plugin = addon.getAddonInfo('name') + ' ' + addon.getAddonInfo('version')
common.dbg = True

addon_handle = int(sys.argv[1])

xbmcplugin.setContent(addon_handle, 'movies')


def viewStart():
  addDirectoryItem(localize(30012), { "mode": MODE_MOST_SEEN })
  addDirectoryItem(localize(30013), { "mode": MODE_LATEST_NEWS })
  addDirectoryItem(localize(30014), { "mode": MODE_LATEST_SPORT })
  addDirectoryItem(localize(30015), { "mode": MODE_LATEST_ENT })
  addDirectoryItem(localize(30000), { "mode": MODE_A_TO_O })

def viewAtoO():
  r = requests.get("http://tv.aftonbladet.se/abtv/programs");
  containers = common.parseDOM(r.text, "div", attrs = {"class":"site-index-link-wrapper"})
  programs = []
  for container in containers:
     program = {}
     links = common.parseDOM(container, "a", attrs = {"class":"site-index-link"}, ret="href")
     imgs = common.parseDOM(container, "img", ret = "srcset")
     titles = common.parseDOM(container, "div", attrs = {"class":"site-index-link-title"})
     descs = common.parseDOM(container, "div", attrs = {"class":"site-index-link-desc"})
     for i in range(len(links)):
        program={}
        program["title"]=titles[i]
        program["desc"]=descs[i]
        listimg = imgs[i].split(",")
        lastimg = listimg[len(listimg)-1]
        imglink = lastimg
        #.split(" ")[0]
        imglink = imglink.replace(" https", "http")
        program["img"]=imglink
        program["link"]=links[i]
        programs.append(program)
        common.log(program)
	addDirectoryItem(titles[i], {"mode":MODE_PROGRAM, "url":links[i]}, imglink, True, False, descs[i])


def viewProgram(url, page):
  if ARG_PRG:
    viewProgramType(url, page, ARG_PRG)
  else:
    r = requests.get("http://tv.aftonbladet.se/" + url)
    headers = common.parseDOM(r.text, "div", attrs = {"class": "header"})
    for header in headers:
      common.log(header)
      if header == "Senaste avsnitten":
        addDirectoryItem(localize(30701), { "mode": MODE_PROGRAM, "prg": MODE_PRG_LAST_EP, "url":url })
      if header == "Senaste klippen":
        addDirectoryItem(localize(30702), { "mode": MODE_PROGRAM, "prg": MODE_PRG_LAST_CUT, "url":url })
      if header == "Popul&auml;ra klipp":
        addDirectoryItem(localize(30703), { "mode": MODE_PROGRAM, "prg": MODE_PRG_POP_CUT, "url":url})


def viewProgramType(url, page, type):
  r = requests.get("http://tv.aftonbladet.se/" + url + "/" + type + "?page=" + page + "&pageSize=30")
  common.log("http://tv.aftonbladet.se/" + url + "/" + type + "?page=" + page + "&pageSize=30" + " -> ")
  common.log(len(r.text))
  articles = common.parseDOM(r.text, "article")
  for article in articles:
    art = {}
    link = art["link"] = common.parseDOM(article, "a", ret="href")[0]
    img = common.parseDOM(article, "img", ret = "srcset")[0]
    listimg = img.split(",")
    lastimg = art["img"] = listimg[len(listimg)-1].replace(" http", "http")
    title = art["title"] = common.parseDOM(article, "div", attrs = {"class":"sidescroll-item-header"})[0]
    desc = art["desc"] = common.parseDOM(article, "div", attrs = {"class":"sidescroll-item-description"})[0]
    #art["epi"] = common.parseDOM(article, "div", attrs = {"class":"abLabelThin sidescroll-item-episode"})[0]
    art["date"] = common.parseDOM(article, "div", attrs = {"class":"abLabelThin"})[0]

    addDirectoryItem(title, {"mode":MODE_VIDEO, "url":link}, lastimg, False, False, desc)
  if len(articles) == 30:
    addDirectoryItem(localize(30101), {"mode":MODE_PROGRAM, "url":url, "prg":type, "page":int(page)+1}, None, True, False, None)


def viewNews(url, page):
  rurl = "http://tv.aftonbladet.se/abtv/latest/news?page=" + page + "&pageSize=30"
  viewRequest(url, page, rurl)


def viewSport(url, page):
  rurl = "http://tv.aftonbladet.se/abtv/latest/sports?page=" + page + "&pageSize=30"
  viewRequest(url, page, rurl)


def viewEnt(url, page):
  rurl = "http://tv.aftonbladet.se/abtv/latest/entertainment?page=" + page + "&pageSize=30"
  viewRequest(url, page, rurl)


def viewMostSeen(url, page):
  rurl = "http://tv.aftonbladet.se/abtv/mostviewed?page=" + page + "&pageSize=30"
  viewRequest(url, page, rurl)


def viewRequest(url, page, rurl):
  common.log(rurl)
  r = requests.get(rurl)
  common.log(len(r.text))
  articles = common.parseDOM(r.text, "article")
  common.log(len(articles))
  for article in articles:
    art = {}
    link = art["link"] = common.parseDOM(article, "a", ret="href")[0]
    img = common.parseDOM(article, "img", ret = "srcset")[0]
    listimg = img.split(",")
    lastimg = art["img"] = listimg[len(listimg)-1].replace(" http", "http")
    title = art["title"] = common.parseDOM(article, "a", attrs = {"class":"title"})[0]
    art["date"] = common.parseDOM(article, "div", attrs = {"class":"abLabelThin"})[0]
    addDirectoryItem(title, {"mode":MODE_VIDEO, "url":link}, lastimg, False, False, None)
  common.log(ARG_MODE)
  if len(articles) == 30:
    addDirectoryItem(localize(30101), {"mode":ARG_MODE, "url":url, "page":int(page)+1}, None, True, False, None)


def startVideo(url):
  jsonlink = url.replace("/abtv/articles/", "https://svp.vg.no/svp/api/v1/ab/assets/") + "?appName=svp-player"
  r = requests.get(jsonlink)
  url = r.json()["streamUrls"]["mp4"]

  player = xbmc.Player()
  startTime = time.time()

  xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=url))



def addDirectoryItem(title, params, thumbnail = None, folder = True, live = False, info = None):

  li = xbmcgui.ListItem(common.replaceHTMLCodes(title))
  li.setProperty("plot", info)
  li.setProperty("rumtime", "1:11")
  li.setProperty("runtime", "1:22")
  li.setLabel2("label2")


  if thumbnail:
    li.setThumbnailImage(thumbnail)

  if not folder:
    if params["mode"] == MODE_VIDEO:
      li.setProperty("IsPlayable", "true")
  if info:
    li.setInfo("Video", info)
    #if "fanart" in info.keys():
    #  li.setArt({"fanart": info["fanart"]})

  xbmcplugin.addDirectoryItem(addon_handle, sys.argv[0] + '?' + urllib.urlencode(params), li, folder)



def getUrlParameters(arguments):
  """
  Return URL parameters as a dict from a query string
  """
  params = {}

  if arguments:

      start = arguments.find("?") + 1
      pairs = arguments[start:].split("&")

      for pair in pairs:

        split = pair.split("=")

        if len(split) == 2:
          params[split[0]] = split[1]

  return params



# Main
ARG_PARAMS = getUrlParameters(sys.argv[2])
common.log(ARG_PARAMS)
ARG_MODE = ARG_PARAMS.get("mode")
ARG_URL = urllib.unquote_plus(ARG_PARAMS.get("url", ""))
ARG_PAGE = ARG_PARAMS.get("page")
ARG_PRG = ARG_PARAMS.get("prg")
if not ARG_PAGE:
  ARG_PAGE = "1"

if not ARG_MODE:
  viewStart()
elif ARG_MODE == MODE_PROGRAM:
  viewProgram(ARG_URL, ARG_PAGE)
elif ARG_MODE == MODE_VIDEO:
  startVideo(ARG_URL)
elif ARG_MODE == MODE_A_TO_O:
  viewAtoO()
elif ARG_MODE == MODE_LATEST_NEWS:
  viewNews(ARG_URL, ARG_PAGE)
elif ARG_MODE == MODE_MOST_SEEN:
  viewMostSeen(ARG_URL, ARG_PAGE)
elif ARG_MODE == MODE_LATEST_SPORT:
  viewSport(ARG_URL, ARG_PAGE)
elif ARG_MODE == MODE_LATEST_ENT:
  viewEnt(ARG_URL, ARG_PAGE)


xbmcplugin.endOfDirectory(addon_handle)

