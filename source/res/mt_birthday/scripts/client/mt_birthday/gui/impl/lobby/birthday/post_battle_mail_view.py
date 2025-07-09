# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/post_battle_mail_view.py
from copy import copy
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV
from frameworks.wulf import ViewSettings
from gui.gift_system.constants import GifterResponseState
from gui.gift_system.wrappers import SendGiftResponse
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.Scaleform.daapi.view.lobby.postbattle_extra_tab.postbattle_extra_tab import PostbattleExtraTabView
from helpers import dependency
from mt_birthday.birthday_constants import BIRTHDAY_2025_STAMP_CODE_SPECIAL
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.post_battle_mail_view_model import PostBattleMailViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.post_battle_player_model import PostBattlePlayerModel
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.gui.impl.lobby.tooltips.disable_player_tooltip import DisablePlayerTooltip
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from messenger.proto.events import g_messengerEvents
from messenger.m_constants import USER_ACTION_ID
from nations import MAP
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.shared import IItemsCache

def updateModelWrapper(func):

    def wrapper(self, playerSpaIDs, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            for playersList in [tx.getAllyPlayerList(), tx.getEnemyPlayerList()]:
                for playerModel in playersList:
                    playerSpaID = playerModel.userInfo.getDatabaseID()
                    if playerSpaID in playerSpaIDs:
                        func(self, playerModel, playerSpaID, *args, **kwargs)

                playersList.invalidate()

    return wrapper


class PostBattleMailView(PostbattleExtraTabView):
    __mtBirthday = dependency.descriptor(ITanksBirthdayController)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__battleResultsData', '__sentPlayerSpaID', '__arenaUniqueID')

    def __init__(self, flags, layoutID=R.views.mt_birthday.lobby.birthday.PostBattleMailView()):
        settings = ViewSettings(layoutID)
        settings.flags = flags
        settings.model = PostBattleMailViewModel()
        super(PostBattleMailView, self).__init__(settings)
        self.__battleResultsData = None
        self.__sentPlayerSpaID = None
        self.__arenaUniqueID = None
        return

    @property
    def viewModel(self):
        return super(PostBattleMailView, self).getViewModel()

    def onArenaInfoUpdated(self, arenaUniqueID):
        if self.__arenaUniqueID and not self.__arenaUniqueID == arenaUniqueID:
            LOG_DEBUG_DEV('arenaUniqueID is already exists')
        self.__arenaUniqueID = arenaUniqueID
        self.__battleResultsData = self.__battleResults.getResultsVO(arenaUniqueID)
        if self.__battleResults is not None and self.__battleResultsData:
            self.__fillModel()
        return

    def _getEvents(self):
        return ((self.viewModel.onSent, self.__onSent),
         (self.__mtBirthday.giftSystem.updateStampBalance, self.__onEntitlementsUpdated),
         (self.__mtBirthday.giftSystem.onOutcomeGift, self.__onOutcomeGift),
         (self.__mtBirthday.onEventSettingsUpdated, self.__onEventSettingsUpdated),
         (g_messengerEvents.users.onUserActionReceived, self.__onUserActionReceived))

    def __onOutcomeGift(self, sendGiftInfo, *args, **kwargs):
        if not isinstance(sendGiftInfo, SendGiftResponse):
            return
        if sendGiftInfo.receiverIDs:
            self.__updateModel(sendGiftInfo.receiverIDs, isLoading=False)

    def __onUserActionReceived(self, actionID, user, *args, **kwargs):
        if actionID in (USER_ACTION_ID.IGNORED_ADDED, USER_ACTION_ID.IGNORED_REMOVED):
            self.__updateBlackListPlayer([user.getID()])

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.PostStampTooltip():
            return PostStampTooltip()
        return DisablePlayerTooltip(cooldown=self.__mtBirthday.getCooldownGiftTime()) if contentID == R.views.mt_birthday.lobby.tooltips.DisablePlayerTooltip() else super(PostBattleMailView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PostBattleMailView, self).createToolTip(event)

    def __onEntitlementsUpdated(self):
        self.__updateStamps()
        self.__updateFirstBloggerAfterBattleGift()

    def __updateStamps(self):
        self.viewModel.setStampCount(self.__mtBirthday.getStampCount())

    def __updateFirstBloggerAfterBattleGift(self):
        self.viewModel.setIfCanSendBloggerGift(self.__mtBirthday.isFirstBloggerAfterBattleGift(self.__arenaUniqueID) and self.__mtBirthday.getSpecialStampCount())

    def finalize(self):
        self.__battleResultsData = None
        super(PostBattleMailView, self)._finalize()
        return

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            tx.setIsBlogger(self.__mtBirthday.isBlogger())
            tx.setSendBackChance(self.__mtBirthday.getMagicPercent())
            self.__updateStamps()
            self.__updateFirstBloggerAfterBattleGift()
            playersList = tx.getAllyPlayerList()
            self.__fillTeamMembers(self.__battleResultsData['team1'], playersList)
            playersList = tx.getEnemyPlayerList()
            self.__fillTeamMembers(self.__battleResultsData['team2'], playersList)

    def __fillTeamMembers(self, team, playersList):
        playersList.clear()
        teamCopy = copy(team)
        teamCopy.reverse()
        for teamMember in teamCopy:
            if teamMember['isSelf']:
                continue
            vehicleCD = teamMember['vehicleCD']
            vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
            playerModel = PostBattlePlayerModel()
            playerModel.userInfo.setUserName(teamMember['userVO']['userName'])
            playerModel.userInfo.setClanAbbrev(teamMember['userVO']['clanAbbrev'])
            databaseID = teamMember['playerId']
            playerModel.userInfo.setDatabaseID(databaseID)
            playerModel.vehicleInfo.setVehicleTechName(getNationLessName(vehicle.name))
            playerModel.vehicleInfo.setVehicleShortName(teamMember['vehicleName'])
            playerModel.vehicleInfo.setVehicleNation(MAP[vehicle.nationID])
            playerModel.setIsDisabled(self.__mtBirthday.isAlreadyReceivedGift(databaseID))
            playerModel.setIsBanned(self.__mtBirthday.isBannedPlayer(databaseID))
            playerModel.setIsPlayerInBlacklist(self.__mtBirthday.isPlayerInBlackList(databaseID))
            playerModel.setIsBot(databaseID == 0)
            playerModel.setTotalDamage(teamMember['damageDealt'])
            playerModel.setKills(teamMember['kills'])
            playerModel.setXp(teamMember['xp'])
            playersList.addViewModel(playerModel)

        playersList.invalidate()

    def __onSent(self, args):
        if not self.__mtBirthday.isEnabled():
            return
        if 'playerId' not in args:
            LOG_ERROR('%r: Argument "playerId" is not defined in %r', self, args)
            return
        spaID = args['playerId']
        if self.__mtBirthday.isGiftSystemEventActive:
            self.__mtBirthday.giftSystem.sendGifts(self.__mtBirthday.getStampForSending(self.__arenaUniqueID), [spaID], self.__mtBirthday.getRandomBloggerPhraseID(), self.__onSentCallback)
            self.__sentPlayerSpaID = spaID
            self.__updateModel([self.__sentPlayerSpaID], isLoading=True)
        else:
            LOG_DEBUG_DEV('GIft Event is not enabled, cannot send gift')

    def __onSentCallback(self, result):
        if result.state is GifterResponseState.WEB_SUCCESS:
            for declinedReceiver in result.declinedReceivers:
                self.__mtBirthday.addBannedPlayersID(declinedReceiver)

            if result.entitlementCode == BIRTHDAY_2025_STAMP_CODE_SPECIAL and self.__sentPlayerSpaID not in result.declinedReceivers:
                self.__mtBirthday.onBloggerGiftSent(self.__arenaUniqueID)
                if self.viewModel:
                    self.__updateFirstBloggerAfterBattleGift()
            if self.viewModel:
                self.__updateModel([self.__sentPlayerSpaID], isLoading=False)

    @updateModelWrapper
    def __updateBlackListPlayer(self, playerModel, playerSpaID, *args, **kwargs):
        playerModel.setIsPlayerInBlacklist(self.__mtBirthday.isPlayerInBlackList(playerSpaID))

    @updateModelWrapper
    def __updateModel(self, playerModel, playerSpaID, *args, **kwargs):
        playerModel.setIsBanned(self.__mtBirthday.isBannedPlayer(playerSpaID))
        isLoading = kwargs.get('isLoading', None)
        if isLoading is not None:
            playerModel.setIsLoading(isLoading)
            playerModel.setIsDisabled(not isLoading)
        return

    def __onEventSettingsUpdated(self):
        self.__changeSendButtonsStatus(self.__mtBirthday.isEnabled())

    def __changeSendButtonsStatus(self, enable=True):
        with self.viewModel.transaction() as tx:
            for playersList in [tx.getAllyPlayerList(), tx.getEnemyPlayerList()]:
                for playerModel in playersList:
                    playerModel.setIsDisabled(not enable)

                playersList.invalidate()
