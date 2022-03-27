# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/event_battle/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.event_battle.carousel_data_provider import EventBattleCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.event_battle.carousel_filter import EventBattleCarouselFilter

class EventBattleTankCarousel(TankCarousel):

    def __init__(self):
        super(EventBattleTankCarousel, self).__init__()
        self._carouselDPCls = EventBattleCarouselDataProvider
        self._carouselFilterCls = EventBattleCarouselFilter
