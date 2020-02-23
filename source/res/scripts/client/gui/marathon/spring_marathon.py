# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/spring_marathon.py
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.marathon.marathon_event_dp import MarathonEvent

class SpringMarathon(MarathonEvent):

    @property
    def tokenPrefix(self):
        pass

    @property
    def vehiclePrefix(self):
        pass

    @property
    def vehicleID(self):
        pass

    @property
    def awardTokens(self):
        pass

    @property
    def questsInChain(self):
        pass

    def getHangarFlag(self, state=None):
        return backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_france())

    def doesShowRewardVideo(self):
        return False

    def doesShowRewardScreen(self):
        return False

    def doesShowMissionsTab(self):
        return self.isEnabled()

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.springMarathon()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_SPRINGMARATHON

    @property
    def tabTooltipDisabled(self):
        return QUESTS.MISSIONS_TAB_SPRINGMARATHON
