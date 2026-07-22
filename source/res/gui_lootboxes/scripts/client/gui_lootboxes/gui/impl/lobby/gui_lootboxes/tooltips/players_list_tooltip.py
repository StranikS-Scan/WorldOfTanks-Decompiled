# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/players_list_tooltip.py
import typing
from gui.impl.gen import R
from gui.shared.view_helpers.UsersInfoHelper import BatchUsersInfoHelper
from frameworks.wulf import ViewSettings
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.players_list_tooltip_model import PlayersListTooltipModel
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.player_info_model import PlayerInfoModel
if typing.TYPE_CHECKING:
    from typing import Dict

class PlayersListTooltip(ViewImpl):
    __slots__ = ('__playersIds', '__userInfoHelper')

    def __init__(self, playersIds, *args, **kwargs):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.PlayersListTooltip())
        settings.model = PlayersListTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__userInfoHelper = BatchUsersInfoHelper()
        self.__playersIds = set(playersIds[:])
        super(PlayersListTooltip, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(PlayersListTooltip, self)._onLoading(*args, **kwargs)
        self.__processGiftsSenders()

    @property
    def viewModel(self):
        return super(PlayersListTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__userInfoHelper.onNamesReceived, self.__onSenderNameReceived),)

    def _finalize(self):
        self.__userInfoHelper.clearInvalidData()
        super(PlayersListTooltip, self)._finalize()

    def __onSenderNameReceived(self, receivedNames):
        with self.viewModel.transaction() as vm:
            giftsSendersModel = vm.getPlayers()
            for playerId in self.__playersIds:
                name = receivedNames.get(playerId)
                if name:
                    playerModel = PlayerInfoModel()
                    playerName, clanAbbrev = self.getSenderNameAndClanAbbrev(playerId)
                    playerModel.setPlayerName(playerName)
                    playerModel.setPlayerClanTag(clanAbbrev)
                    giftsSendersModel.addViewModel(playerModel)

            giftsSendersModel.invalidate()
            isAllNamesLoaded = len(self.__playersIds) == len(giftsSendersModel)
            self.viewModel.setIsAllNamesLoaded(isAllNamesLoaded)

    def __processGiftsSenders(self):
        with self.viewModel.transaction() as vm:
            giftsSendersModel = vm.getPlayers()
            giftsSendersModel.clear()
            for playerId in self.__playersIds:
                playerModel = PlayerInfoModel()
                playerName, clanAbbrev = self.getSenderNameAndClanAbbrev(playerId)
                if playerName:
                    playerModel.setPlayerName(playerName)
                    playerModel.setPlayerClanTag(clanAbbrev)
                    giftsSendersModel.addViewModel(playerModel)

            giftsSendersModel.invalidate()
            isAllNamesLoaded = len(self.__playersIds) == len(giftsSendersModel)
            self.viewModel.setIsAllNamesLoaded(isAllNamesLoaded)
            self.viewModel.setPlayersCount(len(self.__playersIds))
            self.__userInfoHelper.syncUsersInfo()

    def getSenderNameAndClanAbbrev(self, senderID):
        name = self.__userInfoHelper.getUserName(senderID)
        clanAbbrev = ''
        if name:
            clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(senderID)
        return (name, clanAbbrev)
