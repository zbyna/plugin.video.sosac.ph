# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2015 Libor Zoubek + jondas
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re

import urllib
import urllib2
import cookielib
import sys
import json
import util
from provider import ContentProvider
import xbmcgui
import concurrent.futures
import time
from translatedStrings import *
from csfd import csfd
from bs4 import BeautifulSoup
import requests
import itertools
import simplecache
import string
import locale
import unidecode


sys.setrecursionlimit(10000)

MOVIES_BASE_URL = "http://movies.prehraj.me"
MOVIES_YEAR = "ROKY/"
YEAR_PARAM = "rok"
TV_SHOW_FLAG = "#tvshow#"
ISO_639_1_CZECH = "cs"

# JSONs
URL = "http://tv.sosac.to"
SUBSCRIPTION_MANAGER = "subscription_manager"

J_MOVIES_GENRE = "/vystupy5981/souboryzanry.json"
J_MOVIES_MOST_POPULAR = "/vystupy5981/moviesmostpopular.json"
J_MOVIES_RECENTLY_ADDED = "/vystupy5981/moviesrecentlyadded.json"
# hack missing json with a-z series
J_MOVIES_A_TO_Z_TYPE = "/vystupy5981/souboryaz.json"
J_TV_SHOWS_A_TO_Z_TYPE = "/vystupy5981/tvpismenaaz/"
J_TV_SHOWS = "/vystupy5981/tvpismena/"
J_SERIES = "/vystupy5981/serialy/"
J_TV_SHOWS_MOST_POPULAR = "/vystupy5981/tvshowsmostpopular.json"
J_TV_SHOWS_RECENTLY_ADDED = "/vystupy5981/tvshowsrecentlyadded.json"
J_SEARCH = "/jsonsearchapi.php?q="
STREAMUJ_URL = "http://www.streamuj.tv/video/"
IMAGE_URL = "http://movies.sosac.tv/images/"
IMAGE_MOVIE = IMAGE_URL + "75x109/movie-"
IMAGE_SERIES = IMAGE_URL + "558x313/serial-"
IMAGE_EPISODE = URL

RATING = 'r'
LANG = 'd'
QUALITY = 'q'
DESCRIPTION = 'p'
RATING_STEP = 2


class SosacContentProvider(ContentProvider):
    ISO_639_1_CZECH = None
    par = None

    def __init__(self, username=None, password=None, filter=None, reverse_eps=False,
                 force_english=False, use_memory_cache=True):
        ContentProvider.__init__(self, name='sosac.ph', base_url=MOVIES_BASE_URL,
                                 username=username, password=password, filter=filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        self.reverse_eps = reverse_eps
        self.force_english = force_english
        self.cache = simplecache.SimpleCache()
        self.cache.enable_mem_cache = use_memory_cache

    def on_init(self):
        custom_sort_dict = {'czech': 'cs_CZ.utf8', 'english': 'en_GB.utf8', 'os': ''}
        if self.force_english:
            self.ISO_639_1_CZECH = 'en'
            custom_sort = ADDON_SETTINGS_GET('force-sort')
            try:
                locale.setlocale(locale.LC_ALL, custom_sort)  # Windoof
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, custom_sort_dict[custom_sort])  # Linux
                except locale.Error:
                    locale.setlocale(locale.LC_ALL, custom_sort_dict['os'])
                    xbmcgui.Dialog().notification(
                        'Locale missing !!!',
                        'Generate locale' + custom_sort_dict[custom_sort] + 'for your system',
                        time=1000, sound=False)
                    xbmcgui.Dialog().notification(
                        'Deafult system locale',
                        'Default locale from OS will be used',
                        time=1000, sound=False)
                    ADDON_SETTINGS_SET(id='force-sort', value='os')
        else:
            ADDON_SETTINGS_SET(id='force-ch', value='false')
            self.ISO_639_1_CZECH = ISO_639_1_CZECH

    def capabilities(self):
        return ['resolve', 'categories', 'search']

    def categories(self):
        result = []
        for title, url in [
                (MOVIES, URL + J_MOVIES_A_TO_Z_TYPE),
                (TV_SHOWS, URL + J_TV_SHOWS_A_TO_Z_TYPE),
                (MOVIES_BY_GENRES, URL + J_MOVIES_GENRE),
                (MOVIES_BY_YEAR, URL + "/" + MOVIES_YEAR),
                (MOVIES_MOST_POPULAR, URL + J_MOVIES_MOST_POPULAR),
                (TV_SHOWS_MOST_POPULAR, URL + J_TV_SHOWS_MOST_POPULAR),
                (MOVIES_RECENTLY_ADDED, URL + J_MOVIES_RECENTLY_ADDED),
                (TV_SHOWS_RECENTLY_ADDED, URL + J_TV_SHOWS_RECENTLY_ADDED),
                (CSFD_MAIN, CSFD_BASE + 'level_0'),
                (SPRAVCE_ODBERU, SUBSCRIPTION_MANAGER)]:
            item = self.dir_item(title=title, url=url)
            if title == MOVIES or title == TV_SHOWS or title == MOVIES_RECENTLY_ADDED:
                item['menu'] = {"[B][COLOR red]" + ADD_ALL_TO_LIBRARY + "[/COLOR][/B]": {
                    'action': 'add-all-to-library', 'title': title, 'url': url}}
            if title == SPRAVCE_ODBERU:
                item['menu'] = {"[B][COLOR yellow]" + REMOVE_ALL_FROM_SUBSCRIPTION +
                                "[/COLOR][/B]": {
                                    'action': 'remove-all-from-subscription', 'title': title}}
            result.append(item)
        return result

    def search(self, keyword):
        if len(keyword) < 3 or len(keyword) > 100:
            return [self.dir_item(
                title="Search query must be between 3 and 100 characters long!", url="fail")]
        return self.list_videos(URL + J_SEARCH + urllib.quote_plus(keyword))

    def a_to_z(self, url):
        result = []
        __letters = ['0-9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                     'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        if self.parent.settings['force-ch']:
            __letters.append('ch')
        __letters.sort(cmp=locale.strcoll)
        for letter in __letters:
            item = self.dir_item(title=letter.upper())
            if self.force_english:
                item['url'] = url + '#' + letter.upper()
            else:
                item['url'] = URL + url + letter + ".json"
            result.append(item)
        return result

    @staticmethod
    def particular_letter(url):
        return "a-z/" in url

    def has_tv_show_flag(self, url):
        return TV_SHOW_FLAG in url

    def list(self, url):
        util.info("Examining url " + url)
        if J_MOVIES_A_TO_Z_TYPE in url:
            return self.load_json_list(url)
        if J_MOVIES_GENRE in url:
            return self.load_json_list(url)
        if MOVIES_YEAR in url:
            return self.list_by_year(url)
        if J_MOVIES_MOST_POPULAR in url:
            return self.list_videos(url)
        if J_MOVIES_RECENTLY_ADDED in url:
            return self.list_videos(url)
        if J_TV_SHOWS_A_TO_Z_TYPE in url:
            return self.a_to_z(J_TV_SHOWS)
        if J_TV_SHOWS in url:
            return self.list_series_letter(url)
        if J_SERIES in url:
            return self.list_episodes(url)
        if J_TV_SHOWS_MOST_POPULAR in url:
            return self.list_series_letter(url)
        if J_TV_SHOWS_RECENTLY_ADDED in url:
            return self.list_recentlyadded_episodes(url)
        if SUBSCRIPTION_MANAGER in url:
            return self.subscription_manager_tvshows_all_xml()
        if CSFD_BASE in url:
            return self.csfd_lists(url)
        return self.list_videos(url)

    def load_json_list(self, url):
        result = []
        data = util.request(url)
        json_list = json.loads(data)
        if self.force_english and (J_MOVIES_A_TO_Z_TYPE in url):
            json_list = {key.title(): 'p/' + key.title() for key in json_list}
            if self.parent.settings['force-ch']:
                json_list[u'CH'] = u'p/CH'
        for key, value in json_list.iteritems():
            item = self.dir_item(title=key.upper())
            item['url'] = value
            result.append(item)
            item['menu'] = {"[B][COLOR red]" + ADD_ALL_TO_LIBRARY + "[/COLOR][/B]":
                            {'action': 'add-all-to-library',
                             'title': MOVIES_BY_GENRES,
                             'url': value}
                            }
        return sorted(result, key=lambda i: i['title'], cmp=locale.strcoll)

    def list_videos_create(self, videoArray):
        result = []
        for video in videoArray:
            item = self.video_item()
            namePom = self.get_video_name(video)
            if video['y']:
                item['year'] = int(video['y'])
            item['title'] = namePom
            item['img'] = IMAGE_MOVIE + video['i']
            urlPom = video['l'] if video['l'] else ""
            item['url'] = urlPom
            if RATING in video:
                item['rating'] = video[RATING] * RATING_STEP
            if LANG in video:
                item['lang'] = video[LANG]
            if QUALITY in video:
                item['quality'] = video[QUALITY]
            item['menu'] = {"[B][COLOR red]" + ADD_TO_LIBRARY + "[/COLOR][/B]":
                            {'url': urlPom,
                                'action': 'add-to-library',
                             'name': self.get_library_video_name(video),
                             'type': LIBRARY_TYPE_VIDEO}}
            result.append(item)
        return result

    def list_videos(self, url):
        if self.force_english and ('p/' in url):
            pom = self.all_movies_by_name('n')
            pom_url = url.split('/')[1]
            force_ch = ADDON_SETTINGS_GET('force-ch') == 'true'
            if force_ch:
                json_video_array = sorted(pom[url.split('/')[1]],
                                          key=lambda k: k['n']['en'],
                                          cmp=locale.strcoll)
            else:
                if pom_url == 'C':
                    pom_list = pom['C']
                    pom_list.extend(pom['CH'])
                else:
                    pom_list = pom[pom_url]
                json_video_array = sorted(pom_list,
                                          key=lambda k: k['n']['en'],
                                          cmp=locale.strcoll)
            return self.list_videos_create(json_video_array)
        else:
            data = util.request(url)
            json_video_array = json.loads(data)
            if self.force_english and J_MOVIES_MOST_POPULAR not in url:
                json_video_array.sort(key=lambda k: k['n']['en'],
                                      cmp=locale.strcoll)
            return self.list_videos_create(json_video_array)

    def list_series_create(self, json_series_array):
        result = []
        i = 0
        for serial in json_series_array:
            item = self.dir_item()
            item['title'] = self.get_localized_name(serial['n'])
            if serial['y']:
                item['year'] = int(serial['y'])
            item['img'] = IMAGE_SERIES + serial['i']
            item['url'] = serial['l']
            if RATING in serial:
                item['rating'] = serial[RATING] * RATING_STEP
            if DESCRIPTION in serial:
                item['plot'] = serial['p']
            subs = self.get_subs()
            if item['url'] in subs:
                item['menu'] = {
                    "[B][COLOR red]" + REMOVE_FROM_SUBSCRIPTION + "[/COLOR][/B]": {
                        'url': item['url'],
                        'action': 'remove-subscription',
                        'name': self.get_library_video_name(serial)
                    }
                }
                item['title'] = '[B][COLOR yellow]*[/COLOR][/B] ' + item['title']
                result.insert(i, item)
                i += 1
            else:
                item['menu'] = {
                    "[B][COLOR red]" + ADD_TO_LIBRARY + "[/COLOR][/B]": {
                        'url': item['url'],
                        'action': 'add-to-library',
                        'name': self.get_library_video_name(serial),
                        'type': LIBRARY_TYPE_TVSHOW
                    },
                    "[B][COLOR yellow]" + SUBSCRIBE + "[/COLOR][/B]": {
                        'url': item['url'],
                        'action': 'add-subscription',
                        'name': self.get_library_video_name(serial),
                        'type': LIBRARY_TYPE_TVSHOW
                    }
                }
                result.append(item)
        return result

    def list_series_letter(self, url):
        if self.force_english and J_TV_SHOWS_MOST_POPULAR not in url:
            pom = self.all_tvshows_by_name('n')
            pom_url = url.split('#')[1]
            force_ch = ADDON_SETTINGS_GET('force-ch') == 'true'
            if force_ch:
                json_series_array = sorted(pom[pom_url],
                                           key=lambda k: k['n']['en'],
                                           cmp=locale.strcoll)
            else:
                if pom_url == 'C':
                    pom_list = pom['C']
                    pom_list.extend(pom['CH'])
                else:
                    pom_list = pom[pom_url]
                json_series_array = sorted(pom_list,
                                           key=lambda k: k['n']['en'],
                                           cmp=locale.strcoll)
        else:
            data = util.request(url)
            json_series_array = json.loads(data)
        return self.list_series_create(json_series_array)

    def time_usage(func):
        def wrapper(*args, **kwargs):
            beg_ts = time.time()
            retval = func(*args, **kwargs)
            end_ts = time.time()
            util.info('"%s" - elapsed time: %f' % (func.__name__, end_ts - beg_ts))
            return retval
        return wrapper

    def all_videos(self):
        seznam = json.loads(util.request(URL + J_MOVIES_A_TO_Z_TYPE))
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            pom = {executor.submit(self.get_data_cached, seznam[item]): item for item in seznam}
            for pp in concurrent.futures.as_completed(pom):
                for p in json.loads(pp.result()):
                    yield p

    def all_tvshows(self):
        seznam = ['0-9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'e', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            pom = executor.map(self.get_data_cached, (URL + J_TV_SHOWS + item + ".json"
                                                      for item in seznam), timeout=5)
            for pp in pom:
                for p in json.loads(pp):
                    yield p

    # @time_usage
    @simplecache.use_cache(cache_days=7)
    def all_tvshows_with_key(self, keyForDict):
        # =======================================================================================
        # Downloads all json for individual letters
        # and creates {keyForDict : [ {tvshows} ]} from them so that
        # movies in list contain keyForDict
        # =======================================================================================
        result = {}
        for p in self.all_tvshows():
            if p[keyForDict] in result:
                result[p[keyForDict]].append(p)
            else:
                result[p[keyForDict]] = [p]
        return result

    # @time_usage
    @simplecache.use_cache(cache_days=7)
    def all_movies_with_key(self, keyForDict):
        # =======================================================================================
        # Downloads all json for individual letters
        # and creates {keyForDict : [ {movies} ]} from them so that
        # movies in list contain keyForDict
        # =======================================================================================
        result = {}
        for p in self.all_videos():
            if p[keyForDict] in result:
                result[p[keyForDict]].append(p)
            else:
                result[p[keyForDict]] = [p]
        return result

    @simplecache.use_cache(cache_days=7)
    def all_movies_by_name(self, keyForDict):
        result = {}
        for p in self.all_videos():
            pom = p[keyForDict]['en'][0:2]
            if pom == 'Ch':
                pom = 'CH'
            else:
                pom = pom[0]
                if pom not in string.ascii_letters:
                    pom = unidecode.unidecode(pom)
                    if pom not in string.ascii_letters:
                        pom = '0-9'
            if pom in result:
                result[pom].append(p)
            else:
                result[pom] = [p]
        return result

    @simplecache.use_cache(cache_days=7)
    def all_tvshows_by_name(self, keyForDict):
        result = {}
        for p in self.all_tvshows():
            pom = p[keyForDict]['en'][0:2]
            if pom == 'Ch':
                pom = 'CH'
            else:
                pom = pom[0]
                if pom not in string.ascii_letters:
                    pom = unidecode.unidecode(pom)
                    if pom not in string.ascii_letters:
                        pom = '0-9'
            if pom in result:
                result[pom].append(p)
            else:
                result[pom] = [p]
        return result

    def list_year(self, url):
        data = self.all_movies_with_key('y')
        year = url.split('=')
        json_video_array = data[year[1]]
        if self.force_english:
            json_video_array.sort(key=lambda k: k['n']['en'],
                                  cmp=locale.strcoll)
        else:
            json_video_array.sort(key=lambda k: k['n']['cs'])
        return self.list_videos_create(json_video_array)

    def list_by_year(self, url):
        if "?" + YEAR_PARAM in url:
            return self.list_year(url)
        else:
            result = []
            data = self.all_movies_with_key('y')
            for s in sorted(data.keys(), reverse=True):
                urlPom = url + "?" + YEAR_PARAM + "=" + s
                item = {'url': urlPom, 'title': s, 'type': 'dir'}
                item['menu'] = {"[B][COLOR red]" + ADD_ALL_TO_LIBRARY + "[/COLOR][/B]": {
                                'action': 'add-all-to-library',
                                'title': MOVIES_BY_YEAR,
                                'url': urlPom}}
                self._filter(result, item)
            return result

    def list_episodes(self, url):
        result = []
        data = util.request(url)
        json_series = json.loads(data)
        for series in json_series:
            for series_key, episode in series.iteritems():
                for episode_key, video in episode.iteritems():
                    item = self.video_item()
                    item['title'] = series_key + "x" + episode_key + " - " + video['n']
                    if video['i'] is not None:
                        item['img'] = IMAGE_EPISODE + video['i']
                    item['url'] = video['l'] if video['l'] else ""
                    result.append(item)
        if not self.reverse_eps:
            result.reverse()
        return result

    def list_recentlyadded_episodes(self, url):
        result = []
        data = util.request(url)
        json_series = json.loads(data)
        if self.force_english:
            json_series.sort(key=lambda k: k['t']['en'], cmp=locale.strcoll)
        for episode in json_series:
            item = self.video_item()
            item['title'] = self.get_episode_recently_name(episode)
            if episode['i'] is not None:
                item['img'] = IMAGE_EPISODE + episode['i']
            item['url'] = episode['l']
            result.append(item)
        return result

    def get_video_name(self, video):
        name = self.get_localized_name(video['n'])
        year = (" (" + video['y'] + ") ") if video['y'] else " "
        quality = ("- " + video[QUALITY].upper()) if video[QUALITY] else ""
        return name + year + quality

    def get_library_video_name(self, video):
        name = self.get_localized_name(video['n'])
        year = (" (" + video['y'] + ") ") if video['y'] else " "
        return (name + year).encode('utf-8')

    def get_episode_recently_name(self, episode):
        serial = self.get_localized_name(episode['t']) + ' '
        series = episode['s'] + "x"
        number = episode['e'] + " - "
        name = self.get_localized_name(episode['n'])
        return serial + series + number + name

    def get_localized_name(self, names):
        return (names[self.ISO_639_1_CZECH]
                if self.ISO_639_1_CZECH in names else names[ISO_639_1_CZECH])

    # @cached(ttl=24)
    @simplecache.use_cache(cache_days=3)
    def get_data_cached(self, url):
        return util.request(url)

    @simplecache.use_cache(cache_days=3)
    def requests_get_data_cached(self, url):
        return requests.get(url).text

    def add_to_library_decorator(func):
        def wrapper(*args, **kwargs):
            pomSeznam, question, libraryType = func(*args, **kwargs)
            total = len(pomSeznam)
            for i, video in enumerate(pomSeznam):
                item = video['menu']['[B][COLOR red]' + ADD_TO_LIBRARY + '[/COLOR][/B]']
                item["update"] = True
                item["notify"] = True
                item["type"] = libraryType
                args[0].parent.add_item(item, question)
                procento = int(float(i) / total * 100)
                args[0].parent.dialog.update(procento, video['title'])
                if args[0].parent.dialog.iscanceled():
                    return
        return wrapper

    @add_to_library_decorator
    def movies_all_to_library(self):
        result = []
        for item in self.all_videos():
            result.append(item)
        return (self.list_videos_create(result), False, LIBRARY_TYPE_VIDEO)

    @add_to_library_decorator
    def tvshows_all_to_library(self):
        result = []
        dialog = xbmcgui.Dialog()
        question = dialog.yesno(SUBSCRIBE_ALL_TV_SHOWS, '')
        del dialog
        for item in self.all_tvshows():
            result.append(item)
        return (self.list_series_create(result), question, LIBRARY_TYPE_TVSHOW)

    @add_to_library_decorator
    def list_to_library(self, url):
        return (self.list_videos(url), False, LIBRARY_TYPE_VIDEO)

    @add_to_library_decorator
    def generated_list_to_library(self, url):
        return (self.list_year(url), False, LIBRARY_TYPE_VIDEO)

    # @time_usage
    def subscription_manager_tvshows_all_xml(self):
        shows = []
        for serial in self.all_tvshows():
            shows.append(serial)
        if self.force_english:
            shows.sort(key=lambda k: k['n']['en'], cmp=locale.strcoll)
        return self.list_series_create(shows)

    def prepare_dirs(self, menuItems):
        # ========================================================================================
        # prepares dirs according to csfd.py for showing in Kodi
        # ========================================================================================
        result = []
        for di in menuItems:
            item = self.dir_item(title=di['name'])
            item['url'] = di['url']
            result.append(item)
        return result

    def extract_info(self, url, itemType):
        # ========================================================================================
        # extracts 'film' or 'tvseries' info from <table class="content ui-table-list striped">
        # and returns list of media items presented in sosac
        # ========================================================================================
        stranka = self.requests_get_data_cached(url)
        polivka = BeautifulSoup(stranka, 'html.parser')
        tabulka = polivka.find('table', class_="content ui-table-list striped")
        filmy = [film.get_text() for film in tabulka.findAll('td', class_='film')]
        hodnoceni = [prumer.get_text() for
                     prumer in tabulka.findAll('td', class_='average')]
        idFilmu = [film.get('id') for film in tabulka.findAll('td', class_='film')]
        if itemType == 'film':
            indexFilms = self.all_movies_with_key('c')
        else:
            indexFilms = self.all_tvshows_with_key('c')
        result = []
        for idf, fil, hod in itertools.izip(idFilmu, filmy, hodnoceni):
            id_ = idf.split('-')[1]
            rating = float(hod.replace(',', '.').replace('%', '')) / 10 / 2
            if indexFilms.get(id_, None):
                indexFilms[id_][0]['r'] = rating
                result.append(indexFilms[id_][0])
            else:
                neni = u' Není na sosáči'
                nothing = ' Not available in Sosac'
                result.append({"q": "", "i": "",
                               "n": {"cs": ''.join(['[COLOR red]', fil, neni, "[/COLOR]"]),
                                     "en": ''.join(['[COLOR red]', fil, nothing, "[/COLOR]"])},
                               "s": [], "d": [], "y": '', "c": "", "m": "",
                               "r": rating, "g": [], "l": ""})
        return result

    def extract_info_genres(self, url, ZEBRICKY_items_SPEC):
        stranka = self.requests_get_data_cached(url)
        polivka = BeautifulSoup(stranka, 'html.parser')
        tabulka = polivka.find('select', attrs={'name': 'genre'})
        genres = [(genre.get_text(), genre['value']) for
                  genre in tabulka.findAll('option')]
        genres.remove((u'-všechny-', u''))
        items = []
        for name, kod in genres:
            urlPom = ZEBRICKY_items_SPEC.replace('genre=', ''.join(['genre=', kod]))
            items.append({'url': CSFD_BASE + urlPom + '&show=complete',
                          'name': name.encode('utf8')})
        return items

    def extract_info_awards(self, url, tableClass):
        # ========================================================================================
        # extracts 'awards' info from <div class=tableClass>
        # and returns list of media presented in sosac
        # ========================================================================================
        stranka = self.requests_get_data_cached(url)
        polivka = BeautifulSoup(stranka, 'html.parser')
        tabulka = polivka.findAll('div', attrs={'class': tableClass})
        result = []
        indexFilms = self.all_movies_with_key('c')
        for tab in tabulka:
            rok = int(tab.find('h2').get_text()[:5]) - 1
            result.append({"q": "", "i": "", "n": {"cs": ''.join(['[COLOR blue]', '----- ',
                                                                  str(rok + 1), ' -----',
                                                                  "[/COLOR]"]),
                                                   "en": ''.join(['[COLOR blue]', '----- ',
                                                                  str(rok + 1), ' -----'
                                                                  "[/COLOR]"])},
                           "s": [], "d": [], "y": '', 'r': 0, "c": '', "m": "", "g": [], "l": ""})
            filmy = [(odkaz.get_text(),
                      odkaz[('href')].replace('/film/', '').split('-')[0])
                     for odkaz in tab.find('div', attrs={'class': "all"})
                     .find('table').find('tr')
                     .findAll('a', href=re.compile('^/film/'))]
            for f in filmy:
                id_ = f[1]
                naz = f[0] + ' (%s) ' % (rok)
                if indexFilms.get(id_, None):
                    # indexFilms[id][0]['r'] = 'johoho :-)'
                    result.append(indexFilms[id_][0])
                else:
                    neni = u' Není na sosáči'
                    nothing = ' Not available in Sosac'
                    result.append({"q": "", "i": "", "n": {"cs": ''.join(['[COLOR red]', naz, neni,
                                                                          "[/COLOR]"]),
                                                           "en": ''.join(['[COLOR red]', naz,
                                                                          nothing, "[/COLOR]"])},
                                   "s": [], "d": [], "y": '', "c": '', "m": "", "g": [], "l": ""})
        return result

    def extract_info_roky(self, url):
        # ========================================================================================
        # extracts years urls from <div class="navigation">
        # ========================================================================================
        stranka = self.requests_get_data_cached(url)
        polivka = BeautifulSoup(stranka, 'html.parser')
        tabulka = polivka.find('div', attrs={'class': "navigation"})
        odkazy = [{'name': odkaz.get_text(), 'url': CSFD_BASE + odkaz[('href')]} for
                  odkaz in tabulka.findAll('a')]
        o = odkazy[-1]
        if o['name'] not in o['url']:
            o['url'] += '?years=' + o['name']
        odkazy.sort(reverse=True)
        return odkazy

    def csfd_lists(self, url):
        if 'level_0' in url:
            return self.prepare_dirs(csfd['level_0'])
        if 'zebricky/' in url:
            if 'level_1' in url:
                return self.prepare_dirs(csfd['level_0'][0]['level_1'])
            if ZEBRICKY_FILMY_NEJ in url:
                result = self.extract_info(url, 'film')
                return self.list_videos_create(result)
            if ZEBRICKY_TVSHOW_NEJ in url:
                result = self.extract_info(url, 'tvshow')
                return self.list_series_create(result)
            if ZEBRICKY_FILMY_SPEC in url:
                result = self.extract_info_genres(url, ZEBRICKY_FILMY_SPEC)
                return self.prepare_dirs(result)
            if ZEBRICKY_TVSHOW_SPEC in url:
                result = self.extract_info_genres(url, ZEBRICKY_TVSHOW_SPEC)
                return self.prepare_dirs(result)
            if ZEBRICKY_FILMY_SPEC_GENRE in url:
                result = self.extract_info(url, 'film')
                return self.list_videos_create(result)
            if ZEBRICKY_TVSHOW_SPEC_GENRE in url:
                result = self.extract_info(url, 'tvshow')
                return self.list_series_create(result)
        if 'oceneni/' in url:
            if 'level_1' in url:
                return self.prepare_dirs(csfd['level_0'][1]['level_1'])
            if OCENENI_OSCAR in url:
                if OCENENI_OSCAR_ROKY in url:
                    result = self.extract_info_awards(url, 'th-1 ct-general oscars')
                    return self.list_videos_create(result)
                odkazy = self.extract_info_roky(url)
                return self.prepare_dirs(odkazy)
            if OCENENI_ZLATA_PALMA in url:
                if OCENENI_ZLATA_PALMA_ROKY in url:
                    result = self.extract_info_awards(url, 'th-1 ct-general cannes-iff')
                    return self.list_videos_create(result)
                odkazy = self.extract_info_roky(url)
                return self.prepare_dirs(odkazy)

    def _url(self, url):
        # DirtyFix nefunkcniho downloadu: Neznam kod tak se toho zkusenejsi chopte
        # a prepiste to lepe :)
        if '&authorize=' in url:
            return url
        else:
            return self.base_url + "/" + url.lstrip('./')

    def resolve(self, item, captcha_cb=None, select_cb=None):
        data = item['url']
        if not data:
            raise ResolveException('Video is not available.')
        result = self.findstreams([STREAMUJ_URL + data])
        if len(result) == 1:
            return result[0]
        elif len(result) > 1 and select_cb:
            return select_cb(result)

    def get_subs(self):
        return self.parent.get_subs()
