# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/lunar_marathon.py
from gui.impl.gen import R
from gui.marathon.marathon_event import MarathonEvent
from gui.marathon.marathon_event_container import MarathonEventContainer
from gui.marathon.marathon_event_controller import marathonCreator
from gui.Scaleform.locale.QUESTS import QUESTS

class LunarMarathonEvent(MarathonEvent):

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.moon_marathon()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_MOON_MARATHON

    @property
    def entryTooltip(self):
        return self._data.tooltips

    @property
    def isNeedHandlingEscape(self):
        return True

    def createMarathonWebHandlers(self):
        from gui.marathon.web_handlers import createDefaultMarathonWebHandlers
        return createDefaultMarathonWebHandlers()


@marathonCreator(LunarMarathonEvent)
class LunarMarathon(MarathonEventContainer):

    def _override(self):
        self.prefix = 'moon_marathon'
        self.tokenPrefix = 'moon_marathon:WZ1222_'
        self.hangarFlagName = 'flag_marathon'
        self.questsInChain = 10
        self.minVehicleLevel = 6
        self.questsPerStep = 3
