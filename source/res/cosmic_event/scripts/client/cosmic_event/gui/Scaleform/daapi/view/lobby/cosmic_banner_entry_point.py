# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/Scaleform/daapi/view/lobby/cosmic_banner_entry_point.py
from cosmic_event.gui.impl.lobby.banner_entry_point.cosmic_banner_entry_point import CosmicBannerEntryPointView
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.CosmicBannerEntryPointMeta import CosmicBannerEntryPointMeta

class CosmicBannerEntryPoint(CosmicBannerEntryPointMeta):

    def _makeInjectView(self):
        return CosmicBannerEntryPointView(ViewFlags.VIEW)
