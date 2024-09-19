# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_progression_controller.py
import logging
from Event import Event, EventManager
from event_common import BP_TANKMEN_ENTITLEMENT_TAG_PREFIX
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_helpers import getTankmanFirstNationGroup
from gui.entitlements.tankmen_entitlements_cache import TankmenEntitlementsCache
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWTProgressionController, ISpecialSoundCtrl
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class WTProgressionController(IWTProgressionController, EventsHandler):
    __tankmenCache = TankmenEntitlementsCache()
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __specialSounds = dependency.descriptor(ISpecialSoundCtrl)

    def __init__(self):
        self.__isInited = False
        self.__voicedTankmenGroupNames = set()
        self.__eventsManager = EventManager()
        self.onEntitlementCacheUpdated = Event(self.__eventsManager)

    def init(self):
        super(WTProgressionController, self).init()
        BattlePassAwardsManager.init()

    def onLobbyInited(self, event):
        self._subscribe()
        storageData = self.__settingsCore.serverSettings.getBPStorage()
        self.__settingsCore.serverSettings.updateBPStorageData(storageData)
        if not self.__isInited:
            self.__updateVoicedTankmenGroupNames()
            self.tankmenCacheUpdate()
        self.__isInited = True

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__isInited = False
        self.__stop()
        self.__tankmenCache.clear()

    def fini(self):
        self.__isInited = False
        self.__stop()
        self.__eventsManager.clear()
        self.__tankmenCache.clear()
        super(WTProgressionController, self).fini()

    def getTankmenEntitlements(self):
        return self.__tankmenCache.getBalance()

    def tankmenCacheUpdate(self, isWaiting=False):
        if isWaiting:
            self.__tankmenCache.updateWithDelay(self.__getTankmenTagForRequest(), self.__onResponse)
        else:
            self.__tankmenCache.update(self.__getTankmenTagForRequest(), self.__onResponse)

    def isVoicedTankman(self, tankmanGroupName):
        return tankmanGroupName in self.__voicedTankmenGroupNames

    def isOfferEnabled(self):
        return self.__lobbyContext.getServerSettings().isOffersEnabled()

    def getSpecialTankmen(self):
        return self.__lobbyContext.getServerSettings().eventBattlesConfig.specialTankmen

    def __onResponse(self, *_):
        self.onEntitlementCacheUpdated()

    def __updateVoicedTankmenGroupNames(self):
        self.__voicedTankmenGroupNames = set()
        for groupName in self.getSpecialTankmen().iterkeys():
            group = getTankmanFirstNationGroup(groupName)
            if group is not None and any((self.__specialSounds.checkTagForSpecialVoice(tag) for tag in group.tags)):
                self.__voicedTankmenGroupNames.add(groupName)

        return

    def __getTankmenTagForRequest(self):
        return '{}_{}'.format(BP_TANKMEN_ENTITLEMENT_TAG_PREFIX, 0)

    def __stop(self):
        self._unsubscribe()
