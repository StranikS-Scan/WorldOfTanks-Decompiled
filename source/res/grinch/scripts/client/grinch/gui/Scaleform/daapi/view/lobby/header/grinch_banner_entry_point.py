# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/lobby/header/grinch_banner_entry_point.py
from grinch.gui.impl.lobby.banner_entry_point.grinch_banner_entry_point import GrinchBannerEntryPoint as GrinchBannerEntryPointView
from grinch.gui.Scaleform.daapi.view.meta.GrinchBannerEntryPointMeta import GrinchBannerEntryPointMeta

class GrinchBannerEntryPoint(GrinchBannerEntryPointMeta):

    def isSingle(self, value):
        if self.__view:
            self.__view.setIsSingle(value)

    def _makeInjectView(self):
        self.__view = GrinchBannerEntryPointView()
        return self.__view
