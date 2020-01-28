# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/bob_event.py
import logging
import Event
from gui import GUI_SETTINGS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.game_control.bob_controller import BobController
from gui.impl import backport
from gui.impl.gen import R
from gui.marathon.marathon_event_dp import MarathonEvent
from helpers import dependency
from skeletons.gui.game_control import IBobController
_logger = logging.getLogger(__name__)
_BOB_EVENT_SECTION = 'bobEvent'

class BobEventAddUrl(object):
    EMPTY_URL = ''
    SKILLS = 'skillsUrl'


class BobEvent(MarathonEvent):
    BOB_EVENT_PREFIX = 'bob_event:'
    bobController = dependency.descriptor(IBobController)

    def __init__(self):
        super(BobEvent, self).__init__()
        self.onDataChanged = Event.Event()
        self.__urlDict = GUI_SETTINGS.lookup(_BOB_EVENT_SECTION)
        self.__additionalUrl = BobEventAddUrl.EMPTY_URL

    @property
    def prefix(self):
        return self.BOB_EVENT_PREFIX

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.battleOfBloggers.naasia() if BobController.isNaAsiaRealm() else R.strings.quests.missions.tab.label.battleOfBloggers()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_BATTLEOFBLOGGERS_NAASIA if BobController.isNaAsiaRealm() else QUESTS.MISSIONS_TAB_BATTLEOFBLOGGERS

    @property
    def tabTooltipDisabled(self):
        return QUESTS.MISSIONS_TAB_BATTLEOFBLOGGERS_NAASIA if self.bobController.isNaAsiaRealm() else QUESTS.MISSIONS_TAB_BATTLEOFBLOGGERS

    def init(self):
        super(BobEvent, self).init()
        self.bobController.onUpdated += self.onDataChanged

    def fini(self):
        self.bobController.onUpdated -= self.onDataChanged
        super(BobEvent, self).fini()

    def isEnabled(self):
        return self.bobController.needShowEventTab() and not self._bootcamp.isInBootcamp()

    def isAvailable(self):
        return self.isEnabled()

    def createMarathonWebHandlers(self):
        from gui.marathon.web_handlers import createBobWebHandlers
        return createBobWebHandlers()

    def getMarathonFlagState(self, vehicle):
        flagState = super(BobEvent, self).getMarathonFlagState(vehicle)
        flagState.update({'visible': False})
        return flagState

    def getHangarFlag(self, state=None):
        return backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_green())

    def doesShowRewardVideo(self):
        return False

    def doesShowRewardScreen(self):
        return False

    def doesShowMissionsTab(self):
        return self.isEnabled()

    def setAdditionalUrl(self, additionalUrl):
        self.__additionalUrl = additionalUrl

    def _getUrl(self):
        if self.__additionalUrl in self.__urlDict:
            relativeUrl = self.__urlDict.get(self.__additionalUrl, BobEventAddUrl.EMPTY_URL)
        else:
            relativeUrl = self.__additionalUrl
        baseUrl = self._lobbyContext.getServerSettings().bobConfig.url + relativeUrl
        if not baseUrl:
            _logger.warning('Battle of bloggers url from bob_config.xml is absent or invalid: %s', baseUrl)
        self.__additionalUrl = BobEventAddUrl.EMPTY_URL
        return baseUrl
