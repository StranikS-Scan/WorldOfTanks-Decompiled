# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/scaleform/daapi/view/lobby/tech_tree_trade_in_banner.py
from tech_tree_trade_in.gui.impl.lobby.entry_point_view import EntryPointView
from gui.Scaleform.daapi.view.meta.CarouselBannerInjectMeta import CarouselBannerInjectMeta
from shared_utils import nextTick

class TechTreeTradeInBannerComponent(CarouselBannerInjectMeta):
    __slots__ = ('__view', '__isExtended')

    def __init__(self):
        super(TechTreeTradeInBannerComponent, self).__init__()
        self.__view = None
        self.__isExtended = False
        return

    def setIsExtended(self, value):
        self.__isExtended = value
        if self.__view is not None:
            self.__view.setIsExtended(self.__isExtended)
        return

    def _onPopulate(self):
        self.__createInject()

    def _dispose(self):
        self.__view = None
        super(TechTreeTradeInBannerComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = EntryPointView(isExtended=self.__isExtended)
        return self.__view

    @nextTick
    def __createInject(self):
        self._createInjectView()
