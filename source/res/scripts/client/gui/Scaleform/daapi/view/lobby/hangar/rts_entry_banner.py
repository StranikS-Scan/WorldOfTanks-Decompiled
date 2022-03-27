# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/rts_entry_banner.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.RTSEntryBannerMeta import RTSEntryBannerMeta
from gui.impl.lobby.rts.entry_banner_view import EntryBannerView

class RTSEntryBanner(RTSEntryBannerMeta):

    def _makeInjectView(self):
        self.__view = EntryBannerView(ViewFlags.COMPONENT)
        return self.__view
