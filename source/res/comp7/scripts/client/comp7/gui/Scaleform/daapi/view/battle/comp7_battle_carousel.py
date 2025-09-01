# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/comp7_battle_carousel.py
from account_helpers.AccountSettings import COMP7_CAROUSEL_FILTER_1, COMP7_CAROUSEL_FILTER_2
from account_helpers.AccountSettings import COMP7_CAROUSEL_FILTER_CLIENT_1
from comp7_core.gui.Scaleform.daapi.view.battle.battle_carousel import PrebattleTankCarousel

class Comp7PrebattleTankCarousel(PrebattleTankCarousel):
    _FILTER_SERVER_SECTIONS = (COMP7_CAROUSEL_FILTER_1, COMP7_CAROUSEL_FILTER_2)
    _FILTER_CLIENT_SECTIONS = (COMP7_CAROUSEL_FILTER_CLIENT_1,)
