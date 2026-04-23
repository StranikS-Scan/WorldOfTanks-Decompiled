# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/entry_points/paragons_entry_point.py
from gui.Scaleform.daapi.view.meta.ResizableEntryPointMeta import ResizableEntryPointMeta
from gui.impl.lobby.paragons.banner.banner_view import ParagonsBannerView

class ParagonsBannerEntryPoint(ResizableEntryPointMeta):

    def isSingle(self, value):
        pass

    def _makeInjectView(self):
        self.__view = ParagonsBannerView()
        return self.__view
