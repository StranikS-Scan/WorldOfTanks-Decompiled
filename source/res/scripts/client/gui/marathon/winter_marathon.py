# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/winter_marathon.py
from gui.impl import backport
from marathon_event_dp import MarathonEvent, MarathonEventIconsData, MARATHON_STATE

class WinterMarathon(MarathonEvent):

    @property
    def prefix(self):
        pass

    @property
    def tokenPrefix(self):
        pass

    @property
    def vehicleName(self):
        pass

    @property
    def hangarFlags(self):
        pass

    @property
    def marathonTooltipHeader(self):
        pass

    @property
    def minVehicleLevel(self):
        pass

    @property
    def icons(self):
        icons = super(WinterMarathon, self).icons._asdict()
        icons.update({'mapFlagHeaderIcon': {MARATHON_STATE.ENABLED_STATE: backport.image(self._getIconsResource('winter_icon')()),
                               MARATHON_STATE.DISABLED_STATE: backport.image(self._getIconsResource('winter_disable_icon')())}})
        return MarathonEventIconsData(**icons)
