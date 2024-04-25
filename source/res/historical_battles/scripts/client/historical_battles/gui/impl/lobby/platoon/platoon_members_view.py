# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/platoon/platoon_members_view.py
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, BonusState, _strButtons
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.impl.lobby.platoon.platoon_helpers import removeNationFromTechName
from gui.prb_control.entities.base.unit.entity import UnitEntity
from gui.prb_control.settings import REQUEST_TYPE
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.gui_items.badge import Badge
from helpers import i18n, dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_slot_model import HbSlotModel, FrontmanRole
from historical_battles.gui.impl.lobby.platoon.platoon_helpers import getPlatoonSlotsData, getCommanderInfo
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_members_window_model import HbMembersWindowModel
from messenger.m_constants import USER_TAG
from messenger.formatters import TimeFormatter
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from adisp import adisp_process

class HistoricalBattlesMembersView(SquadMembersView):
    _battleType = 'historical_battles'
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    _gameEventController = dependency.descriptor(IGameEventController)
    _R_TOOLTIPS_TEXT = R.strings.tooltips.event.squad
    _layoutID = R.views.historical_battles.lobby.MembersWindow()

    @property
    def prbEntity(self):
        return self.__platoonCtrl.prbEntity

    @property
    def _viewModelClass(self):
        return HbMembersWindowModel

    def _onLoading(self, *args, **kwargs):
        super(HistoricalBattlesMembersView, self)._onLoading(*args, **kwargs)
        self._gameEventController.onDisableFrontsWidget(not self.prbEntity.isCommander())
        self._updateButtons()
        self._fillModel()

    def _addListeners(self):
        super(HistoricalBattlesMembersView, self)._addListeners()
        self._gameEventController.onFrontmanLockChanged += self._updateReadyButton
        self._gameEventController.onSelectedFrontmanChanged += self._updateReadyButton
        self._gameEventController.onGameParamsChanged += self._updateReadyButton
        self._gameEventController.onSelectedFrontChanged += self._updateReadyButton
        self._gameEventController.onLobbyHeaderUpdate += self._updateReadyButton

    def _removeListeners(self):
        self._gameEventController.onFrontmanLockChanged -= self._updateReadyButton
        self._gameEventController.onSelectedFrontmanChanged -= self._updateReadyButton
        self._gameEventController.onGameParamsChanged -= self._updateReadyButton
        self._gameEventController.onSelectedFrontChanged -= self._updateReadyButton
        self._gameEventController.onLobbyHeaderUpdate -= self._updateReadyButton
        super(HistoricalBattlesMembersView, self)._removeListeners()

    def _finalize(self):
        self._gameEventController.onDisableFrontsWidget(False)
        super(HistoricalBattlesMembersView, self)._finalize()

    def _getPlatoonSlotsData(self):
        return getPlatoonSlotsData(self.prbEntity)

    def _getCommanderInfo(self):
        entity = self.prbEntity
        return getCommanderInfo(entity, entity.getID()) if isinstance(entity, UnitEntity) else {}

    def _isCommander(self):
        return self.prbEntity.isCommander()

    def _updateReadyButton(self, *args):
        if not self.__platoonCtrl.isInPlatoon():
            return
        isInQueue = self.__platoonCtrl.isInQueue()
        actionButtonStateVO = SquadActionButtonStateVO(self.prbEntity)
        simpleState = actionButtonStateVO.getSimpleState()
        onlyReadinessText = actionButtonStateVO.isReadinessTooltip()
        front = self._gameEventController.frontController.getSelectedFront()
        isInBan = self._gameEventController.isBanned
        with self.viewModel.transaction() as model:
            if not self.__platoonCtrl.isInCoolDown(REQUEST_TYPE.SET_PLAYER_STATE):
                model.btnSwitchReady.setIsEnabled(actionButtonStateVO['isEnabled'] and not isInQueue)
            if self.__platoonCtrl.getPlayerInfo().isReady:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.notReady.caption()))
            else:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.ready.caption()))
            tooltip = ''
            if actionButtonStateVO['toolTipData']:
                tooltip = i18n.makeString(actionButtonStateVO['toolTipData'] + '/body')
            elif not self._gameEventController.isBattlesEnabled():
                simpleState = backport.text(R.strings.hb_lobby.memberWindow.btnReady.footerMsg.frontDisable())
                tooltip = backport.text(R.strings.hb_lobby.hangar.startBtn.disabled.body())
            elif not front.isEnabled() or not front.isAvailable():
                simpleState = backport.text(R.strings.hb_lobby.memberWindow.btnReady.footerMsg.frontDisable())
                tooltip = backport.text(R.strings.hb_lobby.hangar.startBtn.notReady.body())
            if tooltip:
                model.btnSwitchReady.setDescription(tooltip)
            model.setFooterMessage(simpleState)
            model.setIsFooterMessageGrey(actionButtonStateVO['isEnabled'] or onlyReadinessText or isInQueue)
            if isInBan:
                startButtonR = R.strings.hb_lobby.hangar.startBtn
                timeStr = TimeFormatter.getLongDatetimeFormat(self._gameEventController.banExpiryTime)
                body = backport.text(startButtonR.banned.body(), time=timeStr)
                model.setFooterMessage(body)
                model.btnSwitchReady.setIsEnabled(False)
        self._fillModel()

    def _updateMembers(self):
        self._updateSlotsData()
        self._updateUnitCommanderData()
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as model:
            model.setIsEvent(True)

    def _updateUnitCommanderData(self):
        isUnitCommander = self._isCommander()
        self._gameEventController.onDisableFrontsWidget(not isUnitCommander)
        if not isUnitCommander:
            self._gameEventController.frontController.setSelectedFrontID(0)

    @adisp_process
    def _onSwitchReady(self):
        result = yield self._platoonCtrl.togglePlayerReadyAction(checkAmmo=False)
        if result:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)

    def _updateSlotsData(self):
        platoonCtrl = self.__platoonCtrl
        searching = platoonCtrl.isInSearch()
        isWTREnabled = self.__lobbyContext.getServerSettings().isWTREnabled()
        accID = BigWorld.player().id
        estimatedTime = self._getEstimatedTimeInQueue()
        slots = self._getPlatoonSlotsData()
        with self.viewModel.transaction() as model:
            slotModelArray = model.getSlots()
            slotModelArray.clear()
            slotCount = 0
            for it in slots:
                playerData = it.get('player', {})
                slot = HbSlotModel()
                slot.setIsEmpty(not bool(playerData))
                if playerData:
                    slot.player.commonData.setName(playerData.get('userName', ''))
                    slot.player.commonData.setColor('#DE1E7E')
                    slot.player.setIsReady(playerData.get('readyState', False))
                    slot.player.setAccID(str(playerData.get('dbID', None)))
                    slot.player.setIsCommander(playerData.get('isCommander', False))
                    slot.player.setIsCurrentUser(accID == playerData.get('accID', None))
                    slot.player.commonData.setClanTag(playerData.get('clanAbbrev', ''))
                    slot.player.setIsPrem(it.get('hasPremiumAccount', False))
                    slot.player.commonData.setRating(playerData.get('accountWTR', '') if isWTREnabled else '')
                    badgeIconPath = playerData.get('badgeVisualVO', {}).get('icon', '')
                    slot.player.commonData.setBadgeID(Badge.getBadgeIDFromIconPath(badgeIconPath))
                    playerStatus = it.get('playerStatus', PLAYER_GUI_STATUS.NORMAL)
                    slot.setIsInBattle(playerStatus == PLAYER_GUI_STATUS.BATTLE)
                    if playerStatus == PLAYER_GUI_STATUS.BATTLE:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.inBattle()))
                    elif playerStatus != PLAYER_GUI_STATUS.READY:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.notReady()))
                    isAdditionalMsgVisible = it.get('isVisibleAdtMsg', False)
                    if isAdditionalMsgVisible:
                        additionalMsg = it.get('additionalMsg', '')
                        slot.setInfoText(additionalMsg)
                    isOffline = playerData.get('isOffline', False)
                    if isOffline:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.connectionLost()))
                    colors = playerData.get('colors', [])
                    if len(colors) > 1:
                        slot.player.commonData.setColor('#' + '{0:06X}'.format(colors[1 if isOffline else 0]))
                    tags = playerData.get('tags', [])
                    slot.player.voice.setIsMutedByUser(USER_TAG.MUTED in tags)
                    slot.player.setIsIgnored(USER_TAG.IGNORED in tags)
                    vehicle = it.get('selectedVehicle', {})
                    if vehicle:
                        vehicleItem = self.__itemsCache.items.getItemByCD(vehicle.get('intCD', 0))
                        slot.player.vehicle.setName(vehicleItem.userName)
                        slot.player.vehicle.setTechName(replaceHyphenToUnderscore(removeNationFromTechName(vehicleItem.name)))
                        slot.player.vehicle.setType(vehicleItem.type)
                        slot.player.vehicle.setNation(vehicleItem.nationName)
                        slot.setVehicleImage(R.images.gui.maps.icons.vehicle.dyn(replaceHyphenToUnderscore(vehicleItem.name.replace(':', '-')))())
                else:
                    slot.setIsSearching(searching)
                    slot.setInfoText(backport.text(R.strings.platoon.members.card.empty()))
                    slot.setEstimatedTime(estimatedTime)
                    slotLabelHtml = it.get('slotLabel', '')
                    if slotLabelHtml:
                        self._convertSlotLabelData(slot.getSlotLabelElements(), slotLabelHtml)
                slot.setIsProfiledVehicle(it.get('selectedVehicleLevel', 0) > 1)
                slot.setSpeciality(it.get('speciality', FrontmanRole.NONE))
                slot.setSpecialityTooltipHead(it.get('specialityTooltipHead', ''))
                slot.setSpecialityTooltipBody(it.get('specialityTooltipBody', ''))
                slot.setSlotId(slotCount)
                slotCount += 1
                slotModelArray.addViewModel(slot)

            slotModelArray.invalidate()
            self._updateButtons()
            self._updateHeader()
        return

    def _onFrontChanged(self, args=None):
        frontID = int(args.get('id'))
        if frontID is not None:
            self._gameEventController.frontController.setSelectedFrontID(frontID)
        self._updateReadyButton()
        return

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview(R.views.historical_battles.lobby.subViews.Chat()))

    def _getTitle(self):
        title = ''.join((backport.text(R.strings.platoon.squad()), backport.text(R.strings.hb_lobby.memberWindow.header.event())))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.hb_lobby.memberWindow.header.tooltip.event.header())
        tooltipBody = backport.text(R.strings.hb_lobby.memberWindow.header.tooltip.event.body())
        return (tooltipHeader, tooltipBody)

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(True)
            model.setShowNoBonusPlaceholder(True)
            model.noBonusPlaceholder.setIcon(R.images.historical_battles.gui.maps.icons.membersWindow.icon())
            self._currentBonusState = bonusState

    def _getBonusState(self):
        return BonusState.NO_BONUS

    def _createHeaderInfoTooltip(self):
        tooltip = R.strings.platoon.members.header.noBonusPlaceholder.tooltip
        header = backport.text(tooltip.header())
        body = backport.text(tooltip.body())
        return self._createSimpleTooltipContent(header=header, body=body)
