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
from mt_birthday.gui.impl.lobby.tooltips.disable_player_tooltip import DisablePlayerTooltip
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from wg_async import wg_async, wg_await
from BWUtil import AsyncReturn
if typing.TYPE_CHECKING:
    from typing import Set, Dict, List, Iterable
    from messenger.proto.xmpp.entities import XMPPUserEntity
    from mt_birthday.gui.feature_types import BattlePlayerData
PlayerData = namedtuple('_PlayerData', ('name',
 'clanAbbrev',
 'spaID',
 'locked',
 'isNameLoading'))

class PlayerSelectView(FullScreenDialogBaseView):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
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
        self.fillModel()

    def _getEvents(self):
        return ((self.viewModel.onConfirm, self.__onConfirm),
         (self.viewModel.onClose, self.__onClose),
         (self.__userInfoHelper.onNamesReceived, self.__onLastFightsNamesReceived),
         (self.__tankBirthdayController.onEventSettingsUpdated, self.__onEventSettingsUpdated))

    def __onLastFightsNamesReceived(self, receivedSpaIDs):
        with self.viewModel.transaction() as tx:
            lastFightsTab = tx.lastFights
            playersToSelect = lastFightsTab.getPlayersToSelect()
            for playerModel in playersToSelect:
                spaID = int(playerModel.getSpaID())
                if spaID not in receivedSpaIDs:
                    continue
                name = receivedSpaIDs[spaID]
                clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(spaID)
                playerModel.setName(name)
                playerModel.setClanAbbrev(clanAbbrev)
                playerModel.setIsNameLoading(False)
                self.__allPlayers[spaID] = PlayerData(name, clanAbbrev, spaID, False, False)

            playersToSelect.invalidate()

    def _getAdditionalData(self):
        return self.__selectedPlayers

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.DisablePlayerTooltip():
            return DisablePlayerTooltip(cooldown=self.__tankBirthdayController.getCooldownGiftTime())
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

    def __processFriends(self):
        friends = set()
        for friend in self.__getFriends():
            spaID = friend.getID()
            if self.isPlayerBanned(spaID):
                continue
            name = friend.getName()
            clanAbbrev = friend.getClanAbbrev()
            locked = self.__tankBirthdayController.isAlreadyReceivedGift(spaID)
            isNameLoading = False
            friends.add(PlayerData(name, clanAbbrev, spaID, locked, isNameLoading))

        friends = sorted(friends, key=lambda x: x.name.lower())
        return friends

    def __processClanmates(self):
        clanmates = set()
        for clanmate in self.__getClanmates():
            spaID = clanmate.getID()
            if self.isPlayerBanned(spaID):
                continue
            name = clanmate.getName()
            clanAbbrev = clanmate.getClanAbbrev()
            locked = self.__tankBirthdayController.isAlreadyReceivedGift(spaID)
            isNameLoading = False
            clanmates.add(PlayerData(name, clanAbbrev, spaID, locked, isNameLoading))

        clanmates = sorted(clanmates, key=lambda x: x.name.lower())
        return clanmates

    @wg_async
    def __processLastFights(self):
        lastFights = []
        lastFighters = yield wg_await(self.__tankBirthdayController.getLastFightsPlayers())
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
            lastFights.append(PlayerData(name, clanAbbrev, lastFightPlayer.spaID, locked, isNameLoading))

        self.__userInfoHelper.syncUsersInfo()
        raise AsyncReturn(lastFights)
        return

    def __fillTab(self, tab, playersData):
        for playerData in playersData:
            playerModel = PlayerModel()
            playerModel.setName(playerData.name)
            playerModel.setSpaID(playerData.spaID)
            playerModel.setClanAbbrev(playerData.clanAbbrev)
            playerModel.setLocked(playerData.locked)
            playerModel.setIsNameLoading(playerData.isNameLoading)
            tab.getPlayersToSelect().addViewModel(playerModel)
            if playerData.spaID not in self.__allPlayers:
                self.__allPlayers[playerData.spaID] = playerData

    def __fillFriendsTab(self, tx):
        friendsTab = tx.friends
        friendsList = friendsTab.getPlayersToSelect()
        friendsList.clear()
        self.__fillTab(friendsTab, self.__processFriends())
        friendsList.invalidate()
        friendsTab.setIsLoaded(True)

    def __fillClanmatesTab(self, tx):
        clanmatesTab = tx.clanmates
        clanmatesList = clanmatesTab.getPlayersToSelect()
        clanmatesList.clear()
        self.__fillTab(clanmatesTab, self.__processClanmates())
        clanmatesList.invalidate()
        clanmatesTab.setIsLoaded(True)

    def __fillLastFightsTab(self, tx, lastFighters):
        lastFightsTab = tx.lastFights
        lastFightsList = lastFightsTab.getPlayersToSelect()
        lastFightsList.clear()
        self.__fillTab(lastFightsTab, lastFighters)
        lastFightsList.invalidate()
        lastFightsTab.setIsLoaded(True)

    def __fillPreviouslySelectedPlayers(self, tx):
        previouslySelectedPlayers = tx.getPreviouslySelectedPlayers()
        previouslySelectedPlayers.clear()
        for playerData in self.__previouslySelectedPlayers:
            playerModel = PlayerModel()
            playerModel.setName(playerData.name)
            playerModel.setSpaID(playerData.spaID)
            playerModel.setClanAbbrev(playerData.clanAbbrev)
            playerModel.setLocked(playerData.locked)
            playerModel.setIsNameLoading(playerData.isNameLoading)
            previouslySelectedPlayers.addViewModel(playerModel)

        previouslySelectedPlayers.invalidate()

    @wg_async
    def __fillAsyncPart(self):
        lastFighters = yield wg_await(self.__processLastFights())
        with self.viewModel.transaction() as tx:
            self.__fillLastFightsTab(tx, lastFighters)

    def __getStampCount(self):
        return self.__tankBirthdayController.getStampCount()

    def __getMaxSelectedPlayers(self):
        return self.__tankBirthdayController.getMaxSelectedPlayers()

    def fillModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillFriendsTab(tx)
            self.__fillClanmatesTab(tx)
            self.__fillPreviouslySelectedPlayers(tx)
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
