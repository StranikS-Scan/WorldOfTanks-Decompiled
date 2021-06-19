# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/may_marathon.py
from gui.impl.gen import R
from gui.marathon.marathon_event import MarathonEvent
from gui.marathon.marathon_event_container import MarathonEventContainer
from gui.marathon.marathon_event_controller import marathonCreator
from gui.Scaleform.locale.QUESTS import QUESTS

class MayMarathonEvent(MarathonEvent):

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.may21_marathon()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_MAY21_MARATHON

    @property
    def entryTooltip(self):
        return self._data.tooltips

    @property
    def tokenPrefix(self):
        return self._data.tokenPrefix

    @property
    def grindPostfix(self):
        return self._data.grindPostfix

    @property
    def proPostfix(self):
        return self._data.proPostfix

    @property
    def finishedPostfix(self):
        return self._data.finishedPostfix

    @property
    def packagePrefix(self):
        return self._data.packagePrefix

    @property
    def packageTemplate(self):
        return self._data.packageTemplate

    @property
    def isNeedHandlingEscape(self):
        return True

    def createMarathonWebHandlers(self):
        from gui.marathon.web_handlers import createDefaultMarathonWebHandlers
        return createDefaultMarathonWebHandlers()


@marathonCreator(MayMarathonEvent)
class MayMarathon(MarathonEventContainer):

    def _override(self):
        self.prefix = 'may21_marathon'
        self.tokenPrefix = 'may21_marathon:KPZ07RH_'
        self.packagePrefix = 'KPZ07RH_'
        self.packageTemplate = 'kpz07rh_vehicle_{}0d{}'
        self.hangarFlagName = 'flag_may_marathon'
        self.grindPostfix = '_GRIND'
        self.proPostfix = '_PRO'
        self.finishedPostfix = '_v2'
        self.questsInChain = 10
        self.minVehicleLevel = 6
        self.questsPerStep = 3
