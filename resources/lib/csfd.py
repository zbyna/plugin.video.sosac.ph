# -*- coding: UTF-8 -*-
from translatedStrings import *

csfd = {'level_0' :
            [
                {
                    'name':CSFD_LADDERS,
                    'url': CSFD_BASE + 'zebricky/level_1',
                    'type':'DIR',
                    'level_1':[
                                {
                                    'name':BEST_MOVIES,
                                    'url': CSFD_BASE +ZEBRICKY_FILMY_NEJ,
                                    'type':'DIR'},
                                {
                                    'name': BEST_MOVIES_BY_GENRE,
                                    'url':CSFD_BASE + ZEBRICKY_FILMY_SPEC,
                                    'type':'DIR'
                                },
                                {
                                    'name': BEST_TV_SHOWS,
                                    'url': CSFD_BASE +ZEBRICKY_TVSHOW_NEJ,
                                    'type':'DIR'
                                },
                                {
                                    'name': BEST_TV_SHOWS_BY_GENRE,
                                    'url': CSFD_BASE + ZEBRICKY_TVSHOW_SPEC,
                                    'type':'DIR'
                                }
                            ]
                },
                {
                  'name': CSFD_AWARDS,
                  'url': CSFD_BASE +'oceneni/level_1',
                  'type':'DIR',
                  'level_1':[
                                {
                                    'name':OSCARS,
                                    'url': CSFD_BASE + OCENENI_OSCAR,
                                    'type':'DIR'},
                                {
                                    'name': GOLDEN_PALM,
                                    'url':CSFD_BASE + OCENENI_ZLATA_PALMA,
                                    'type':'DIR'
                                },
                                
                            ]
                }
            ]
        }