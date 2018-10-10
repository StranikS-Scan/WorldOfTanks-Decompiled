# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/tmp_ignore_list_ctrl.py
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.battle_control.battle_cache.cache_records import TmpIgnoredCacheRecord
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from messenger.proto.events import g_messengerEvents
from messenger.m_constants import USER_ACTION_ID, PROTO_TYPE

class _TmpIgnoreListCtrl(IBattleController):

    def __init__(self, setup):
        super(_TmpIgnoreListCtrl, self).__init__()
        self.__arenaDP = setup.arenaDP
        self.__tmpIgnoredRecord = TmpIgnoredCacheRecord.get()

    @proto_getter(PROTO_TYPE.MIGRATION)
    def protoMigration(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def getControllerID(self):
        return BATTLE_CTRL_ID.TMP_IGNORE_LIST_CTRL

    def startControl(self):
        g_messengerEvents.users.onUsersListReceived += self._onUserListReceived
        g_messengerEvents.users.onUserActionReceived += self._onUserActionReceived

    def stopControl(self):
        g_messengerEvents.users.onUsersListReceived -= self._onUserListReceived
        g_messengerEvents.users.onUserActionReceived -= self._onUserActionReceived
        self.__tmpIgnoredRecord = None
        self.__arenaDP = None
        return

    def _onUserActionReceived(self, usrActionID, user):
        if self.__arenaDP is not None:
            isCacheChanged = False
            if USER_ACTION_ID.TMP_IGNORED_ADDED == usrActionID:
                isCacheChanged = self.__tmpIgnoredRecord.addToTmpIgnored(user.getID())
            elif USER_ACTION_ID.TMP_IGNORED_REMOVED == usrActionID:
                isCacheChanged = self.__tmpIgnoredRecord.removeTmpIgnored(user.getID())
            if isCacheChanged:
                self.__tmpIgnoredRecord.save()
        return

    def _onUserListReceived(self, tags):
        self.__syncTmpIgnoredAccounts()

    def __syncTmpIgnoredAccounts(self):
        if self.__arenaDP is not None:
            for accDBID in self.__tmpIgnoredRecord.getTmpIgnored():
                contact = self.usersStorage.getUser(accDBID)
                if contact is None or not contact.isIgnored():
                    vID = self.__arenaDP.getVehIDByAccDBID(accDBID)
                    vInfo = self.__arenaDP.getVehicleInfo(vID)
                    name = vInfo.player.name or ''
                    self.protoMigration.contacts.addTmpIgnored(accDBID, name)

        return


def createTmpIgnoreListCtrl(setup):
    arenaGuiTypeVisitor = setup.arenaVisitor.gui
    return None if arenaGuiTypeVisitor.isTutorialBattle() else _TmpIgnoreListCtrl(setup)
