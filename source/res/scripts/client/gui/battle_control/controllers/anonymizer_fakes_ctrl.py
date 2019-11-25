# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/anonymizer_fakes_ctrl.py
import typing
import logging
import BigWorld
from avatar_helpers import getAvatarSessionID
from constants import BattleUserActions
from gui.anonymizer.battle_cooldown_manager import BattleCooldownManager
from gui.battle_control.battle_cache.cache_records import RelationsCacheRecord
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IAnonymizerFakesController
from messenger.storage import storage_getter
from messenger.proto import proto_getter
from messenger.proto.entities import BattleUserEntity, CurrentBattleUserEntity
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_errors import ChatCoolDownError
from messenger.m_constants import USER_TAG, PROTO_TYPE, UserEntityScope, USER_ACTION_ID, CLIENT_ACTION_ID
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.arena_dp import ArenaDataProvider
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
_logger = logging.getLogger(__name__)
_ACTION_BY_TAG = {(USER_TAG.FRIEND, True): USER_ACTION_ID.FRIEND_ADDED,
 (USER_TAG.FRIEND, False): USER_ACTION_ID.FRIEND_REMOVED,
 (USER_TAG.IGNORED, True): USER_ACTION_ID.IGNORED_ADDED,
 (USER_TAG.IGNORED, False): USER_ACTION_ID.IGNORED_REMOVED,
 (USER_TAG.MUTED, True): USER_ACTION_ID.MUTE_SET}
_CREATION_UPDATED_TAGS = (USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.MUTED)

class _RelationData(object):
    __slots__ = ('vehicleID', 'sessionID', 'databaseID', 'name')

    def __init__(self, vInfo):
        self.vehicleID = vInfo.vehicleID
        self.sessionID = vInfo.player.avatarSessionID
        self.databaseID = vInfo.player.accountDBID
        self.name = vInfo.player.getPlayerLabel()

    def isValid(self, avatarSessionID):
        return avatarSessionID == self.sessionID


class AnonymizerFakesController(IAnonymizerFakesController):
    __slots__ = ('__fakeIDs', '__relationsCache', '__arenaDP', '__avatarSessionID', '__postProcs', '__cooldown', '__mergedDBIDs')

    def __init__(self, setup):
        super(AnonymizerFakesController, self).__init__()
        self.__arenaDP = setup.arenaDP
        self.__relationsCache = RelationsCacheRecord.get()
        self.__cooldown = BattleCooldownManager()
        self.__fakeIDs = set()
        self.__mergedDBIDs = set()
        self.__avatarSessionID = ''
        self.__postProcs = {USER_ACTION_ID.FRIEND_ADDED: self.__addBattleFriend,
         USER_ACTION_ID.IGNORED_ADDED: self.__addBattleIgnored,
         USER_ACTION_ID.IGNORED_REMOVED: self.__removeBattleIgnored}

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def getControllerID(self):
        return BATTLE_CTRL_ID.ANONYMIZER_FAKES

    def stopControl(self):
        self.__arenaDP = None
        self.__postProcs = None
        self.__clear()
        return

    def invalidateVehiclesInfo(self, arenaDP):
        self.__clear()
        self.__avatarSessionID = getAvatarSessionID()
        currentInfo = arenaDP.getVehicleInfo(arenaDP.getVehIDBySessionID(self.__avatarSessionID))
        self.usersStorage.addUser(CurrentBattleUserEntity(self.__avatarSessionID, currentInfo.player.getPlayerLabel()))
        self.__fakeIDs.add(self.__avatarSessionID)
        for vInfo in self.__arenaDP.getVehiclesInfoIterator():
            self.__addBattleUser(_RelationData(vInfo))

        g_messengerEvents.users.onUsersListReceived({USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.IGNORED_TMP})

    def addVehicleInfo(self, vo, arenaDP):
        if self.__addBattleUser(_RelationData(vo)) is not None:
            g_messengerEvents.users.onUsersListReceived({USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.IGNORED_TMP})
        return

    def updateVehiclesInfo(self, updated, arenaDP):
        mergeChanges = False
        for _, vInfo in updated:
            mergeChanges = self.__mergeRelations(_RelationData(vInfo)) or mergeChanges

        if mergeChanges:
            g_messengerEvents.users.onUsersListReceived({USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.IGNORED_TMP})

    def addBattleFriend(self, avatarSessionID):
        if self.__isCooldown(CLIENT_ACTION_ID.ADD_FRIEND):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is not None and user.isFriend():
                _logger.error('%s is already friend', avatarSessionID)
                return
            self.__cooldown.process(CLIENT_ACTION_ID.ADD_FRIEND)
            self.__modifyRelations(avatarSessionID, BattleUserActions.ADD_FRIEND)
            return

    def removeBattleFriend(self, avatarSessionID):
        if self.__isCooldown(CLIENT_ACTION_ID.REMOVE_FRIEND):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is not None and not user.isFriend():
                _logger.error('%s is not a friend', avatarSessionID)
                return
            self.__cooldown.process(CLIENT_ACTION_ID.REMOVE_FRIEND)
            self.__modifyRelations(avatarSessionID, BattleUserActions.REMOVE_FRIEND)
            return

    def addBattleIgnored(self, avatarSessionID):
        if self.__isCooldown(CLIENT_ACTION_ID.ADD_IGNORED):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is not None and user.isIgnored() and not user.isTemporaryIgnored():
                _logger.error('%s is already permanent ignored', avatarSessionID)
                return
            self.__cooldown.process(CLIENT_ACTION_ID.ADD_IGNORED)
            self.__modifyRelations(avatarSessionID, BattleUserActions.ADD_IGNORED)
            return

    def removeBattleIgnored(self, avatarSessionID):
        if self.__isCooldown(CLIENT_ACTION_ID.REMOVE_IGNORED):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is not None and (not user.isIgnored() or user.isTemporaryIgnored()):
                _logger.error('%s is not permanent ignored', avatarSessionID)
                return
            self.__cooldown.process(CLIENT_ACTION_ID.REMOVE_IGNORED)
            self.__modifyRelations(avatarSessionID, BattleUserActions.REMOVE_IGNORED)
            return

    def mute(self, avatarSessionID, name):
        if self.__isCooldown(CLIENT_ACTION_ID.SET_MUTE):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is None:
                user = BattleUserEntity(avatarSessionID, name)
                self.usersStorage.addUser(user)
                self.__fakeIDs.add(avatarSessionID)
            if not user.isMuted():
                accDBID = self.__getAccDBID(avatarSessionID)
                user.addTags((USER_TAG.MUTED,))
                if accDBID > 0:
                    self.proto.contacts.setMuted(accDBID, name)
                else:
                    _logger.debug('we do not know accDBID about %s. real mute call skipped', avatarSessionID)
                self.__cooldown.process(CLIENT_ACTION_ID.SET_MUTE)
                g_messengerEvents.users.onBattleUserActionReceived(USER_ACTION_ID.MUTE_SET, user)
            else:
                _logger.error('%s is already muted', avatarSessionID)
            return

    def unmute(self, avatarSessionID):
        if self.__isCooldown(CLIENT_ACTION_ID.UNSET_MUTE):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is not None:
                if not user.isMuted():
                    _logger.error('%s is not muted', avatarSessionID)
                    return
                accDBID = self.__getAccDBID(avatarSessionID)
                user.removeTags((USER_TAG.MUTED,))
                if accDBID > 0:
                    self.proto.contacts.unsetMuted(accDBID)
                else:
                    _logger.debug('we do not know accDBID about %s. real unmute call skipped', avatarSessionID)
                self.__cooldown.process(CLIENT_ACTION_ID.UNSET_MUTE)
                g_messengerEvents.users.onBattleUserActionReceived(USER_ACTION_ID.MUTE_UNSET, user)
            else:
                _logger.error('there is no muted entity for %s', avatarSessionID)
            return

    def addTmpIgnored(self, avatarSessionID, name):
        if self.__isCooldown(CLIENT_ACTION_ID.ADD_IGNORED):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is None or not user.isMuted():
                self.mute(avatarSessionID, name)
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is not None:
                if user.isTemporaryIgnored():
                    _logger.error('%s is already temporary ignored', avatarSessionID)
                    return
                vehID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
                if not vehID:
                    _logger.error('can not get vehicleID for %s', avatarSessionID)
                    return
                user.addTags((USER_TAG.IGNORED_TMP,))
                isCacheChanged = self.__relationsCache.addTmpIgnored(vehID)
                if isCacheChanged:
                    self.__relationsCache.save()
                else:
                    _logger.error('%s is already in battle cache as tmp ignored', avatarSessionID)
                self.__cooldown.process(CLIENT_ACTION_ID.ADD_IGNORED)
                g_messengerEvents.users.onBattleUserActionReceived(USER_ACTION_ID.TMP_IGNORED_ADDED, user)
            else:
                _logger.error('addTmpIgnored: mute does not create entity for %s', avatarSessionID)
            return

    def removeTmpIgnored(self, avatarSessionID):
        if self.__isCooldown(CLIENT_ACTION_ID.REMOVE_IGNORED):
            return
        else:
            user = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
            if user is not None and user.isMuted():
                self.unmute(avatarSessionID)
            if user is not None:
                if not user.isTemporaryIgnored():
                    _logger.error('%s is not temporary ignored', avatarSessionID)
                    return
                vehID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
                if not vehID:
                    _logger.error('can not get vehicleID for %s', avatarSessionID)
                    return
                user.removeTags((USER_TAG.IGNORED_TMP,))
                isCacheChanged = self.__relationsCache.removeTmpIgnored(vehID)
                if isCacheChanged:
                    self.__relationsCache.save()
                else:
                    _logger.error('%s is not in battle cache as tmp ignored', avatarSessionID)
                self.__cooldown.process(CLIENT_ACTION_ID.REMOVE_IGNORED)
                g_messengerEvents.users.onBattleUserActionReceived(USER_ACTION_ID.TMP_IGNORED_REMOVED, user)
            else:
                _logger.error('there is no temporary ignored entity for %s', avatarSessionID)
            return

    def __addBattleFriend(self, user):
        if user.isTemporaryIgnored():
            self.removeTmpIgnored(user.getID())

    def __addBattleIgnored(self, user):
        if not user.isMuted():
            self.mute(user.getID(), user.getName())

    def __removeBattleIgnored(self, user):
        if user is not None and user.isMuted():
            self.unmute(user.getID())
        return

    def __addBattleUser(self, vehicleData):
        avatarSessionID = vehicleData.sessionID
        if avatarSessionID and avatarSessionID != self.__avatarSessionID:
            user = self.__buildBattleUser(vehicleData)
            if user is not None:
                self.usersStorage.addUser(user)
                self.__fakeIDs.add(avatarSessionID)
                return user
        return

    def __buildBattleUser(self, vehicleData):
        self.__mergeRelations(vehicleData)
        tags = set()
        if self.__relationsCache.isFriend(vehicleData.vehicleID):
            tags.add(USER_TAG.FRIEND)
        if self.__relationsCache.isIgnored(vehicleData.vehicleID):
            tags.update((USER_TAG.IGNORED, USER_TAG.MUTED))
        elif self.__relationsCache.isTmpIgnored(vehicleData.vehicleID):
            tags.update((USER_TAG.IGNORED_TMP, USER_TAG.MUTED))
        if vehicleData.databaseID > 0:
            realUser = self.usersStorage.getUser(vehicleData.databaseID)
            if realUser and realUser.isMuted():
                tags.update((USER_TAG.MUTED,))
        return BattleUserEntity(vehicleData.sessionID, vehicleData.name, tags) if tags else None

    def __clear(self):
        for fakeSessionID in self.__fakeIDs:
            self.usersStorage.removeUser(fakeSessionID)

        self.__fakeIDs.clear()
        self.__mergedDBIDs.clear()
        self.__avatarSessionID = ''

    def __isCooldown(self, actionID):
        if self.__cooldown.isInProcess(actionID):
            error = ChatCoolDownError(actionID, self.__cooldown.getDefaultCoolDown())
            g_messengerEvents.onErrorReceived(error)
            return True
        return False

    def __getAccDBID(self, avatarSessionID):
        accDBID = 0
        vehID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
        if vehID:
            accDBID = self.__arenaDP.getVehicleInfo(vehID).player.accountDBID
        return accDBID

    def __modifyRelations(self, avatarSessionID, actionID):
        vehicleID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
        if not vehicleID:
            _logger.error('can not get vehicleID for %s', avatarSessionID)
            return
        vehicleData = _RelationData(self.__arenaDP.getVehicleInfo(vehicleID))
        if not vehicleData.isValid(avatarSessionID):
            _logger.error('can not get vehicleInfo for %s', vehicleID)
            return
        isCacheChanged = False
        if actionID == BattleUserActions.ADD_FRIEND:
            isCacheChanged = self.__relationsCache.addFriend(vehicleID) or isCacheChanged
            isCacheChanged = self.__relationsCache.removeIgnored(vehicleID) or isCacheChanged
        elif actionID == BattleUserActions.REMOVE_FRIEND:
            isCacheChanged = self.__relationsCache.removeFriend(vehicleID) or isCacheChanged
        elif actionID == BattleUserActions.ADD_IGNORED:
            isCacheChanged = self.__relationsCache.addIgnored(vehicleID) or isCacheChanged
        elif actionID == BattleUserActions.REMOVE_IGNORED:
            isCacheChanged = self.__relationsCache.removeIgnored(vehicleID) or isCacheChanged
        if isCacheChanged:
            self.__relationsCache.save()
            BigWorld.player().modifyPlayerRelations(vehicleID, actionID)
            self.__notifyModification(vehicleData)
        else:
            _logger.error('cache is not modified after %s on %s ', actionID, avatarSessionID)

    def __mergeRelations(self, vehicleData):
        if vehicleData.databaseID > 0 and vehicleData.databaseID not in self.__mergedDBIDs:
            isCacheChanged = False
            realUser = self.usersStorage.getUser(vehicleData.databaseID)
            if realUser is not None:
                if realUser.isFriend():
                    isCacheChanged = self.__relationsCache.addFriend(vehicleData.vehicleID) or isCacheChanged
                if realUser.isIgnored() and not realUser.isTemporaryIgnored():
                    isCacheChanged = self.__relationsCache.addIgnored(vehicleData.vehicleID) or isCacheChanged
                if isCacheChanged:
                    self.__relationsCache.save()
            self.__mergedDBIDs.add(vehicleData.databaseID)
            return isCacheChanged
        else:
            return False

    def __notifyModification(self, vehicleData):
        actions = list()
        user = self.usersStorage.getUser(vehicleData.sessionID, scope=UserEntityScope.BATTLE)
        if user is None:
            user = self.__addBattleUser(vehicleData)
            tags = user.getTags() if user else set()
            actions.extend([ _ACTION_BY_TAG[tag, True] for tag in tags if tag in _CREATION_UPDATED_TAGS ])
        else:
            isCacheFriend = self.__relationsCache.isFriend(vehicleData.vehicleID)
            if isCacheFriend != user.isFriend():
                if isCacheFriend:
                    user.addTags((USER_TAG.FRIEND,))
                else:
                    user.removeTags((USER_TAG.FRIEND,))
                actions.append(_ACTION_BY_TAG[USER_TAG.FRIEND, isCacheFriend])
            isCacheIgnored = self.__relationsCache.isIgnored(vehicleData.vehicleID)
            if isCacheIgnored != (user.isIgnored() and not user.isTemporaryIgnored()):
                if isCacheIgnored:
                    user.addTags((USER_TAG.IGNORED,))
                else:
                    user.removeTags((USER_TAG.IGNORED,))
                actions.append(_ACTION_BY_TAG[USER_TAG.IGNORED, isCacheIgnored])
        for action in actions:
            g_messengerEvents.users.onBattleUserActionReceived(action, user)
            if action in self.__postProcs:
                self.__postProcs[action](user)

        return
