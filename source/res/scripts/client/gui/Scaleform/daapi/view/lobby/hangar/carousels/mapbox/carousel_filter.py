# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/mapbox/carousel_filter.py
from account_helpers.AccountSettings import MAPBOX_CAROUSEL_FILTER_1, MAPBOX_CAROUSEL_FILTER_2, MAPBOX_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCarouselFilter

class MapboxCarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(MapboxCarouselFilter, self).__init__()
        self._serverSections = (MAPBOX_CAROUSEL_FILTER_1, MAPBOX_CAROUSEL_FILTER_2, BATTLEPASS_CAROUSEL_FILTER_1)
        self._clientSections = (MAPBOX_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
