# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/dog_tags.py
import logging
from functools import partial
import typing
import BigWorld
import AccountCommands
from Event import Event
from account_helpers.AccountSyncData import AccountSyncData
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.dog_tags_storage import UnlockedComponentsStorage, PlayerDogTagStorage, ProgressStorage, ExtraDataStorage
from dog_tags_common.player_dog_tag import DisplayableDogTag, PlayerDogTag
from dog_tags_common.settings_constants import Settings, DT_PDATA_KEY
from gui.server_events import settings as userSettings
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from dog_tags_common import settings_constants
if typing.TYPE_CHECKING:
    from typing import Callable, Union
    from Account import PlayerAccount
    from dog_tags_common.dog_tags_storage import ProgressRecord
    from gui.clans.clan_account_profile import ClanAccountProfile
    from dog_tags_common.dog_tags_storage import SkillDataRecord
_logger = logging.getLogger(__name__)

class DogTags(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.onDogTagDataChanged = Event()
        self.__ignore = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        dataResetKey = (DT_PDATA_KEY, '_r')
        if dataResetKey in diff:
            itemDiff = diff[dataResetKey]
            synchronizeDicts(itemDiff, self.__cache)
            self.__handleResetNotifications(itemDiff)
            self.onDogTagDataChanged(itemDiff)
        if DT_PDATA_KEY in diff:
            itemDiff = diff[DT_PDATA_KEY]
            synchronizeDicts(itemDiff, self.__cache)
            self.__handleSynchNotifications(itemDiff)
            self.onDogTagDataChanged(itemDiff)

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def getDisplayableDT(self, clanProfile=None):
        return self._makeDisplayableDT(clanProfile, PlayerDogTagStorage(self.__cache).get())

    def getDisplayableDTForComponents(self, compIds, clanProfile=None):
        playerDT = PlayerDogTagStorage(self.__cache).buildPlayerDogTag(compIds)
        return self._makeDisplayableDT(clanProfile, playerDT)

    def getUnlockedComps(self):
        allComps = set(componentConfigAdapter.getAllComponents())
        unlockedComps = set(UnlockedComponentsStorage(self.__cache).getAll())
        return unlockedComps.intersection(allComps)

    def getComponentProgress(self, compId):
        return ProgressStorage(self.__cache).get(compId)

    def getSkillData(self, compId):
        return ExtraDataStorage(self.__cache).getSkillData(compId) or []

    def getUnseenComps(self):
        allUnlockedComps = self.getUnlockedComps()
        seenComps = userSettings.getDogTagsSettings().seenComps
        return allUnlockedComps - seenComps

    def updatePlayerDT(self, backgroundId, engravingId):
        self.__account._doCmdIntArr(AccountCommands.CMD_UPDATE_PLAYER_DOG_TAG, [backgroundId, engravingId], self.__onUpdatePlayerDTCmdResponseReceived)

    def unlockComponentsDev(self, componentIds):
        self.__account._doCmdIntArr(AccountCommands.CMD_UNLOCK_DOG_TAG_COMPONENTS_DEV, componentIds, None)
        return

    def lockComponentsDev(self, componentIds):
        self.__account._doCmdIntArr(AccountCommands.CMD_LOCK_DOG_TAG_COMPONENTS_DEV, componentIds, None)
        return

    def unlockAllComponentsDev(self):
        self.__account._doCmdInt(AccountCommands.CMD_UNLOCK_ALL_DOG_TAG_COMPONENTS_DEV, 0, None)
        return

    def setProgressDev(self, compId, value):
        self.__account._doCmdInt2(AccountCommands.CMD_SET_DOG_TAG_COMPONENT_PROGRESS_DEV, compId, value, None)
        return

    def updateSettings(self, showVictimsDogTag, showDogTagToKiller):
        self.__account._doCmdIntStr(AccountCommands.CMD_UPDATE_SETTING, showVictimsDogTag, Settings.SHOW_VICTIMS_DT.value, None)
        self.__account._doCmdIntStr(AccountCommands.CMD_UPDATE_SETTING, showDogTagToKiller, Settings.SHOW_DT_TO_KILLER.value, None)
        return

    def updateSetting(self, setting, value):
        if isinstance(setting, settings_constants.Settings):
            setting = setting.value
        self.__account._doCmdIntStr(AccountCommands.CMD_UPDATE_SETTING, value, setting, None)
        return

    def isSynchronized(self):
        return bool(self.__cache)

    @staticmethod
    def _makeDisplayableDT(clanProfile, playerDT):
        clanTag = clanProfile.getClanAbbrev() if clanProfile and clanProfile.isInClan() else ''
        return DisplayableDogTag(playerDT, BigWorld.player().name, clanTag)

    def __onGetCacheResponse(self, callback, resultID):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        elif resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def __onUpdatePlayerDTCmdResponseReceived(self, resultID, requestID, errorStr, errorMsg=None):
        if not AccountCommands.isCodeValid(requestID):
            _logger.error((errorStr, errorMsg))

    def __handleSynchNotifications(self, dogTagsDiff):
        if PlayerDogTagStorage.key in dogTagsDiff:
            _logger.info('UPDATE Player DT: %r', self.__cache[PlayerDogTagStorage.key])
        if UnlockedComponentsStorage.key in dogTagsDiff:
            _logger.info('UPDATE unlocked components: %r', self.__cache[UnlockedComponentsStorage.key])

    def __handleResetNotifications(self, resetData):
        _logger.info('RESET Player DT: %s', resetData)
