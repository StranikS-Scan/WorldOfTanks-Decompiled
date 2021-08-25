# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/bts_marathon.py
from gui.impl.gen import R
from gui.marathon.marathon_event import MarathonEvent
from gui.marathon.marathon_event_container import MarathonEventContainer
from gui.marathon.marathon_event_controller import marathonCreator
from gui.Scaleform.locale.QUESTS import QUESTS

class BtsMarathonEvent(MarathonEvent):

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.sabaton_marathon()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_SABATON_MARATHON

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
    def packageStyleTemplate(self):
        return self._data.packageStyleTemplate

    @property
    def postPostfix(self):
        return self._data.postPostfix

    @property
    def stageDoneTemplate(self):
        return self._data.tokenPrefix + self._data.stageDonePostfix

    @property
    def isNeedHandlingEscape(self):
        return True

    def createMarathonWebHandlers(self):
        from gui.marathon.web_handlers import createDefaultMarathonWebHandlers
        return createDefaultMarathonWebHandlers()


@marathonCreator(BtsMarathonEvent)
class BtsMarathon(MarathonEventContainer):

    def _override(self):
        self.prefix = 'sabaton_marathon'
        self.tokenPrefix = 'sabaton_marathon:strvk_'
        self.styleTokenPostfix = 'post_complete'
        self.packagePrefix = 'strvk_'
        self.packageTemplate = 'strvk_vehicle_{}0d{}'
        self.packageStyleTemplate = 'strvk_3d_style_{}{}'
        self.hangarFlagName = 'flag_bts_marathon'
        self.grindPostfix = '_grind'
        self.proPostfix = '_pro'
        self.postPostfix = 'post_'
        self.finishedPostfix = '_v2'
        self.stageDonePostfix = '3d_style_q%STAGE%_done'
        self.questsInChain = 10
        self.minVehicleLevel = 6
        self.questsPerStep = 3
        self.vehicleName = 'sweden:S31_Strv_K'
