# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/player_select_view.py
import typing
from collections import namedtuple
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper, FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.utils import getPlayerDatabaseID
from helpers import dependency
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.shared_find_criteria import MutualFriendsFindCriteria
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.player_select_view_model import PlayerSelectViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.player_model import PlayerModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.players_tab_model import PlayersTabModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.common.player_online_status_model import PlayerOnlineStatus
from mt_birthday.gui.impl.lobby.tooltips.disable_player_tooltip import DisablePlayerTooltip
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.gui.impl.sounds import BIRTHDAY_PLAYER_SELECT_SOUND_SPACE
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import getPlayerOnlineStatus, getIsPlayerWaitResponse
from th_async import th_async, th_await
from BWUtil import AsyncReturn
if typing.TYPE_CHECKING:
    from typing import Set, Dict, List, Iterable
    from messenger.proto.xmpp.entities import XMPPUserEntity
    from mt_birthday.gui.feature_types import BattlePlayerData
    from frameworks.wulf import Array
PlayerData = namedtuple('_PlayerData', ('name',
 'clanAbbrev',
 'spaID',
 'locked',
 'isNameLoading',
 'playerOnlineStatus',
 'isWaitResponse'))

class PlayerSelectView(FullScreenDialogBaseView):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    _COMMON_SOUND_SPACE = BIRTHDAY_PLAYER_SELECT_SOUND_SPACE
    __slots__ = ('__allPlayers', '__selectedPlayers', '__userInfoHelper', '__playerDatabaseID', '__previouslySelectedPlayers')

    def __init__(self, layoutID, previouslySelectedPlayers):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PlayerSelectViewModel()
        super(PlayerSelectView, self).__init__(settings)
        self.__previouslySelectedPlayers = previouslySelectedPlayers
        self.__userInfoHelper = self.__tankBirthdayController.userInfoHelper
        self.__allPlayers = dict()
        self.__selectedPlayers = []
        self.__playerDatabaseID = getPlayerDatabaseID()

    def _onLoading(self, *args, **kwargs):
        super(PlayerSelectView, self)._onLoading()
        if self.__tankBirthdayController.giftSystem.isWaitResponseNeedUpdate():
            updatedAtAfter = self.__tankBirthdayController.giftSystem.getLastPlayerUpdatedAt()
            self.__tankBirthdayController.giftSystem.requestWaitResponse(getUpdatedAtAfter=updatedAtAfter)
        self.fillModel()

    def _getEvents(self):
        return ((self.viewModel.onConfirm, self.__onConfirm),
         (self.viewModel.onClose, self.__onClose),
         (self.__userInfoHelper.onNamesReceived, self.__onNamesReceived),
         (self.__tankBirthdayController.onEventSettingsUpdated, self.__onEventSettingsUpdated))

    def __onNamesReceived(self, receivedSpaIDs):
        with self.viewModel.transaction() as tx:
            self.__fillAsyncTab(receivedSpaIDs, tx.lastFights.getPlayersToSelect())
            self.__fillAsyncTab(receivedSpaIDs, tx.sentResponse.getPlayersToSelect())

    def _getAdditionalData(self):
        return self.__selectedPlayers

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.DisablePlayerTooltip():
            return DisablePlayerTooltip()
        return PostStampTooltip() if contentID == R.views.mt_birthday.lobby.tooltips.PostStampTooltip() else super(PlayerSelectView, self).createToolTipContent(event, contentID)

    @args2params(str)
    def __onConfirm(self, selectedPlayers):
        if not selectedPlayers:
            return
        self.__selectedPlayers = [ self.__allPlayers[int(playerID)] for playerID in selectedPlayers.split(',') ]
        self._setResult(DialogButtons.SUBMIT)
        self.destroyWindow()

    def __onClose(self):
        self._setResult(DialogButtons.CANCEL)
        self.destroyWindow()

    def __onEventSettingsUpdated(self):
        if not self.__tankBirthdayController.isEnabled():
            self.__onClose()

    def _finalize(self):
        self.__userInfoHelper.clearInvalidData()
        super(PlayerSelectView, self)._finalize()

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    def __getFriends(self):
        return self.__tankBirthdayController.usersStorage.getList(MutualFriendsFindCriteria())

    def __getClanmates(self):
        clanmates = set()
        for clanmate in self.__tankBirthdayController.usersStorage.getClanMembersIterator(exCurrent=True):
            if not self.__tankBirthdayController.isPlayerInBlackList(clanmate.getID()):
                clanmates.add(clanmate)

        return clanmates

    def __getBannedPlayersIDs(self):
        return self.__tankBirthdayController.getBannedPlayersIDs()

    def isPlayerBanned(self, contactID):
        return contactID in self.__getBannedPlayersIDs()

    def isSelfPlayer(self, contactID):
        return contactID == self.__playerDatabaseID

    def __isAllowedPlayer(self, contactID):
        return any((checker(contactID) for checker in (self.isSelfPlayer, self.isPlayerBanned, self.__tankBirthdayController.isPlayerInBlackList)))

    def __processPlayers(self, playerList):
        players = set()
        for player in playerList:
            spaID = player.getID()
            if self.isPlayerBanned(spaID):
                continue
            name = player.getName()
            clanAbbrev = player.getClanAbbrev()
            locked = self.__tankBirthdayController.isAlreadyReceivedGift(spaID)
            isNameLoading = False
            playerOnlineStatus = self.__getPlayerOnlineStatus(spaID)
            isWaitResponse = getIsPlayerWaitResponse(spaID)
            players.add(PlayerData(name, clanAbbrev, spaID, locked, isNameLoading, playerOnlineStatus, isWaitResponse))

        friends = sorted(players, key=lambda x: x.name.lower())
        return friends

    @th_async
    def __processLastFights(self):
        lastFights = []
        lastFighters = yield th_await(self.__tankBirthdayController.getLastFightsPlayers())
        for lastFightPlayer in lastFighters:
            if self.__isAllowedPlayer(lastFightPlayer.spaID):
                continue
            if lastFightPlayer.name is None:
                name = self.__userInfoHelper.getUserName(lastFightPlayer.spaID, withEmptyName=True)
                isNameLoading = not name
            else:
                name = lastFightPlayer.name
                isNameLoading = False
            locked = self.__tankBirthdayController.isAlreadyReceivedGift(lastFightPlayer.spaID)
            clanAbbrev = lastFightPlayer.clanAbbrev
            if clanAbbrev is None:
                clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(lastFightPlayer.spaID) or ''
            playerOnlineStatus = self.__getPlayerOnlineStatus(lastFightPlayer.spaID)
            isWaitResponse = getIsPlayerWaitResponse(lastFightPlayer.spaID)
            lastFights.append(PlayerData(name, clanAbbrev, lastFightPlayer.spaID, locked, isNameLoading, playerOnlineStatus, isWaitResponse))

        self.__userInfoHelper.syncUsersInfo()
        raise AsyncReturn(lastFights)
        return

    def __processWaitResponse(self):
        waitResponsePlayers = []
        for playerSpaID in self.__tankBirthdayController.getWaitResponsePlayers():
            if self.__isAllowedPlayer(playerSpaID):
                continue
            name = self.__tankBirthdayController.userInfoHelper.getUserName(playerSpaID, withEmptyName=True)
            isNameLoading = not name
            locked = self.__tankBirthdayController.isAlreadyReceivedGift(playerSpaID)
            clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(playerSpaID) or ''
            playerOnlineStatus = self.__getPlayerOnlineStatus(playerSpaID)
            isWaitResponse = getIsPlayerWaitResponse(playerSpaID)
            waitResponsePlayers.append(PlayerData(name, clanAbbrev, playerSpaID, locked, isNameLoading, playerOnlineStatus, isWaitResponse))

        self.__userInfoHelper.syncUsersInfo()
        return waitResponsePlayers

    def __fillTab(self, tab, playersData):
        playersList = tab.getPlayersToSelect()
        self.__fillTabWithoutLoadedInfo(playersData, playersList)
        tab.setIsLoaded(True)

    def __fillTabWithoutLoadedInfo(self, playersData, playersList):
        playersList.clear()
        for playerData in playersData:
            playerModel = PlayerModel()
            playerModel.setLocked(playerData.locked)
            self.__fillCommonPlayerInfo(playerModel, playerData.spaID, playerData.name, playerData.clanAbbrev, playerData.isNameLoading)
            playersList.addViewModel(playerModel)
            if playerData.spaID not in self.__allPlayers:
                self.__allPlayers[playerData.spaID] = playerData

        playersList.invalidate()

    def __fillAsyncTab(self, receivedSpaIDs, playersList):
        for playerModel in playersList:
            spaID = int(playerModel.getSpaID())
            if spaID not in receivedSpaIDs:
                continue
            name = receivedSpaIDs[spaID]
            playerOnlineStatus = self.__getPlayerOnlineStatus(spaID)
            isWaitResponse = getIsPlayerWaitResponse(spaID)
            clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(spaID)
            isNameLoading = False
            self.__fillCommonPlayerInfo(playerModel, spaID, name, clanAbbrev, isNameLoading)
            self.__allPlayers[spaID] = PlayerData(name, clanAbbrev, spaID, False, isNameLoading, playerOnlineStatus, isWaitResponse)

        playersList.invalidate()

    def __fillCommonPlayerInfo(self, playerModel, spaID, name, clanAbbrev, isNameLoading):
        playerModel.setSpaID(spaID)
        playerModel.setName(name)
        playerModel.setClanAbbrev(clanAbbrev)
        playerModel.setIsNameLoading(isNameLoading)
        playerModel.playerOnlineStatus.setStatus(self.__getPlayerOnlineStatus(spaID))
        playerModel.setIsWaitResponse(getIsPlayerWaitResponse(spaID))

    def __getPlayerOnlineStatus(self, playerID):
        return getPlayerOnlineStatus(self.__tankBirthdayController.userInfoHelper.users.getUser(playerID))

    @th_async
    def __fillAsyncPart(self):
        lastFighters = yield th_await(self.__processLastFights())
        with self.viewModel.transaction() as tx:
            self.__fillTab(tx.lastFights, lastFighters)

    def __getStampCount(self):
        return self.__tankBirthdayController.getStampCount()

    def __getMaxSelectedPlayers(self):
        return self.__tankBirthdayController.getMaxSelectedPlayers()

    def fillModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillTab(tx.friends, self.__processPlayers(self.__getFriends()))
            self.__fillTab(tx.clanmates, self.__processPlayers(self.__getClanmates()))
            self.__fillTab(tx.sentResponse, self.__processWaitResponse())
            self.__fillTabWithoutLoadedInfo(self.__previouslySelectedPlayers, tx.getPreviouslySelectedPlayers())
            tx.setStampCount(self.__getStampCount())
            tx.setMaxSelectedPlayers(self.__getMaxSelectedPlayers() or 0)
        self.__fillAsyncPart()

    @property
    def viewModel(self):
        return super(PlayerSelectView, self).getViewModel()


class PlayerSelectViewWindow(FullScreenDialogWindowWrapper):
    __slots__ = ()

    def __init__(self, previouslySelectedPlayers=None):
        super(PlayerSelectViewWindow, self).__init__(PlayerSelectView(R.views.mt_birthday.lobby.birthday.PlayerSelectView(), previouslySelectedPlayers=previouslySelectedPlayers), doBlur=False)
