# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per vvvvid
# ----------------------------------------------------------
import requests, sys, inspect
from core import channeltools, support, tmdb
from platformcode import autorenumber, logger, config, platformtools

host = support.config.get_channel_url()

# Creating persistent session
current_session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'}

# Getting conn_id token from vvvvid and creating payload
login_page = host + '/user/login'
try:
    res = current_session.get(login_page, headers=headers)
    conn_id = res.json()['data']['conn_id']
    payload = {'conn_id': conn_id}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14', 'Cookie': res.headers['set-cookie']}
except:
    conn_id = ''


main_host = host + '/vvvvid/ondemand/'
# host = main_host


@support.menu
def mainlist(item):
    if conn_id:
        anime = ['/vvvvid/ondemand/anime/',
                ('Popolari',['/vvvvid/ondemand/anime/', 'movies', 'channel/10002/last/']),
                ('Nuove Uscite',['/vvvvid/ondemand/anime/', 'movies', 'channel/10007/last/']),
                ('Generi',['/vvvvid/ondemand/anime/', 'movies', 'channel/10004/last/?category=']),
                ('A-Z',['/vvvvid/ondemand/anime/', 'movies', 'channel/10003/last/?filter='])
                ]
        film =  ['/vvvvid/ondemand/film/',
                ('Popolari',['/vvvvid/ondemand/film/', 'movies', 'channel/10002/last/']),
                ('Nuove Uscite',['/vvvvid/ondemand/film/', 'movies', 'channel/10007/last/']),
                ('Generi',['/vvvvid/ondemand/film/', 'movies', 'channel/10004/last/?category=']),
                ('A-Z',['/vvvvid/ondemand/film/', 'movies', 'channel/10003/last/?filter=']),
                ]
        tvshow = ['/vvvvid/ondemand/series/',
                ('Popolari',['/vvvvid/ondemand/series/', 'movies', 'channel/10002/last/']),
                ('Nuove Uscite',['/vvvvid/ondemand/series/', 'movies', 'channel/10007/last/']),
                ('Generi',['/vvvvid/ondemand/series/', 'movies', 'channel/10004/last/?category=']),
                ('A-Z',['/vvvvid/ondemand/series/', 'movies', 'channel/10003/last/?filter='])
                ]
        show = [('Show {bold} {tv}',['/vvvvid/ondemand/show/', 'movies', '', 'tvshow']),
                ('Popolari {submenu} {tv}',['/vvvvid/ondemand/show/', 'movies', 'channel/10002/last/', 'tvshow']),
                ('Nuove Uscite {submenu} {tv}',['/vvvvid/ondemand/show/', 'movies', 'channel/10007/last/', 'tvshow']),
                ('Generi {submenu} {tv}',['/vvvvid/ondemand/show/', 'movies', 'channel/10004/last/?category=', 'tvshow']),
                ('A-Z {submenu} {tv}',['/vvvvid/ondemand/show/', 'movies', 'channel/10003/last/?filter=', 'tvshow']),
                ('Cerca Show... {bold submenu} {tv}', ['/vvvvid/ondemand/show/', 'search', '', 'tvshow'])
                ]
        kids = [('Kids {bold}',['/vvvvid/ondemand/kids/', 'movies', '', 'tvshow']),
                ('Popolari {submenu} {kids}',['/vvvvid/ondemand/kids/', 'movies', 'channel/10002/last/', 'tvshow']),
                ('Nuove Uscite {submenu} {kids}',['/vvvvid/ondemand/kids/', 'movies', 'channel/10007/last/', 'tvshow']),
                ('Generi {submenu} {kids}',['/vvvvid/ondemand/kids/', 'movies', 'channel/10004/last/?category=', 'tvshow']),
                ('A-Z {submenu} {kids}',['/vvvvid/ondemand/kids/', 'movies', 'channel/10003/last/?filter=', 'tvshow']),
                ('Cerca Kids... {bold submenu} {kids}', ['/vvvvid/ondemand/kids/', 'search', '', 'tvshow'])
                ]
    else:
        Top = [("Visibile solo dall'Italia {bold}",[])]
    return locals()


def search(item, text):
    logger.debug(text)
    itemlist = []
    if conn_id:
        if 'film' in item.url: item.contentType = 'movie'
        else: item.contentType = 'tvshow'
        item.search = text
        try:
            itemlist = movies(item)
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)
            return []
    return itemlist


def newest(category):
    item = support.Item()
    item.args = 'channel/10007/last/'
    if category == 'movie':
        item.contentType = 'movie'
        item.url = main_host + 'film/'
    if category == 'tvshow':
        item.contentType = 'tvshow'
        item.url = main_host + 'series/'
    if category == 'anime':
        item.contentType = 'tvshow'
        item.url = main_host + 'anime/'
    return movies(item)


def movies(item):

    itemlist = []
    # logger.dbg()
    if not item.args:
        json_file =loadjs(item.url + 'channel/10005/last/')
        logger.debug(json_file)
        make_itemlist(itemlist, item, json_file)
        itemlist = support.pagination(itemlist, item, 'movies')
        if item.contentType != 'movie': autorenumber.start(itemlist)
        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    elif ('=' not in item.args) and ('=' not in item.url):
        json_file=loadjs(item.url + item.args)
        make_itemlist(itemlist, item, json_file)

    elif '=' in item.args:
        json_file = current_session.get(item.url + 'channels', headers=headers, params=payload).json()
        Filter = support.match(item.args, patron=r'\?([^=]+)=').match
        keys = [i[Filter] for i in json_file['data'] if Filter in i][0]
        for key in keys:
            if key not in ['1','2']:
                itemlist.append(
                    item.clone(title = support.typo(key.upper() if Filter == 'filter' else key['name'], 'bold'),
                               url =  item.url + item.args + (key if Filter == 'filter' else str(key['id'])),
                               action = 'movies',
                               args = 'filters'))

    else:
        json_file=loadjs(item.url)
        item.args=''
        make_itemlist(itemlist, item, json_file)

    if 'category' in item.args:
        support.thumb(itemlist,mode='genre')

    return itemlist


def episodes(item):
    itemlist = []
    if config.get_setting("window_type") == 0:
        item.window = True
        item.folder = False

    if item.episodes:
        episodes = item.episodes
        show_id = item.show_id 
        season_id = item.season_id
    else:
        json_file = current_session.get(item.url, headers=headers, params=payload).json()['data']
        if len(json_file) > 1:
            for key in json_file:
                itemlist.append(item.clone(title=support.typo(key['name'],'bold'), show_id = str(key['show_id']), season_id = str(key['season_id']), episodes = key['episodes']))
            return itemlist
        else:
            episodes = json_file[0]['episodes']
            show_id = str(json_file[0]['show_id'])
            season_id = str(json_file[0]['season_id'])

    for episode in episodes:
        try:
            title = episode['title'].encode('utf8')
        except:
            title = episode['title']

        if type(title) == tuple: title = title[0]
        itemlist.append(
            item.clone(title = title,
                       contentType = 'episode',
                       contentEpisodeNumber = int(episode['number']),
                       url=  main_host + show_id + '/season/' + str(season_id),
                       action= 'findvideos',
                       video_id= episode['video_id']))

    if inspect.stack()[1][3] not in ['find_episodes']:
        autorenumber.start(itemlist, item)
        for i in itemlist:
            logger.debug(i)

    support.videolibrary(itemlist,item)
    return itemlist

def findvideos(item):
    from lib import vvvvid_decoder
    itemlist = []
    if item.contentType == 'movie':
        json_file = current_session.get(item.url, headers=headers, params=payload).json()
        item.url = main_host + str(json_file['data'][0]['show_id']) + '/season/' + str(json_file['data'][0]['episodes'][0]['season_id']) + '/'
        item.video_id = json_file['data'][0]['episodes'][0]['video_id']
    logger.info('url=',item.url)
    json_file = current_session.get(item.url, headers=headers, params=payload).json()
    for episode in json_file['data']:
        logger.info(episode)
        if episode['video_id'] == item.video_id:
            url = vvvvid_decoder.dec_ei(episode['embed_info'] or episode['embed_info_sd'])
            if 'youtube' in url: item.url = url
            item.url = url.replace('manifest.f4m','master.m3u8').replace('http://','https://').replace('/z/','/i/')
            if 'https' not in item.url:
                url = support.match('https://or01.top-ix.org/videomg/_definst_/mp4:' + item.url + '/playlist.m3u').data
                url = url.split()[-1]
                itemlist.append(
                    item.clone(action= 'play',
                               title=config.get_localized_string(30137),
                               url= 'https://or01.top-ix.org/videomg/_definst_/mp4:' + item.url + '/' + url,
                               server= 'directo')
                )
            else:
                key_url = 'https://www.vvvvid.it/kenc?action=kt&conn_id=' + conn_id + '&url=' + item.url.replace(':','%3A').replace('/','%2F')
                key = vvvvid_decoder.dec_ei(current_session.get(key_url, headers=headers, params=payload).json()['message'])

                itemlist.append(
                    item.clone(action= 'play',
                               title=config.get_localized_string(30137),
                               url= item.url + '?' + key,
                               server= 'directo'))

    return support.server(item, itemlist=itemlist, Download=False)

def make_itemlist(itemlist, item, data):
    search = item.search if item.search else ''
    infoLabels = {}

    for key in data['data']:
        if search.lower() in encode(key['title']).lower():
            title = encode(key['title'])
            fulltitle=title.split('-')[0].strip()
            infoLabels['year'] = key['date_published']
            infoLabels['title'] = fulltitle
            if item.contentType != 'movie': infoLabels['tvshowtitle'] = fulltitle
            itemlist.append(
                item.clone(title = support.typo(title, 'bold'),
                           fulltitle= title,
                           show= title,
                           url= main_host + str(key['show_id']) + '/seasons/',
                           action= 'findvideos' if item.contentType == 'movie' else 'episodes',
                           contentType = item.contentType,
                           contentSerieName= fulltitle if item.contentType != 'movie' else '',
                           contentTitle= fulltitle if item.contentType == 'movie' else '',
                           infoLabels=infoLabels,
                           videolibrary=False))
    return itemlist

def loadjs(url):
    if '?category' not in url:
        url += '?full=true'
    logger.debug('Json URL;',url)
    json = current_session.get(url, headers=headers, params=payload).json()
    return json


def encode(text):
    if sys.version_info[0] >= 3:
        return text
    else:
        return text.encode('utf8')