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
import xml.etree.ElementTree as ET

import urllib
import urllib2
import cookielib
import sys
import json

import util
from provider import ContentProvider, cached, ResolveException
import xbmc
import xbmcgui

sys.setrecursionlimit(10000)

MOVIES_BASE_URL = "http://movies.prehraj.me"
MOVIES_YEAR = "filmyxml.php"
YEAR_PARAM = "rok"
TV_SHOW_FLAG = "#tvshow#"
ISO_639_1_CZECH = "cs"

# JSONs
URL = "http://tv.sosac.to"
SUBSCRIPTION_MANAGER = "subscription_manager"
ADD_TO_LIBRARY = ""
REMOVE_FROM_SUBSCRIPTION = ""
ADD_ALL_TO_LIBRARY = ""
SUBSCRIBE = ""
J_MOVIES_A_TO_Z_TYPE = "/vystupy5981/souboryaz.json"
J_MOVIES_GENRE = "/vystupy5981/souboryzanry.json"
J_MOVIES_MOST_POPULAR = "/vystupy5981/moviesmostpopular.json"
J_MOVIES_RECENTLY_ADDED = "/vystupy5981/moviesrecentlyadded.json"
# hack missing json with a-z series
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


class SosacContentProvider(ContentProvider):
    ISO_639_1_CZECH = None
    par = None

    def __init__(self, username=None, password=None, filter=None, reverse_eps=False):
        ContentProvider.__init__(self, name='sosac.ph', base_url=MOVIES_BASE_URL, username=username,
                                 password=password, filter=filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        self.reverse_eps = reverse_eps

    def on_init(self):
        kodilang = self.lang or 'cs'
        if kodilang == ISO_639_1_CZECH or kodilang == 'sk':
            self.ISO_639_1_CZECH = ISO_639_1_CZECH
        else:
            self.ISO_639_1_CZECH = 'en'

    def capabilities(self):
        return ['resolve', 'categories', 'search']

    def categories(self):
        MOVIES = self.parent.getString(30300)
        TV_SHOWS = self.parent.getString(30301)
        MOVIES_BY_GENRES = self.parent.getString(30302)
        MOVIES_MOST_POPULAR = self.parent.getString(30303)
        TV_SHOWS_MOST_POPULAR = self.parent.getString(30304)
        MOVIES_RECENTLY_ADDED = self.parent.getString(30305)
        TV_SHOWS_RECENTLY_ADDED = self.parent.getString(30306)
        ADD_ALL_TO_LIBRARY = self.parent.getString(30307)
        SPRAVCE_ODBERU = self.parent.getString(30310)
        MOVIES_BY_YEAR = self.parent.getString(30311)
        REMOVE_ALL_FROM_SUBSCRIPTION = self.parent.getString(30313)
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
                (SPRAVCE_ODBERU, SUBSCRIPTION_MANAGER)]:
            item = self.dir_item(title=title, url=url)
            if title == MOVIES or title == TV_SHOWS or title == MOVIES_RECENTLY_ADDED:
                item['menu'] = {"[B][COLOR red]" + ADD_ALL_TO_LIBRARY + "[/COLOR][/B]": {
                    'action': 'add-all-to-library', 'title': title}}
            if title == SPRAVCE_ODBERU:
                item['menu'] = {"[B][COLOR yellow]" + REMOVE_ALL_FROM_SUBSCRIPTION + "[/COLOR][/B]": {
                    'action': 'remove-all-from-subscription', 'title': title}}
            result.append(item)
        return result

    def search(self, keyword):
        if len(keyword) < 3 or len(keyword) > 100:
            return [self.dir_item(title="Search query must be between 3 and 100 characters long!", url="fail")]
        return self.list_search(URL + J_SEARCH + urllib.quote_plus(keyword))

    def a_to_z(self, url):
        result = []
        for letter in ['0-9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'e', 'h', 'i', 'j', 'k', 'l', 'm',
                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
            item = self.dir_item(title=letter.upper())
            item['url'] = URL + url + letter + ".json"
            result.append(item)
        return result

    @staticmethod
    def remove_flag_from_url(url, flag):
        return url.replace(flag, "", count=1)

    @staticmethod
    def particular_letter(url):
        return "a-z/" in url

    def has_tv_show_flag(self, url):
        return TV_SHOW_FLAG in url

    def remove_flags(self, url):
        return url.replace(TV_SHOW_FLAG, "", 1)

    def list(self, url):
        global ADD_TO_LIBRARY
        ADD_TO_LIBRARY = self.parent.getString(30308)
        global REMOVE_FROM_SUBSCRIPTION
        REMOVE_FROM_SUBSCRIPTION = self.parent.getString(30309)
        global ADD_ALL_TO_LIBRARY
        ADD_ALL_TO_LIBRARY = self.parent.getString(30307)
        global SUBSCRIBE
        SUBSCRIBE = self.parent.getString(30312)
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
        return self.list_videos(url)

    def load_json_list(self, url):
        result = []
        data = util.request(url)
        json_list = json.loads(data)
        for key, value in json_list.iteritems():
            item = self.dir_item(title=self.upper_first_letter(key))
            item['url'] = value
            result.append(item)

        return sorted(result, key=lambda i: i['title'])

    def list_videos(self, url):
        result = []
        data = util.request(url)
        json_video_array = json.loads(data)
        for video in json_video_array:
            item = self.video_item()
            item['title'] = self.get_video_name(video)
            item['img'] = IMAGE_MOVIE + video['i']
            item['url'] = video['l'] if video['l'] else ""
            if RATING in video:
                item['rating'] = video[RATING]
            if LANG in video:
                item['lang'] = video[LANG]
            if QUALITY in video:
                item['quality'] = video[QUALITY]
            result.append(item)
        return result

    def list_series_letter(self, url):
        result = []
        data = util.request(url)
        json_list = json.loads(data)
        for serial in json_list:
            item = self.dir_item()
            item['title'] = self.get_localized_name(serial['n'])
            item['img'] = IMAGE_SERIES + serial['i']
            item['url'] = serial['l']
            result.append(item)
        return result

    def list_by_year(self, url):
        MOVIES_BY_YEAR = self.parent.getString(30311)
        if "?" + YEAR_PARAM in url:
            return self.list_xml_letter(url)
        else:
            result = []
            page = util.request(url)
            data = util.substr(page, '<select name=\"rok\">', '</select')
            for s in reversed(list(re.finditer('<option value=\"([^\"]+)\">([^<]+)</option>', data,
                                               re.IGNORECASE | re.DOTALL))):
                if s.group(2) == '0000':
                    continue
                urlPom = url + "?" + YEAR_PARAM + "=" + s.group(1)
                item = {'url': urlPom, 'title': s.group(2), 'type': 'dir'}
                item['menu'] = {"[B][COLOR red]" + ADD_ALL_TO_LIBRARY + "[/COLOR][/B]": {
                    'action': 'add-all-to-library', 'title': MOVIES_BY_YEAR, 'url': urlPom}}
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
        for episode in json_series:
            item = self.video_item()
            item['title'] = self.get_episode_recently_name(episode)
            item['img'] = IMAGE_EPISODE + episode['i']
            item['url'] = episode['l']
            result.append(item)
        return result

    def get_video_name(self, video):
        name = self.get_localized_name(video['n'])
        year = (" (" + video['y'] + ") ") if video['y'] else " "
        quality = ("- " + video[QUALITY].upper()) if video[QUALITY] else ""
        return name + year + quality

    def get_episode_recently_name(self, episode):
        serial = self.get_localized_name(episode['t']) + ' '
        series = episode['s'] + "x"
        number = episode['e'] + " - "
        name = self.get_localized_name(episode['n'])
        return serial + series + number + name

    def add_video_flag(self, items):
        flagged_items = []
        for item in items:
            flagged_item = self.video_item()
            flagged_item.update(item)
            flagged_items.append(flagged_item)
        return flagged_items

    def add_directory_flag(self, items):
        flagged_items = []
        for item in items:
            flagged_item = self.dir_item()
            flagged_item.update(item)
            flagged_items.append(flagged_item)
        return flagged_items

    def get_localized_name(self, names):
        return (names[self.ISO_639_1_CZECH]
                if self.ISO_639_1_CZECH in names else names[ISO_639_1_CZECH])

    @cached(ttl=24)
    def get_data_cached(self, url):
        return util.request(url)

    def library_movies_all_xml(self):
        page = util.request('http://tv.prehraj.me/filmyxml.php')
        pagedata = util.substr(page, '<select name=\"rok\">', '</select>')
        pageitems = re.finditer('<option value=\"(?P<url>[^\"]+)\">(?P<name>[^<]+)</option>',
                                pagedata, re.IGNORECASE | re.DOTALL)
        pagetotal = float(len(list(pageitems)))
        pageitems = re.finditer('<option value=\"(?P<url>[^\"]+)\">(?P<name>[^<]+)</option>',
                                pagedata, re.IGNORECASE | re.DOTALL)
        util.info("PocetRoku: %d" % pagetotal)
        pagenum = 0
        for m in pageitems:
            pagenum += 1
            if self.parent.dialog.iscanceled():
                return
            pageperc = float(pagenum / pagetotal) * 100
            util.info("Rokpercento: %d" % int(pageperc))
            data = util.request('http://tv.prehraj.me/filmyxml.php?rok=' +
                                m.group('url') + '&sirka=670&vyska=377&affid=0#')
            tree = ET.fromstring(data)
            total = float(len(list(tree.findall('film'))))
            util.info("TOTAL: %d" % total)
            num = 0
            for film in tree.findall('film'):
                num += 1
                perc = float(num / total) * 100
                util.info("percento: %d" % int(perc))
                if self.parent.dialog.iscanceled():
                    return
                item = self.video_item()
                try:
                    if ISO_639_1_CZECH in self.ISO_639_1_CZECH:
                        title = film.findtext('nazevcs').encode('utf-8')
                    else:
                        title = film.findtext('nazeven').encode('utf-8')
                    self.parent.dialog.update(int(perc), str(pagenum) + '/' + str(int(pagetotal)) +
                                              ' [' + m.group('url') + '] ->  ' + title)
                    item['title'] = '%s (%s)' % (title, film.findtext('rokvydani'))
                    item['name'] = item['title']
                    item['url'] = 'http://movies.prehraj.me/' + self.ISO_639_1_CZECH + \
                        'player/' + self.parent.make_name(title + '-' + film.findtext('rokvydani'))
                    item['menu'] = {"[B][COLOR red]" + ADD_TO_LIBRARY + "[/COLOR][/B]": {
                        'url': item['url'], 'action': 'add-to-library', 'name': item['title']}}
                    item['update'] = True
                    item['notify'] = False
                    self.parent.add_item(item)
                except Exception as e:
                    util.error("ERR TITLE: " + item['title'] + " | " + str(e))
                    pass
#        self.parent.dialog.close()

    def library_movie_recently_added_xml(self):
        data = util.request(
            'http://tv.prehraj.me/filmyxml2.php?limit=200&sirka=670&vyska=377&affid=0#')
        tree = ET.fromstring(data)
        total = float(len(list(tree.findall('film'))))
        util.info("TOTAL: %d" % total)
        num = 0
        for film in tree.findall('film'):
            num += 1
            perc = float(num / total) * 100
            util.info("percento: %d" % int(perc))
            if self.parent.dialog.iscanceled():
                return
            self.parent.dialog.update(int(perc), film.findtext('nazevcs') + ' (' +
                                      film.findtext('rokvydani') + ')\n' +
                                      film.findtext('nazeven') + ' (' +
                                      film.findtext('rokvydani') + ')\n\n\n')
            item = self.video_item()
            try:
                if ISO_639_1_CZECH in self.ISO_639_1_CZECH:
                    title = film.findtext('nazevcs').encode('utf-8')
                else:
                    title = film.findtext('nazeven').encode('utf-8')
                item['title'] = '%s (%s)' % (title, film.findtext('rokvydani'))
                item['name'] = item['title']
                item['url'] = 'http://movies.prehraj.me/' + self.ISO_639_1_CZECH + \
                    'player/' + self.parent.make_name(title + '-' + film.findtext('rokvydani'))
                item['menu'] = {"[B][COLOR red]" + ADD_TO_LIBRARY + "[/COLOR][/B]": {
                    'url': item['url'], 'action': 'add-to-library', 'name': item['title']}}
                item['update'] = True
                item['notify'] = False
                self.parent.add_item(item)
                # print("TITLE: ", item['title'])
            except Exception as e:
                util.error("ERR TITLE: " + item['title'] + " | " + str(e))
                pass
#        self.parent.dialog.close()

    def library_tvshows_all_xml(self):
        SUBSCRIBE_ALL_TV_SHOWS = self.parent.getString(30314)
        page = util.request('http://tv.prehraj.me/serialyxml.php')
        data = util.substr(page, '<select name=\"serialy\">', '</select>')
        items = re.finditer('<option value=\"(?P<url>[^\"]+)\">(?P<name>[^<]+)</option>', data,
                            re.IGNORECASE | re.DOTALL)
        total = float(len(list(items)))
        items = re.finditer('<option value=\"(?P<url>[^\"]+)\">(?P<name>[^<]+)</option>', data,
                            re.IGNORECASE | re.DOTALL)
        util.info("Pocet: %d" % total)
        dialog = xbmcgui.Dialog()
        question = dialog.yesno(SUBSCRIBE_ALL_TV_SHOWS, '')
        num = 0
        for m in items:
            num += 1
            if self.parent.dialog.iscanceled():
                return
            perc = float(num / total) * 100
            util.info("percento: %d" % int(perc))
            self.parent.dialog.update(int(perc), m.group('name'))
            item = {'url': 'http://tv.prehraj.me/cs/detail/' + m.group('url'),
                    'action': 'add-to-library', 'name': m.group('name'), 'update': True,
                    'notify': True}
            self.parent.add_item(item, question)
        util.info("done....")

    def subscription_manager_tvshows_all_xml(self):
        page = util.request('http://tv.prehraj.me/serialyxml.php')
        data = util.substr(page, '<select name=\"serialy\">', '</select>')
        items = re.finditer('<option value=\"(?P<url>[^\"]+)\">(?P<name>[^<]+)</option>', data,
                            re.IGNORECASE | re.DOTALL)
        total = float(len(list(items)))
        items = re.finditer('<option value=\"(?P<url>[^\"]+)\">(?P<name>[^<]+)</option>', data,
                            re.IGNORECASE | re.DOTALL)
        shows = []
        i = 0
        subs = self.get_subs()
        for m in items:
            flagged_item = self.dir_item()
            urlPom = 'http://tv.prehraj.me/cs/detail/' + m.group('url')
            namePom = m.group('name')
            flagged_item = {'url': urlPom,
                            'action': 'add-to-library', 'title': namePom, 'update': True,
                            'notify': True, 'type': 'dir', 'size': '0'}
            if flagged_item['url'] in subs:
                flagged_item['menu'] = {
                    "[B][COLOR red]" + REMOVE_FROM_SUBSCRIPTION + "[/COLOR][/B]": {
                        'url': urlPom,
                        'action': 'remove-subscription', 'name': namePom
                    }
                }
                flagged_item['title'] = '[B][COLOR yellow]*[/COLOR][/B] ' + flagged_item['title']
                flagged_item['url'] = TV_SHOW_FLAG + flagged_item['url']
                shows.insert(i, flagged_item)
                i += 1
            else:
                flagged_item['menu'] = {
                    "[B][COLOR red]" + ADD_TO_LIBRARY + "[/COLOR][/B]": {
                        'url': urlPom,
                        'action': 'add-to-library',
                        'name': namePom
                    },
                    "[B][COLOR yellow]" + SUBSCRIBE + "[/COLOR][/B]": {
                        'url': urlPom,
                        'action': 'add-subscription',
                        'name': namePom
                    }
                }
                flagged_item['url'] = TV_SHOW_FLAG + flagged_item['url']
                shows.append(flagged_item)
        return shows

    def list_xml_letter_to_library(self, url):
        result = []
        data = util.request(url)
        tree = ET.fromstring(data)
        total = float(len(tree.findall('film')))
        i = 0
        for film in tree.findall('film'):
            i += 1
            item = self.video_item()
            try:
                if ISO_639_1_CZECH in self.ISO_639_1_CZECH:
                    title = film.findtext('nazevcs').encode('utf-8')
                else:
                    title = film.findtext('nazeven').encode('utf-8')
                basetitle = '%s (%s)' % (title, film.findtext('rokvydani'))
                item['title'] = '%s' % (basetitle)
                item['name'] = item['title']
                item['url'] = self.base_url + '/player/' + self.parent.make_name(
                    film.findtext('nazeven').encode('utf-8') + '-' + film.findtext('rokvydani'))
                item['menu'] = {"[B][COLOR red]" + ADD_TO_LIBRARY + "[/COLOR][/B]": {
                    'url': item['url'], 'action': 'add-to-library', 'name': basetitle}}
                item['update'] = True
                item['notify'] = False
                procenta = (i / total) * 100
                self.parent.dialog.update(int(procenta), item['title'])
                self.parent.add_item(item)
            except Exception as e:
                util.error("ERR TITLE: " + item['title'] + " | " + str(e))
                pass

    def add_flag_to_url(self, item, flag):
        item['url'] = flag + item['url']
        return item

    def add_url_flag_to_items(self, items, flag):
        subs = self.get_subs()
        for item in items:
            if item['url'] in subs:
                item['title'] = '[B][COLOR yellow]*[/COLOR][/B] ' + item['title']
            self.add_flag_to_url(item, flag)
        return items

    def _url(self, url):
        # DirtyFix nefunkcniho downloadu: Neznam kod tak se toho zkusenejsi chopte
        # a prepiste to lepe :)
        if '&authorize=' in url:
            return url
        else:
            return self.base_url + "/" + url.lstrip('./')

    def list_tv_shows_by_letter(self, url):
        util.info("Getting shows by letter " + url)
        shows = self.list_by_letter(url)
        util.info("Resolved shows " + str(shows))
        shows = self.add_directory_flag(shows)
        return self.add_url_flag_to_items(shows, TV_SHOW_FLAG)

    def list_movies_by_letter(self, url):
        movies = self.list_by_letter(url)
        util.info("Resolved movies " + str(movies))
        return self.add_video_flag(movies)

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

    def list_search(self, url):
        return self.list_videos(url)

    def upper_first_letter(self, name):
        return name[:1].upper() + name[1:]
