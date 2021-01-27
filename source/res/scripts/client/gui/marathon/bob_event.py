# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/bob_event.py
import logging
from gui import GUI_SETTINGS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.impl.gen import R
from gui.marathon.marathon_constants import ZERO_TIME
from gui.marathon.marathon_event import MarathonEvent
from gui.marathon.marathon_event_container import MarathonEventContainer
from gui.marathon.marathon_event_controller import marathonCreator
from gui.marathon.marathon_resource_manager import MarathonResourceManager
from helpers import dependency
from skeletons.gui.game_control import IBobController
_logger = logging.getLogger(__name__)
_BOB_EVENT_SECTION = 'bobEvent'

class BobEventAddUrl(object):
    EMPTY_URL = ''
    SKILLS = 'skillsUrl'


class BobEvent(MarathonEvent):
    BOB_EVENT_PREFIX = 'bob_event'
    bobController = dependency.descriptor(IBobController)

    def __init__(self, resourceGeneratorClass, dataContainerClass):
        super(BobEvent, self).__init__(resourceGeneratorClass, dataContainerClass)
        self.__urlDict = GUI_SETTINGS.lookup(_BOB_EVENT_SECTION)
        self.__additionalUrl = BobEventAddUrl.EMPTY_URL

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.bob()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_BOB

    @property
    def isNeedHandlingEscape(self):
        return True

    def isEnabled(self):
        timeTillStartRegistration, _ = self.bobController.getTimeTillRegistrationStartOrEnd()
        return self.bobController.isEnabled() and timeTillStartRegistration <= ZERO_TIME and not self._bootcamp.isInBootcamp()

    def isAvailable(self):
        return self.isEnabled()

    def createMarathonWebHandlers(self):
        from gui.marathon.web_handlers import createBobWebHandlers
        return createBobWebHandlers()

    def getMarathonFlagState(self, vehicle):
        return {'visible': False}

    def setAdditionalUrl(self, additionalUrl):
        self.__additionalUrl = additionalUrl

    def _getUrl(self, urlType=None):
        if self.__additionalUrl in self.__urlDict:
            relativeUrl = self.__urlDict.get(self.__additionalUrl, BobEventAddUrl.EMPTY_URL)
        else:
            relativeUrl = self.__additionalUrl
        baseUrl = self._lobbyContext.getServerSettings().bobConfig.url + relativeUrl
        if not baseUrl:
            _logger.warning('Battle of bloggers url from bob_config.xml is absent or invalid: %s', baseUrl)
        self.__additionalUrl = BobEventAddUrl.EMPTY_URL
        return baseUrl


class BobResourceManager(MarathonResourceManager):

    def _initialize(self):
        pass


@marathonCreator(BobEvent, BobResourceManager)
class BobEventContainer(MarathonEventContainer):

    def _override(self):
        self.prefix = BobEvent.BOB_EVENT_PREFIX
        self.hangarFlagName = 'flag_green'
        self.doesShowRewardScreen = False
        self.doesShowRewardVideo = False
        self.doesShowInPostBattle = False
