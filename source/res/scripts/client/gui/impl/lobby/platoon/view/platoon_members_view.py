# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_members_view.py
import logging
import BigWorld
import typing
from enum import Enum
from helpers.CallbackDelayer import CallbackDelayer
import VOIP
from BonusCaps import BonusCapsConst
from CurrentVehicle import g_currentVehicle
from UnitBase import UNDEFINED_ESTIMATED_TIME
from adisp import adisp_process
from constants import PremiumConfigs, Configs
from frameworks.wulf import WindowFlags, ViewSettings, WindowStatus
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES import MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl import backport
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.backport.backport_context_menu import createContextMenuData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.platoon.comp7_member_count_dropdown import Comp7DropdownItem
from gui.impl.gen.view_models.views.lobby.platoon.comp7_slot_model import Comp7SlotModel
from gui.impl.gen.view_models.views.lobby.platoon.comp7_window_model import Comp7WindowModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel, PrebattleTypes
from gui.impl.gen.view_models.views.lobby.platoon.slot_label_element_model import SlotLabelElementModel, Types
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel, ErrorType
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7 import comp7_shared
from gui.impl.lobby.comp7.comp7_model_helpers import getSeasonNameEnum
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from gui.impl.lobby.platoon.platoon_helpers import formatSearchEstimatedTime, BonusState, getPlatoonBonusState
from gui.impl.lobby.platoon.tooltip.platoon_alert_tooltip import AlertTooltip
from gui.impl.lobby.platoon.tooltip.platoon_wtr_tooltip import WTRTooltip
from gui.impl.lobby.platoon.view.slot_label_html_handler import SlotLabelHtmlParser
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.impl.lobby.platoon.view.subview.platoon_tiers_filter_subview import SettingsPopover
from gui.impl.lobby.platoon.view.subview.platoon_tiers_limit_subview import TiersLimitSubview
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.impl.pub import ViewImpl
from gui.prb_control import prb_getters, prbEntityProperty
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE, SELECTOR_BATTLE_TYPES
from gui.prestige.prestige_helpers import hasVehiclePrestige, fillPrestigeEmblemModel
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from gui.shared.gui_items.badge import Badge
from helpers import i18n, dependency
from messenger.ext import channel_num_gen
from messenger.m_constants import PROTO_TYPE
from messenger.m_constants import USER_TAG
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from shared_utils import findFirst
from skeletons.gui.game_control import IPlatoonController, IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from helpers.server_settings import Comp7RanksConfig
    from comp7_ranks_common import Comp7Division
_logger = logging.getLogger(__name__)
_strButtons = R.strings.platoon.buttons

def getMemberContextMenuData(event, platoonSlotsData):
    userName = event.getArgument('userName')
    if userName:
        for it in platoonSlotsData:
            playerData = it['player']
            if playerData is not None and playerData['userName'] == userName:
                return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.UNIT_USER, playerData)

    _logger.warning('Username %s not found in platoon slots data', userName)
    return


_MULTIPLE_FREE_SLOTS_BORDER = 2

def _floatToPercents(value):
    return int(value * 100)


class _LayoutStyle(Enum):
    HORIZONTAL = 'horizontal'
    HORIZONTAL_SHORT = 'horizontal_short'
    VERTICAL = 'vertical'


class SquadMembersView(ViewImpl, CallbackDelayer):
    _platoonCtrl = dependency.descriptor(IPlatoonController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _layoutID = R.views.lobby.platoon.MembersWindow()
    _prebattleType = PrebattleTypes.SQUAD

    def __init__(self, prbType):
        settings = ViewSettings(layoutID=self._layoutID, model=self._viewModelClass())
        self._currentBonusState = None
        self.__prbEntityType = prbType
        super(SquadMembersView, self).__init__(settings)
        return

    def getPrebattleType(self):
        return self._prebattleType.value

    def getPrbEntityType(self):
        return self.__prbEntityType

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def _viewModelClass(self):
        return MembersWindowModel

    @property
    def _slotModelClass(self):
        return SlotModel

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def _onLoading(self, *args, **kwargs):
        self._addListeners()
        self._addSubviews()
        with self.viewModel.transaction() as model:
            model.setCanMinimize(True)
        self._initWindowData()
        self._updateMembers()

    def _initialize(self, *args, **kwargs):
        self.__setPreBattleCarouselOpened(True)
        self.__setPreBattleCarouselFocus(True)

    def _finalize(self):
        self._removeListeners()
        self.__setPreBattleCarouselOpened(False)
        self.__setPreBattleCarouselFocus(False)
        self.clearCallbacks()

    def _addSubviewToLayout(self, subview):
        self.setChildView(subview.layoutID, subview)

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())
        self._addSubviewToLayout(TiersLimitSubview())

    def createPopOverContent(self, event):
        return SettingsPopover()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.platoon.AlertTooltip():
            if self._platoonCtrl.isInCoolDown(REQUEST_TYPE.AUTO_SEARCH):
                return
            tooltip = R.strings.platoon.buttons.findPlayers.tooltip
            header = tooltip.header()
            if not self._platoonCtrl.isSearchingForPlayersEnabled():
                body = tooltip.noAssembling.body()
            else:
                body = tooltip.noSuitableTank.body()
            return AlertTooltip(header, body)
        elif contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip():
            return SquadBonusTooltipContent(bonusState=getPlatoonBonusState(True))
        else:
            if contentID == R.views.lobby.platoon.WTRTooltip():
                slotId = event.getArgument('slotId')
                slot = next((slot for slot in self.viewModel.getSlots() if slot.getSlotId() == slotId), None)
                if slot is not None:
                    commonData = slot.player.commonData
                    return WTRTooltip(commonData.getName(), commonData.getClanTag(), commonData.getBadgeID(), commonData.getRating())
            return super(SquadMembersView, self).createToolTipContent(event=event, contentID=contentID)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getMemberContextMenuData(event, self._platoonCtrl.getPlatoonSlotsData())
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.onStatusChanged += self.__onStatusChangedContextMenu
                window.load()
                return window
        return super(SquadMembersView, self).createContextMenu(event)

    def __onStatusChangedContextMenu(self, windowStatus):
        if windowStatus == WindowStatus.DESTROYED and self._platoonCtrl.isInPlatoon():
            self._updateMembers()

    def _addListeners(self):
        with self.viewModel.transaction() as model:
            model.btnInviteFriends.onClick += self._onInviteFriends
            model.btnSwitchReady.onClick += self._onSwitchReady
            model.btnFindPlayers.onClick += self._onFindPlayers
            model.header.btnMuteAll.onClick += self._onToggleMuteAll
            model.header.btnLeavePlatoon.onClick += self._onLeavePlatoon
            model.onClosed += self._onLeavePlatoon
            model.onMinimized += self.__onMinimized
            model.onFocusChange += self.__onFocusChange
        self._platoonCtrl.onMembersUpdate += self._updateMembers
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        g_messengerEvents.voip.onChannelEntered += self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLeft += self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelAvailable += self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLost += self.__updateVoiceChatToggleState
        g_currentVehicle.onChanged += self._updateReadyButton
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.__onUsersReceived
        usersEvents.onUserActionReceived += self.__onUserActionReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged += self._updateMembers
            unitMgr.unit.onSquadSizeChanged += self._updateMembers
        g_eventBus.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self._updateReadyButton, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__onMinimized, scope=EVENT_BUS_SCOPE.LOBBY)
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._platoonCtrl.onAvailableTiersForSearchChanged += self.__onAvailableTiersForSearchChanged
        self._platoonCtrl.onAutoSearchCooldownChanged += self._updateFindPlayersButton

    def _removeListeners(self):
        with self.viewModel.transaction() as model:
            model.btnInviteFriends.onClick -= self._onInviteFriends
            model.btnSwitchReady.onClick -= self._onSwitchReady
            model.btnFindPlayers.onClick -= self._onFindPlayers
            model.header.btnMuteAll.onClick -= self._onToggleMuteAll
            model.header.btnLeavePlatoon.onClick -= self._onLeavePlatoon
            model.onClosed -= self._onLeavePlatoon
            model.onMinimized -= self.__onMinimized
            model.onFocusChange -= self.__onFocusChange
        self._platoonCtrl.onMembersUpdate -= self._updateMembers
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        g_messengerEvents.voip.onChannelEntered -= self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLeft -= self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelAvailable -= self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLost -= self.__updateVoiceChatToggleState
        g_currentVehicle.onChanged -= self._updateReadyButton
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self.__onUsersReceived
        usersEvents.onUserActionReceived -= self.__onUserActionReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged -= self._updateMembers
            unitMgr.unit.onSquadSizeChanged -= self._updateMembers
        g_eventBus.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self._updateReadyButton, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__onMinimized, scope=EVENT_BUS_SCOPE.LOBBY)
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self._platoonCtrl.onAvailableTiersForSearchChanged -= self.__onAvailableTiersForSearchChanged
        self._platoonCtrl.onAutoSearchCooldownChanged -= self._updateFindPlayersButton

    def _getEstimatedTimeInQueue(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            estimatedTime = unitMgr.unit.getEstimatedTimeInQueue()
            if estimatedTime != UNDEFINED_ESTIMATED_TIME:
                return formatSearchEstimatedTime(estimatedTime)

    @staticmethod
    def _convertSlotLabelData(slotLabelArray, slotLabelHtml):
        slotLabelArray.clear()
        parser = SlotLabelHtmlParser()
        parser.feed(slotLabelHtml)
        slotLabelElements = parser.getElements()
        for element in slotLabelElements:
            model = SlotLabelElementModel()
            model.setType(element.get('type', Types.TEXT))
            model.setContent(element.get('text', ''))
            model.setStyleJson(element.get('style', ''))
            slotLabelArray.addViewModel(model)

    def _updateMembers(self):
        slots = self._getPlatoonSlotsData()
        searching = self._platoonCtrl.isInSearch()
        isWTREnabled = self._getWTRStatus()
        accID = BigWorld.player().id
        estimatedTime = self._getEstimatedTimeInQueue()
        with self.viewModel.transaction() as model:
            slotModelArray = model.getSlots()
            slotModelArray.clear()
            slotCount = 0
            for slotData in slots:
                playerData = slotData.get('player', {})
                isEmpty = not bool(playerData)
                slotModel = self._slotModelClass()
                slotModel.setIsEmpty(isEmpty)
                slotModel.setPrebattleType(self._prebattleType)
                if playerData:
                    self._setPlayerData(accID, isWTREnabled, slotData, playerData, slotModel)
                    self._setVehicleData(slotData, slotModel)
                    self._setModeSlotSpecificData(slotData, slotModel)
                else:
                    slotModel.setIsSearching(searching)
                    slotModel.setInfoText(backport.text(R.strings.platoon.members.card.empty()))
                    slotModel.setEstimatedTime(estimatedTime)
                    slotLabelHtml = slotData.get('slotLabel', '')
                    if slotLabelHtml:
                        self._convertSlotLabelData(slotModel.getSlotLabelElements(), slotLabelHtml)
                slotModel.setSlotId(slotCount)
                slotCount += 1
                slotModelArray.addViewModel(slotModel)

            slotModelArray.invalidate()
            self._updateButtons()
            self._updateHeader()

    def _getPlatoonSlotsData(self):
        return self._platoonCtrl.getPlatoonSlotsData()

    def _setPlayerData(self, accID, isWTREnabled, slotData, playerData, slotModel):
        slotModel.player.commonData.setName(playerData.get('userName', ''))
        slotModel.player.commonData.setColor('#DE1E7E')
        slotModel.player.setIsReady(playerData.get('readyState', False))
        slotModel.player.setAccID(str(playerData.get('dbID', None)))
        slotModel.player.setIsCommander(playerData.get('isCommander', False))
        slotModel.player.setIsCurrentUser(accID == playerData.get('accID', None))
        slotModel.player.commonData.setClanTag(playerData.get('clanAbbrev', ''))
        slotModel.player.setIsPrem(slotData.get('hasPremiumAccount', False))
        slotModel.player.commonData.setRating(playerData.get('accountWTR', '') if isWTREnabled else '')
        badgeIconPath = playerData.get('badgeVisualVO', {}).get('icon', '')
        slotModel.player.commonData.setBadgeID(Badge.getBadgeIDFromIconPath(badgeIconPath))
        playerStatus = slotData.get('playerStatus', PLAYER_GUI_STATUS.NORMAL)
        slotModel.setIsInBattle(playerStatus == PLAYER_GUI_STATUS.BATTLE)
        slotModel.setPrebattleType(self._prebattleType)
        if playerStatus == PLAYER_GUI_STATUS.BATTLE:
            slotModel.setInfoText(backport.text(R.strings.platoon.members.card.inBattle()))
        elif playerStatus != PLAYER_GUI_STATUS.READY:
            slotModel.setInfoText(backport.text(R.strings.platoon.members.card.notReady()))
        isAdditionalMsgVisible = slotData.get('isVisibleAdtMsg', False)
        if isAdditionalMsgVisible:
            additionalMsg = slotData.get('additionalMsg', '')
            slotModel.setInfoText(additionalMsg)
        isOffline = playerData.get('isOffline', False)
        if isOffline:
            slotModel.setInfoText(backport.text(R.strings.platoon.members.card.connectionLost()))
        colors = playerData.get('colors', [])
        if len(colors) > 1:
            slotModel.player.commonData.setColor('#' + '{0:06X}'.format(colors[1 if isOffline else 0]))
        tags = playerData.get('tags', [])
        slotModel.player.voice.setIsMutedByUser(USER_TAG.MUTED in tags)
        slotModel.player.setIsIgnored(USER_TAG.IGNORED in tags)
        prestigeLevel = slotData.get('prestigeLevel', 0)
        vehicleData = slotData.get('selectedVehicle')
        vehicleCD = vehicleData.get('intCD', 0) if vehicleData else 0
        isPrestigeAvailable = hasVehiclePrestige(vehicleCD) and prestigeLevel != 0
        slotModel.player.setIsPrestigeAvailable(isPrestigeAvailable)
        if isPrestigeAvailable:
            fillPrestigeEmblemModel(slotModel.player.prestigeEmblem, prestigeLevel, vehicleCD)
        return

    def _setVehicleData(self, slotData, slotModel):
        vehicle = slotData.get('selectedVehicle', {})
        if vehicle:
            vehicleItem = self._itemsCache.items.getItemByCD(vehicle.get('intCD', 0))
            fillVehicleModel(slotModel.player.vehicle, vehicleItem)

    def _setModeSlotSpecificData(self, slotData, slotModel):
        pass

    def _getIsVehiclePremium(self, vehicle):
        return vehicle.isPremium or vehicle.isElite

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.standard.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.standard.body())
        return (tooltipHeader, tooltipBody)

    def _initWindowData(self):
        with self.viewModel.transaction() as model:
            model.setCanMinimize(True)
            model.setRawTitle(self._getTitle())
            header, body = self._getWindowInfoTooltipHeaderAndBody()
            model.setWindowTooltipHeader(header)
            model.setWindowTooltipBody(body)
            layoutStyle = self.__getLayoutStyle()
            fileName = '{battleType}_{layout}_list'.format(battleType=self._prebattleType.value, layout=layoutStyle.value)
            self._setHeaderBg(fileName, model)
            model.setIsHorizontal(layoutStyle in (_LayoutStyle.HORIZONTAL, _LayoutStyle.HORIZONTAL_SHORT))
            model.setIsShort(layoutStyle == _LayoutStyle.HORIZONTAL_SHORT)
            model.setPrebattleType(self._prebattleType)
            self._initWindowModeSpecificData(model)
        self._setBonusInformation(getPlatoonBonusState(True))

    def _setHeaderBg(self, fileName, model):
        fileNameRes = R.images.gui.maps.icons.platoon.members_window.backgrounds.dyn(fileName)
        if fileNameRes.exists():
            model.header.setBackgroundImage(backport.image(fileNameRes()))
        else:
            _logger.warning('R.images.gui.maps.icons.platoon.members_window.backgrounds %s not found', fileName)

    def _initWindowModeSpecificData(self, model):
        pass

    def _setBonusInformation(self, bonusState):
        hasBonuses = bonusState != BonusState.NO_BONUS
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(hasBonuses)
            model.setShowNoBonusPlaceholder(not hasBonuses)
            if hasBonuses:
                bonusesArray = model.getBonuses()
                bonusesArray.clear()
                xpBonusModel = self._createXpBonusModel(bonusState)
                if xpBonusModel:
                    bonusesArray.addViewModel(xpBonusModel)
                creditBonusModel = self._createPremiumBonusModel(bonusState)
                if creditBonusModel:
                    bonusesArray.addViewModel(creditBonusModel)
                bonusesArray.invalidate()
            else:
                self._setNoBonusInformation(model)
        self._currentBonusState = bonusState

    def _setNoBonusInformation(self, model):
        pass

    def _updateHeader(self):
        bonusState = getPlatoonBonusState(True)
        if bonusState != self._currentBonusState:
            self._setBonusInformation(bonusState)

    def _createXpBonusModel(self, bonusState):
        if BonusState.hasAnyBitSet(bonusState, BonusState.XP_BONUS):
            xpBonusModel = BonusModel()
            xpBonusModel.setCurrency(BonusModel.XP)
            xpBonusModel.setAmount(_floatToPercents(self._eventsCache.getSquadXPFactor()))
            return xpBonusModel
        else:
            return None

    def _createPremiumBonusModel(self, bonusState):
        if BonusState.hasAnyBitSet(bonusState, BonusState.SQUAD_CREDITS_BONUS | BonusState.PREM_CREDITS_BONUS):
            squadPremiumBonus = self._lobbyContext.getServerSettings().squadPremiumBonus
            amount = squadPremiumBonus.ownCredits if BonusState.hasAnyBitSet(bonusState, BonusState.PREM_CREDITS_BONUS) else squadPremiumBonus.mateCredits
            amount = int(round(amount * 100))
            creditBonusModel = BonusModel()
            creditBonusModel.setCurrency(BonusModel.CREDITS)
            creditBonusModel.setAmount(amount)
            return creditBonusModel
        else:
            return None

    def _updateButtons(self):
        platoonCtrl = self._platoonCtrl
        isInQueue = platoonCtrl.isInQueue()
        isCommander = self._isCommander()
        canSendInvite = platoonCtrl.getPermissions().canSendInvite()
        isInSearch = platoonCtrl.isInSearch()
        self.__updateVoiceChatToggleState()
        canInviteMoreThanOne = platoonCtrl.getMaxSlotCount() > _MULTIPLE_FREE_SLOTS_BORDER
        inviteLabels = _strButtons.invite.players if canInviteMoreThanOne else _strButtons.invite.player
        with self.viewModel.transaction() as model:
            model.setIsCommander(isCommander)
            model.header.btnLeavePlatoon.setCaption(backport.text(_strButtons.leavePlatoon.caption()))
            model.header.btnLeavePlatoon.setDescription(backport.text(_strButtons.leavePlatoon.description()))
            model.header.btnLeavePlatoon.setIsEnabled(not isInQueue)
            model.btnInviteFriends.setCaption(backport.text(inviteLabels.caption()))
            model.btnInviteFriends.setDescription(backport.text(inviteLabels.description()))
            model.btnInviteFriends.setIsEnabled(self._hasFreeSlot() and isCommander and canSendInvite and not isInQueue and not isInSearch)
        self._updateFindPlayersButton()
        self._updateReadyButton()

    def _updateFindPlayersButton(self, *args):
        isInQueue = self._platoonCtrl.isInQueue()
        isCommander = self._isCommander()
        if not isCommander:
            return
        canStartAutoSearch = self._platoonCtrl.getPermissions().canStartAutoSearch()
        isInSearch = self._platoonCtrl.isInSearch()
        isEnabled = isCommander and not isInQueue and canStartAutoSearch and self._platoonCtrl.hasFreeSlot()
        isCooldown = self._platoonCtrl.isInCoolDown(REQUEST_TYPE.AUTO_SEARCH)
        hasSearchSupport = self._platoonCtrl.hasSearchSupport()
        with self.viewModel.transaction() as model:
            model.setShouldShowFindPlayersButton(hasSearchSupport)
            if hasSearchSupport:
                model.btnFindPlayers.setIsEnabled(isEnabled and self._platoonCtrl.canStartSearch() and not isCooldown)
                model.btnFindPlayers.setHasTooltip(self._platoonCtrl.hasFreeSlot())
                if isCommander:
                    if isInSearch:
                        cancelButton = _strButtons.cancelSearch
                        model.btnFindPlayers.setCaption(backport.text(cancelButton.caption()))
                        model.btnFindPlayers.setDescription(backport.text(cancelButton.description()))
                        model.btnFindPlayers.setSoundClickName(R.sounds.gui_platoon_2_cancel_search())
                        model.btnFindPlayers.setIsLight(False)
                    else:
                        findButton = _strButtons.findPlayers
                        model.btnFindPlayers.setCaption(backport.text(findButton.caption()))
                        model.btnFindPlayers.setDescription(backport.text(findButton.descriptionMembers()))
                        model.btnFindPlayers.setSoundClickName(R.sounds.gui_platoon_2_find_players())
                        model.btnFindPlayers.setIsLight(True)

    def _isCommander(self):
        playerInfo = self._platoonCtrl.getPlayerInfo()
        isCommander = False
        if playerInfo:
            isCommander = playerInfo.isCommander()
        return isCommander

    def _onInviteFriends(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY), ctx={'prbName': 'unit',
         'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)

    @adisp_process
    def _onSwitchReady(self):
        result = yield self._platoonCtrl.togglePlayerReadyAction()
        if result:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)

    def _hasFreeSlot(self):
        return self._platoonCtrl.hasFreeSlot()

    def _getWTRStatus(self):
        return self._lobbyContext.getServerSettings().isWTREnabled()

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.dyn(self.getPrebattleType())()))))
        return title

    def _updateReadyButton(self, *args):
        if not self._platoonCtrl.isInPlatoon():
            return
        isInQueue = self._platoonCtrl.isInQueue()
        isEnabled, onlyReadinessText, simpleState, toolTipData = self._getActionButtonStateInfo()
        with self.viewModel.transaction() as model:
            if not self._platoonCtrl.isInCoolDown(REQUEST_TYPE.SET_PLAYER_STATE):
                model.btnSwitchReady.setIsEnabled(isEnabled and not isInQueue)
            if self._platoonCtrl.getPlayerInfo().isReady:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.notReady.caption()))
            else:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.ready.caption()))
            model.btnSwitchReady.setDescription(toolTipData)
            model.setFooterMessage(simpleState)
            model.setIsFooterMessageGrey(isEnabled or onlyReadinessText or isInQueue)

    def _getActionButtonStateInfo(self):
        actionButtonStateVO = self.__getActionButtonStateVO()
        isEnabled = actionButtonStateVO['isEnabled']
        onlyReadinessText = actionButtonStateVO.isReadinessTooltip()
        simpleState = actionButtonStateVO.getSimpleState()
        toolTipData = i18n.makeString(actionButtonStateVO['toolTipData'] + '/body')
        return (isEnabled,
         onlyReadinessText,
         simpleState,
         toolTipData)

    def _onFindPlayers(self):
        platoonCtrl = self._platoonCtrl
        if platoonCtrl.isInSearch():
            platoonCtrl.cancelSearch()
        else:
            platoonCtrl.startSearch()
            platoonCtrl.requestPlayerQueueInfo()

    def _onToggleMuteAll(self):
        voipMgr = VOIP.getVOIPManager()
        isChannelEnabled = not self.viewModel.header.btnMuteAll.getIsSelected()
        voipMgr.enableCurrentChannel(not isChannelEnabled)
        self.__updateVoiceChatToggleState()

    def _onLeavePlatoon(self):
        self._platoonCtrl.leavePlatoon(parent=self)

    def __onServerSettingsChange(self, diff):
        if Configs.UNIT_ASSEMBLER_CONFIG.value in diff:
            self._updateButtons()
        if PremiumConfigs.PREM_SQUAD in diff or BonusCapsConst.CONFIG_NAME in diff:
            self._setBonusInformation(getPlatoonBonusState(True))

    def __onAvailableTiersForSearchChanged(self):
        self._updateButtons()

    def __onPlayerSpeaking(self, accountDBID, isSpeak):
        slotModelArray = self.viewModel.getSlots()
        for it in slotModelArray:
            if it.player.getAccID() == str(accountDBID):
                return it.player.voice.setIsSpeaking(isSpeak)

    def __getLayoutStyle(self):
        maxSlotCount = self._platoonCtrl.getMaxSlotCount()
        if maxSlotCount == 3:
            return _LayoutStyle.HORIZONTAL
        return _LayoutStyle.HORIZONTAL_SHORT if maxSlotCount < 3 else _LayoutStyle.VERTICAL

    def __updateVoiceChatToggleState(self, *_):
        voipMgr = VOIP.getVOIPManager()
        isMuteButtonVisible = voipMgr.isVoiceSupported() and voipMgr.isChannelAvailable()
        isVoiceChannelEnabled = voipMgr.isEnabled() and voipMgr.isCurrentChannelEnabled() and isMuteButtonVisible
        with self.viewModel.transaction() as model:
            model.header.btnMuteAll.setIsVisible(isMuteButtonVisible)
            model.header.btnMuteAll.setIsSelected(not isVoiceChannelEnabled)
            if isMuteButtonVisible:
                model.header.btnMuteAll.setIsSelected(not isVoiceChannelEnabled)
                if isVoiceChannelEnabled:
                    tooltipCaption = _strButtons.mute.caption()
                    tooltipBody = _strButtons.mute.description()
                else:
                    tooltipCaption = _strButtons.unMute.caption()
                    tooltipBody = _strButtons.unMute.description()
                model.header.btnMuteAll.setTooltipHeader(backport.text(tooltipCaption))
                model.header.btnMuteAll.setTooltipBody(backport.text(tooltipBody))

    def __onMinimized(self, *args, **kwargs):
        self._platoonCtrl.destroyUI(hideOnly=True)

    def __onFocusChange(self, *args, **kwargs):
        if args:
            self.__setPreBattleCarouselFocus(args[0]['isFocused'])

    def __setPreBattleCarouselFocus(self, isFocusIn):
        g_eventBus.handleEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.ON_WINDOW_CHANGE_FOCUS, self.__getClientID(), MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES.CHANNEL_CAROUSEL_ITEM_TYPE_PREBATTLE, isFocusIn), scope=EVENT_BUS_SCOPE.LOBBY)

    def __setPreBattleCarouselOpened(self, isWindowOpened):
        g_eventBus.handleEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.ON_WINDOW_CHANGE_OPEN_STATE, self.__getClientID(), MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES.CHANNEL_CAROUSEL_ITEM_TYPE_PREBATTLE, isWindowOpened), scope=EVENT_BUS_SCOPE.LOBBY)

    def __getClientID(self):
        return channel_num_gen.getClientID4Prebattle(self.getPrbEntityType())

    def __getActionButtonStateVO(self):
        return SquadActionButtonStateVO(self._platoonCtrl.getPrbEntity())

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)
            self.delayCallback(event.coolDown, self._updateReadyButton)

    def __onUserActionReceived(self, _, user, shadowMode):
        if self._platoonCtrl.getPrbEntity() is not None:
            self._updateMembers()
        return

    def __onUsersReceived(self, _):
        if self._platoonCtrl.getPrbEntity() is not None:
            self._updateMembers()
        return


class EventMembersView(SquadMembersView):
    _prebattleType = PrebattleTypes.EVENT

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.event.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.event.body())
        return (tooltipHeader, tooltipBody)

    def _setNoBonusInformation(self, model):
        infoText = R.strings.messenger.dialogs.squadChannel.headerMsg.eventFormationRestriction()
        model.noBonusPlaceholder.setText(infoText)
        model.noBonusPlaceholder.setIcon(R.images.gui.maps.icons.battleTypes.c_64x64.event())


class EpicMembersView(SquadMembersView):
    _prebattleType = PrebattleTypes.EPIC

    def _getWindowInfoTooltipHeaderAndBody(self):
        header = backport.text(R.strings.platoon.members.header.tooltip.epic.header())
        body = backport.text(R.strings.platoon.members.header.tooltip.epic.body())
        return (header, body)

    def _setNoBonusInformation(self, model):
        infoText = R.strings.messenger.dialogs.squadChannel.headerMsg.epicBattleFormationRestriction()
        model.noBonusPlaceholder.setText(infoText)
        model.noBonusPlaceholder.setIcon(R.images.gui.maps.icons.battleTypes.c_64x64.epicbattle())


class BattleRoyalMembersView(SquadMembersView):
    _prebattleType = PrebattleTypes.BATTLEROYAL

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getIsVehiclePremium(self, vehicle):
        return False

    def _getWindowInfoTooltipHeaderAndBody(self):
        pass

    def _getWTRStatus(self):
        return False

    @staticmethod
    def __sortCurrentUser(slot):
        accID = BigWorld.player().id
        player = slot['player'] or {}
        return accID != player.get('accID')

    def _getPlatoonSlotsData(self):
        slots = super(BattleRoyalMembersView, self)._getPlatoonSlotsData()
        slots.sort(key=self.__sortCurrentUser)
        return slots


class MapboxMembersView(SquadMembersView):
    _prebattleType = PrebattleTypes.MAPBOX

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _updateFindPlayersButton(self, *args):
        with self.viewModel.transaction() as model:
            model.setShouldShowFindPlayersButton(value=False)


class Comp7MembersView(SquadMembersView):
    _comp7Controller = dependency.descriptor(IComp7Controller)
    _prebattleType = PrebattleTypes.COMP7

    def __init__(self, prbType):
        super(Comp7MembersView, self).__init__(prbType)
        self.__unitMgr = prb_getters.getClientUnitMgr()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def createToolTipContent(self, event, contentID):
        return SquadBonusTooltipContent(battleType=SELECTOR_BATTLE_TYPES.COMP7, bonusState=getPlatoonBonusState(True)) if contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip() else super(Comp7MembersView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def _viewModelClass(self):
        return Comp7WindowModel

    @property
    def _slotModelClass(self):
        return Comp7SlotModel

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _setModeSlotSpecificData(self, slotData, slotModel):
        playerData = slotData.get('player', {})
        queueInfo = playerData.get('extraData', {}).get('comp7EnqueueData', {})
        rank = queueInfo.get('rank', 0)
        rating = queueInfo.get('rating', 0)
        isOnline = bool(queueInfo.get('isOnline', 0))
        division = self.__getDivision(rank, rating)
        if division is None:
            _logger.error("Failed to get player's division. dbID: %d; rank: %d; rating: %d", playerData.get('dbID'), rank, rating)
            return
        else:
            slotModel.rankData.setRank(comp7_shared.getRankEnumValue(division))
            slotModel.rankData.setDivision(comp7_shared.getDivisionEnumValue(division))
            slotModel.rankData.setScore(rating)
            slotModel.setErrorType(ErrorType.NONE if isOnline else ErrorType.MODEOFFLINE)
            return

    def _getWindowInfoTooltipHeaderAndBody(self):
        squadRatingSettings = self._comp7Controller.getModeSettings().squadRatingRestriction
        rating = squadRatingSettings.get(2)
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.comp7.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.comp7.body(), rating=rating)
        return (tooltipHeader, tooltipBody)

    def _initWindowModeSpecificData(self, model):
        options = self._comp7Controller.getModeSettings().squadSizes
        model.setSeasonName(getSeasonNameEnum())
        model.header.memberCountDropdown.setMultiple(False)
        items = model.header.memberCountDropdown.getItems()
        for option in options:
            item = Comp7DropdownItem()
            item.setId(str(option))
            item.setLabel(str(option))
            items.addViewModel(item)

    def _updateHeader(self):
        super(Comp7MembersView, self)._updateHeader()
        self.__updateDropDown()

    def _getPlatoonSlotsData(self):
        slots = super(Comp7MembersView, self)._getPlatoonSlotsData()
        slots.sort(key=self.__playerTimeJoin)
        return slots

    def _hasFreeSlot(self):
        return len(self.__unitMgr.unit.getPlayers()) < self.__unitMgr.unit.getSquadSize() if self.__unitMgr is not None and self.__unitMgr.unit is not None else False

    def _addListeners(self):
        super(Comp7MembersView, self)._addListeners()
        self.viewModel.header.memberCountDropdown.onChange += self.__onMemberCountDropdown

    def _removeListeners(self):
        super(Comp7MembersView, self)._removeListeners()
        self.viewModel.header.memberCountDropdown.onChange -= self.__onMemberCountDropdown

    @args2params(int)
    def __onMemberCountDropdown(self, selectedIds):
        if selectedIds:
            self.__unitMgr.setSquadSize(selectedIds)

    def __updateDropDown(self):
        with self.viewModel.transaction() as model:
            self.__updateMemberCountDropdown(model)
            items = model.header.memberCountDropdown.getItems()
            actualSquadSize = self.__unitMgr.unit.getSquadSize()
            selected = model.header.memberCountDropdown.getSelected()
            selected.clear()
            selected.addString(str(actualSquadSize))
            selected.invalidate()
            playersCount = len(self.__unitMgr.unit.getPlayers())
            for item in items:
                self.__updateDropdownItem(item, playersCount)

    def __updateMemberCountDropdown(self, model):
        if not self._isCommander():
            model.header.memberCountDropdown.setIsDisabled(True)
            model.header.memberCountDropdown.setTooltipText(self.__getDropDownTooltipText())
        else:
            model.header.memberCountDropdown.setIsDisabled(False)
            model.header.memberCountDropdown.setTooltipText('')

    def __updateDropdownItem(self, item, playersCount):
        itemNumber = int(item.getLabel())
        if itemNumber < playersCount:
            item.setIsDisabled(True)
            item.meta.setTooltipText(self.__getDropDownItemTooltipText())
        else:
            item.setIsDisabled(False)
            item.meta.setTooltipText('')

    def __getDropDownTooltipText(self):
        return backport.text(R.strings.platoon.members.header.tooltip.comp7.dropdown())

    def __getDropDownItemTooltipText(self):
        return backport.text(R.strings.platoon.members.header.tooltip.comp7.dropdown.item())

    @classmethod
    def __getDivision(cls, rank, rating):
        ranksConfig = cls._lobbyContext.getServerSettings().comp7RanksConfig
        division = findFirst(lambda d: rating in d.range, ranksConfig.divisionsByRank.get(rank, ()))
        return division

    @staticmethod
    def __playerTimeJoin(slot):
        player = slot['player'] or {}
        roleIndex = -slot['role'] if not player.get('isOffline') else 0
        return (not player, roleIndex, player.get('timeJoin', 0))


class MembersWindow(PreloadableWindow):
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, initialPosition=None):
        prbType = self.__platoonCtrl.getPrbEntityType()
        from gui.impl.lobby.platoon.platoon_config import PLATOON_VIEW_BY_PRB_TYPE
        viewClass = PLATOON_VIEW_BY_PRB_TYPE.get(prbType)
        if viewClass:
            content = viewClass(prbType)
        else:
            content = None
            _logger.debug('PrbType is unknown %d', prbType)
        super(MembersWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=content)
        if initialPosition:
            self.move(initialPosition.x, initialPosition.y)
        return
