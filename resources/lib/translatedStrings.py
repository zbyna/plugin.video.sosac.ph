import xbmcaddon

__scriptid__ = 'plugin.video.sosac.ph'
__addon__ = xbmcaddon.Addon(id=__scriptid__)

CSFD_BASE = 'http://www.csfd.cz/'
ZEBRICKY_FILMY_NEJ = 'zebricky/nejlepsi-filmy/?show=complete'
ZEBRICKY_SPEC = 'zebricky/specificky-vyber/'
ZEBRICKY_FILMY_SPEC = (ZEBRICKY_SPEC + 
'?type=0&origin=&genre=&year_from=&year_to=&actor=&director=&ok=Zobrazit&_form_=charts')
ZEBRICKY_TVSHOW_NEJ = 'zebricky/nejlepsi-serialy/?show=complete'
ZEBRICKY_TVSHOW_SPEC = (ZEBRICKY_SPEC +
'?type=3&origin=&genre=&year_from=&year_to=&actor=&director=&ok=Zobrazit&_form_=charts')
ZEBRICKY_FILMY_SPEC_GENRE = 'type=0'
ZEBRICKY_TVSHOW_SPEC_GENRE = 'type=3'
OCENENI_OSCAR = 'oceneni/1-oscars/'
OCENENI_OSCAR_ROKY = '?years='
OCENENI_ZLATA_PALMA = 'oceneni/4-cannes-iff/'
OCENENI_ZLATA_PALMA_ROKY = '?years='
# strings used in sosac.py nad sutils.py
LIBRARY_TYPE_VIDEO = "video"
LIBRARY_TYPE_TVSHOW = "tvshow"
# playing from restored position
POKRACOVAT = __addon__.getLocalizedString(30208)
OD_ZACATKU = __addon__.getLocalizedString(30209)
OD_MINULE_POZICE = __addon__.getLocalizedString(30210)
# main menu items
MOVIES = __addon__.getLocalizedString(30300)
TV_SHOWS = __addon__.getLocalizedString(30301)
MOVIES_BY_GENRES = __addon__.getLocalizedString(30302)
MOVIES_MOST_POPULAR = __addon__.getLocalizedString(30303)
TV_SHOWS_MOST_POPULAR = __addon__.getLocalizedString(30304)
MOVIES_RECENTLY_ADDED = __addon__.getLocalizedString(30305)
TV_SHOWS_RECENTLY_ADDED = __addon__.getLocalizedString(30306)
SPRAVCE_ODBERU = __addon__.getLocalizedString(30310)
MOVIES_BY_YEAR = __addon__.getLocalizedString(30311)
CSFD_MAIN = __addon__.getLocalizedString(30323)
CSFD_LADDERS = __addon__.getLocalizedString(30317)
CSFD_AWARDS = __addon__.getLocalizedString(30318)
BEST_MOVIES = __addon__.getLocalizedString(30319)
BEST_MOVIES_BY_GENRE = __addon__.getLocalizedString(30320)
BEST_TV_SHOWS = __addon__.getLocalizedString(30321)
BEST_TV_SHOWS_BY_GENRE = __addon__.getLocalizedString(30322)
OSCARS = __addon__.getLocalizedString(30324)
GOLDEN_PALM = __addon__.getLocalizedString(30325)
# context menu items 
ADD_ALL_TO_LIBRARY = __addon__.getLocalizedString(30307)
ADD_TO_LIBRARY = __addon__.getLocalizedString(30308)
REMOVE_FROM_SUBSCRIPTION = __addon__.getLocalizedString(30309)
SUBSCRIBE = __addon__.getLocalizedString(30312)
REMOVE_ALL_FROM_SUBSCRIPTION = __addon__.getLocalizedString(30313)
SUBSCRIBE_ALL_TV_SHOWS = __addon__.getLocalizedString(30314)
