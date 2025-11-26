# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/filters/fun_random_carousel_filter.py
from __future__ import absolute_import
from account_helpers.AccountSettings import BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1, FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2, FUN_RANDOM_CAROUSEL_FILTER_3, FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1
from gui.filters.battle_pass_carousel_filter import BattlePassCarouselFilter

class FunRandomCarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(FunRandomCarouselFilter, self).__init__()
        self._serverSections = (FUN_RANDOM_CAROUSEL_FILTER_1,
         FUN_RANDOM_CAROUSEL_FILTER_2,
         BATTLEPASS_CAROUSEL_FILTER_1,
         FUN_RANDOM_CAROUSEL_FILTER_3)
        self._clientSections = (FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
        self._criteriesGroups = ()
