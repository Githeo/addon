# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per ilcorsaronero
# ------------------------------------------------------------

from core import support
from platformcode import logger

# def findhost(url):
#     data = support.httptools.downloadpage(url).data
#     url = support.scrapertools.find_single_match(data, '<li><a href="([^"]+)')
#     return url[:-1] if url.endswith('/') else url

host = support.config.get_channel_url()
logger.debug('HOST',host)
# host = 'https://ilcorsaronero.xyz'
headers = [['Referer', host]]


@support.menu
def mainlist(item):

    menu = [
        ('BDRiP {film}', ['/categoria.php?active=0&category=1&order=data&by=DESC&page=', 'movies', [0, 'movie', True], 'undefined']),
        ('Cerca BDRiP... {submenu} {film}', ['/torrent-ita/1/', 'search', ['search', 'movie', True], 'movie']),
        ('DVD {film}', ['/categoria.php?active=0&category=20&order=data&by=DESC&page=', 'movies', [0, 'movie', True], 'undefined']),
        ('Cerca DVD... {submenu} {film}', ['/torrent-ita/20/', 'search', ['search', 'movie', True], 'movie']),
        ('Screener {film}', ['/categoria.php?active=0&category=19&order=data&by=DESC&page=', 'movies', [0, 'movie', True], 'undefined']),
        ('Cerca Screener.. {submenu} {film}', ['/torrent-ita/19/', 'search', ['search', 'movie', True], 'movie']),
        ('Serie TV', ['/categoria.php?active=0&category=15&order=data&by=DES&page=', 'movies', [0 , 'tvshow', True], 'tvshow']),
        ('Cerca Serie TV.. {submenu}', ['/torrent-ita/15/', 'search', ['search', 'tvshow',True], 'tvshow']),
        ('Anime', ['/categoria.php?active=0&category=5&order=data&by=DESC&page=', 'movies', [0, 'anime', True], 'tvshow']),
        ('Cerca Anime.. {submenu}', ['/torrent-ita/5/', 'search', ['search', 'anime', True], 'tvshow']),
        ('Musica', ['/categoria.php?active=0&category=2&order=data&by=DESC&page=', 'movies', [0, 'music', False], 'music']),
        ('Cerca Musica.. {submenu}', ['/torrent-ita/2/', 'search', ['search', 'music', False], 'music']),
        ('Audiolibri {musica}', ['/categoria.php?active=0&category=18&order=data&by=DESC&page=', 'movies', [0, 'music', False], 'music']),
        ('Cerca Audiolibri.. {submenu}', ['/torrent-ita/18/', 'search', ['search', 'music', False], 'music']),
        # mostrerebbe anche risultati non "multimediali" e allungherebbero inutilmente la ricerca globale
        # ('Altro {film}', ['/categoria.php?active=0&category=4&order=data&by=DESC&page=', 'movies', [0, 'other', False]]),
        # ('Cerca altro.. {submenu}', ['/torrent-ita/4/', 'search', ['search', 'other', False]]),
        # ('Cerca Tutto... {color kod bold}', ['/argh.php?search=', 'search', ['search', 'all', False]])
    ]

    return locals()


@support.scrape
def movies(item):
    # debug = True
    sceneTitle = item.args[2]
    if item.args[1] in ['tvshow', 'anime', 'music', 'other']:
        patron = r'>[^"<]+'
    else:
        patron = r'>(?P<quality>[^"<]+)'
    patron += r'</td> <TD[^>]+><A class="tab" HREF="(?P<url>[^"]+)"\s*>(?P<title>[^<]+)<[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>(?P<size>[^<]+)<[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>(?P<seed>[^<]+)'

    if 'search' not in item.args:
        item.url += str(item.args[0])
        def itemlistHook(itemlist):
            args = item.args
            args[0] += 1
            support.nextPage(itemlist, item, 'movies', next_page=item.url, total_pages=15)
            return itemlist
    return locals()


def search(item, text):
    logger.debug( text)
    if 'all' in item.args:
        item.url += text
    else:
        item.url += text + '.html'
    try:
        return movies(item)
    # Cattura l' eccezione così non interrompe la ricerca globle se il canale si rompe!
    except:
        import sys
        for line in sys.exc_info():
            logger.error("search except: %s" % line)
        return []


def findvideos(item):
    if item.contentType == 'tvshow': item.contentType = 'episode'
    Videolibrary = True if 'movie' in item.args else False
    return support.server(item, support.match(item.url, patron=r'"(magnet[^"]+)').match, Videolibrary=Videolibrary)
